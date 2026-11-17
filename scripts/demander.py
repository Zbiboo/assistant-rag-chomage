"""Étape 3 du RAG : poser une question et obtenir une réponse sourcée.

Usage :
    .venv/bin/python scripts/demander.py "J'ai 56 ans, combien de temps serai-je indemnisé ?"
    .venv/bin/python scripts/demander.py            # mode interactif (plusieurs questions)

Déroulé pour chaque question :
  1. REFORMULER : Claude traduit la question en vocabulaire officiel
     (« combien de temps » -> « durée de versement ») pour aider la recherche.
  2. CHERCHER   : BM25 retrouve les morceaux les plus pertinents (étape 2).
  3. RÉPONDRE   : Claude reçoit ces morceaux et doit répondre UNIQUEMENT à
     partir d'eux, en citant ses sources [1], [2]…

Le fichier est en deux parties :
- le MOTEUR (classe Assistant) : renvoie un résultat sans rien afficher ;
  il est réutilisé par l'évaluation et par la page web ;
- l'AFFICHAGE en ligne de commande (fonctions afficher et main).
"""

import sys

import anthropic

import config
from rechercher import charger_index

# --- Les consignes (« prompts ») ---------------------------------------------

CONSIGNE_REFORMULATION = """\
Tu aides un moteur de recherche par mots-clés à fouiller des fiches de \
service-public.gouv.fr sur le chômage et France Travail.

Réécris la question de l'utilisateur sous forme d'une liste de mots-clés, en \
utilisant le vocabulaire officiel de ces fiches. Exemples de correspondances :
- « combien de temps je serai payé » -> durée de versement de l'ARE, durée d'indemnisation
- « combien je vais toucher » -> montant de l'ARE, salaire journalier de référence
- « je quitte mon job » -> démission
- « fonctionnaire » -> agent public, fonctionnaire, contractuel
- « oublier de s'actualiser » -> actualisation mensuelle, radiation, sanction

Garde les éléments de situation utiles (âge, date de fin de contrat, statut).
Réponds uniquement par les mots-clés sur une ligne, sans phrase ni explication."""

CONSIGNE_REPONSE = """\
Tu es un assistant qui informe sur l'assurance chômage et France Travail.

Tu reçois des extraits numérotés de fiches officielles de service-public.gouv.fr. \
Règles impératives :
1. Réponds UNIQUEMENT à partir de ces extraits. N'utilise jamais tes propres \
connaissances, même si tu penses les connaître : les règles changent souvent.
2. Après chaque information, cite le ou les extraits qui la justifient, sous \
la forme [1], [2]…
3. Si les extraits ne permettent pas de répondre, ou seulement en partie, dis-le \
clairement et conseille de vérifier auprès de France Travail. Ne devine pas.
4. Les règles dépendent souvent de la situation (âge, date de fin de contrat, \
secteur privé ou agent public…). Si la question ne précise pas un élément qui \
change la réponse, donne les différents cas présents dans les extraits, ou \
signale l'information qui manque.
5. Réponds en français, simplement et brièvement, pour une personne qui n'est \
pas juriste.
6. Ne termine pas par une liste des sources : elle est affichée automatiquement \
sous ta réponse. Les citations [1], [2]… dans le texte suffisent."""


class QuestionTropLongue(ValueError):
    pass


# --- Le moteur ---------------------------------------------------------------

