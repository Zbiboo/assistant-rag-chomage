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
"""

import sys

import anthropic

from config import charger_env
from rechercher import charger_index

MODELE = "claude-opus-5-5"
NB_EXTRAITS = 5
# Prix de claude-opus-5-5 en dollars par million de tokens (entrée / sortie).
PRIX_ENTREE = 4.00 / 1_000_000
PRIX_SORTIE = 20.00 / 1_000_000

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
pas juriste."""


def texte_de(reponse):
    """Rassemble les blocs de texte d'une réponse de l'API."""
    return "".join(b.text for b in reponse.content if b.type == "text").strip()


def appeler(client, consigne, message, effort):
    """Un appel à Claude. Renvoie (texte, usage).

    `fallbacks="default"` : si le modèle refusait de répondre (filtre de
    sécurité), l'API relancerait automatiquement la demande sur un autre modèle.
    """
    reponse = client.beta.messages.create(
        model=MODELE,
        max_tokens=16000,
        system=consigne,
        messages=[{"role": "user", "content": message}],
        output_config={"effort": effort},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if reponse.stop_reason == "refusal":
        return "(Le modèle a refusé de répondre à cette question.)", reponse.usage
    return texte_de(reponse), reponse.usage


def formater_extraits(resultats):
    """Présente les morceaux trouvés à Claude, chacun avec son numéro."""
    blocs = []
    for n, (_, m) in enumerate(resultats, 1):
        section = " > ".join(m["fil"]) or "(introduction)"
        blocs.append(
            f'<extrait numero="{n}">\n'
            f"Page : {m['titre_page']}\n"
            f"Section : {section}\n\n"
            f"{m['texte']}\n"
            f"</extrait>"
        )
    return "\n\n".join(blocs)


def repondre(client, index, question):
    # 1. Reformuler
    mots_cles, usage1 = appeler(client, CONSIGNE_REFORMULATION, question, effort="low")
    print(f"\n🔎 Recherche : {mots_cles}")

    # 2. Chercher (sur la question d'origine + les mots-clés officiels)
    resultats = index.chercher(question + " " + mots_cles, n=NB_EXTRAITS)
    if not resultats:
        print("Aucun passage trouvé dans les documents.")
        return

    # 3. Répondre
    message = (
        f"Extraits des fiches officielles :\n\n{formater_extraits(resultats)}\n\n"
        f"Question : {question}"
    )
    reponse, usage2 = appeler(client, CONSIGNE_REPONSE, message, effort="medium")

    print(f"\n💬 Réponse :\n\n{reponse}\n")
    print("📚 Sources :")
    for n, (_, m) in enumerate(resultats, 1):
        section = " > ".join(m["fil"]) or "(introduction)"
        print(f"  [{n}] {m['titre_page']}")
        print(f"      Section : {section}")
        print(f"      {m['source']} (vérifié le {m['verifie_le']})")

    entree = usage1.input_tokens + usage2.input_tokens
    sortie = usage1.output_tokens + usage2.output_tokens
    cout = entree * PRIX_ENTREE + sortie * PRIX_SORTIE
    print(f"\n💶 Coût : {entree} tokens en entrée, {sortie} en sortie ≈ {cout:.4f} $\n")


def main():
    charger_env()
    client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement
    index = charger_index()

    question = " ".join(sys.argv[1:])
    if question:
        repondre(client, index, question)
        return
    print("Posez votre question (ou appuyez sur Entrée pour quitter).")
    while question := input("\n❓ ").strip():
        repondre(client, index, question)


if __name__ == "__main__":
    try:
        main()
    except anthropic.AuthenticationError:
        sys.exit("Clé API refusée : vérifiez le fichier .env")
    except anthropic.APIConnectionError:
        sys.exit("Impossible de joindre l'API : vérifiez la connexion internet.")
    except anthropic.APIStatusError as e:
        sys.exit(f"Erreur de l'API ({e.status_code}) : {e.message}")