class Assistant:
    def __init__(self):
        self.client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement
        self.index = charger_index()

    def appeler(self, modele, consigne, message, effort, max_tokens):
        """Un appel à Claude. Renvoie un dict : texte, modèle, tokens, coût."""
        parametres = dict(
            model=modele,
            max_tokens=max_tokens,
            system=consigne,
            messages=[{"role": "user", "content": message}],
            output_config={"effort": effort},
        )
        if modele in config.MODELES_AVEC_REPLI:
            # Repli automatique sur un autre modèle en cas de refus (voir config.py).
            reponse = self.client.beta.messages.create(
                **parametres, betas=["server-side-fallback-2026-07-01"], fallbacks="default"
            )
        else:
            reponse = self.client.messages.create(**parametres)

        if reponse.stop_reason == "refusal":
            texte = "(Le modèle a refusé de répondre à cette question.)"
        else:
            texte = "".join(b.text for b in reponse.content if b.type == "text").strip()
            if reponse.stop_reason == "max_tokens":
                texte += "\n\n(Réponse coupée : limite de longueur atteinte.)"
        entree, sortie = reponse.usage.input_tokens, reponse.usage.output_tokens
        return {
            "texte": texte,
            "modele": modele,
            "tokens_entree": entree,
            "tokens_sortie": sortie,  # inclut les tokens de réflexion du modèle
            "cout": config.cout_en_dollars(modele, entree, sortie),
        }

    # Les 3 étapes, utilisables séparément (l'évaluation s'en sert) :

    def reformuler(self, question):
        return self.appeler(
            config.MODELE_REFORMULATION, CONSIGNE_REFORMULATION, question,
            config.EFFORT_REFORMULATION, config.MAX_TOKENS_REFORMULATION,
        )

    def chercher(self, question, mots_cles=""):
        """Les morceaux les plus pertinents pour la question (+ mots-clés éventuels)."""
        resultats = self.index.chercher(f"{question} {mots_cles}", n=config.NB_EXTRAITS)
        return [m for _, m in resultats]

    def generer(self, question, extraits, modele=None):
        message = (
            f"Extraits des fiches officielles :\n\n{formater_extraits(extraits)}\n\n"
            f"Question : {question}"
        )
        return self.appeler(
            modele or config.MODELE_REPONSE, CONSIGNE_REPONSE, message,
            config.EFFORT_REPONSE, config.MAX_TOKENS_REPONSE,
        )

    def repondre(self, question):
        """Pose une question. Renvoie un dict avec la réponse, les extraits et les coûts."""
        question = question.strip()
        if len(question) > config.LONGUEUR_MAX_QUESTION:
            raise QuestionTropLongue(
                f"La question fait {len(question)} caractères "
                f"(maximum : {config.LONGUEUR_MAX_QUESTION})."
            )

        reformulation = self.reformuler(question)                  # 1. Reformuler
        extraits = self.chercher(question, reformulation["texte"])  # 2. Chercher
        appels = [reformulation]
        if extraits:                                                 # 3. Répondre
            generation = self.generer(question, extraits)
            appels.append(generation)
            texte = generation["texte"]
        else:
            texte = "Je n'ai trouvé aucun passage sur ce sujet dans les fiches officielles."

        couts = [a["cout"] for a in appels]
        return {
            "question": question,
            "mots_cles": reformulation["texte"],
            "reponse": texte,
            "extraits": extraits,
            "appels": appels,
            "cout_total": None if None in couts else sum(couts),
        }


def section_de(morceau):
    return " > ".join(morceau["fil"]) or "(introduction)"


def formater_extraits(extraits):
    """Présente les morceaux trouvés à Claude, chacun avec son numéro.

    Si le même texte figure dans plusieurs sections (plusieurs âges, privé et
    public…), on les liste toutes : le modèle sait ainsi à qui la règle s'applique.
    """
    blocs = []
    for n, m in enumerate(extraits, 1):
        entete = f"Page : {m['titre_page']}\nSection : {section_de(m)}"
        autres = m.get("autres_sections", [])
        if autres:
            entete += "\nCe même texte figure aussi dans :" + "".join(
                f"\n- {a['titre_page']} > {section_de(a)}" for a in autres)
        blocs.append(f'<extrait numero="{n}">\n{entete}\n\n{m["texte"]}\n</extrait>')
    return "\n\n".join(blocs)


# --- L'affichage en ligne de commande -------------------------------------------

def afficher(resultat):
    print(f"\n🔎 Recherche : {resultat['mots_cles']}")
    print(f"\n💬 Réponse :\n\n{resultat['reponse']}\n")
    print("📚 Sources :")
    for n, m in enumerate(resultat["extraits"], 1):
        print(f"  [{n}] {m['titre_page']}")
        print(f"      Section : {section_de(m)}")
        if m.get("autres_sections"):
            print(f"      (texte identique dans {len(m['autres_sections'])} autre(s) section(s))")
        print(f"      {m['source']} (vérifié le {m['verifie_le']})")

    print("\n💶 Consommation :")
    for etape, a in zip(("reformulation", "réponse"), resultat["appels"]):
        cout = f"{a['cout']:.5f} $" if a["cout"] is not None else "prix inconnu"
        print(f"  {etape:<14} {a['modele']:<18} {a['tokens_entree']:>5} tokens entrée, "
              f"{a['tokens_sortie']:>5} sortie  ≈ {cout}")
    if resultat["cout_total"] is not None:
        total = resultat["cout_total"]
        print(f"  {'total':<14} {'':<18} ≈ {total:.5f} $ (≈ {1 / total:.0f} questions pour 1 $)\n")


def main():
    assistant = Assistant()
    question = " ".join(sys.argv[1:])
    questions = [question] if question else None
    if not questions:
        print("Posez votre question (ou appuyez sur Entrée pour quitter).")
    while True:
        q = questions.pop() if questions else (None if question else input("\n❓ ").strip())
        if not q:
            break
        try:
            afficher(assistant.repondre(q))
        except QuestionTropLongue as e:
            print(f"⚠️  {e} Merci de la raccourcir.")


if __name__ == "__main__":
    try:
        main()
    except anthropic.AuthenticationError:
        sys.exit("Clé API refusée : vérifiez le fichier .env")
    except anthropic.APIConnectionError:
        sys.exit("Impossible de joindre l'API : vérifiez la connexion internet.")
    except anthropic.APIStatusError as e:
        sys.exit(f"Erreur de l'API ({e.status_code}) : {e.message}")
