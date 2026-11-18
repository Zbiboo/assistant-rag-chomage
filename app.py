"""Interface web de l'assistant (Gradio), prévue pour Hugging Face Spaces.

Lancer en local :
    .venv/bin/python app.py        puis ouvrir http://127.0.0.1:7860

Ce fichier ne contient QUE l'interface : la recherche et la génération viennent
de la classe Assistant (scripts/demander.py), la même que pour la ligne de
commande et l'évaluation.

Protections :
- longueur maximale de question (vérifiée avant tout appel payant) ;
- plafond GLOBAL de questions par jour, tous visiteurs confondus ;
- erreurs de l'API transformées en message poli, sans détail technique ;
- la clé API reste côté serveur (variable d'environnement), jamais envoyée
  au navigateur.
"""

import datetime
import sys
import threading
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic
import gradio as gr

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE / "scripts"))

import config  # noqa: E402  (charge aussi .env en local)
import decouper  # noqa: E402
from demander import Assistant, QuestionTropLongue, section_de  # noqa: E402

# data/ n'est pas versionné : on recrée les morceaux au démarrage si besoin
# (c'est le cas sur Hugging Face, qui part du dépôt Git).
if not (RACINE / "data" / "morceaux.jsonl").exists():
    decouper.main()

assistant = Assistant()
FUSEAU = ZoneInfo("Europe/Paris")


# --- Plafond global de questions par jour --------------------------------------

class CompteurJournalier:
    """Compte les questions du jour pour TOUS les visiteurs.

    Le compteur est en mémoire : il repart de zéro à minuit (heure de Paris) et
    à chaque redémarrage du serveur. Le verrou (Lock) évite que deux visiteurs
    simultanés ne faussent le compte.
    """

    def __init__(self, maximum):
        self.maximum = maximum
        self.jour = None
        self.nombre = 0
        self.verrou = threading.Lock()

    def reserver(self):
        """Réserve une place pour une question. False si le plafond est atteint."""
        with self.verrou:
            aujourd_hui = datetime.datetime.now(FUSEAU).date()
            if aujourd_hui != self.jour:
                self.jour, self.nombre = aujourd_hui, 0
            if self.nombre >= self.maximum:
                return False
            self.nombre += 1
            return True

    def annuler(self):
        """Rend la place si la question n'a finalement pas été traitée (erreur)."""
        with self.verrou:
            self.nombre = max(0, self.nombre - 1)


compteur = CompteurJournalier(config.QUESTIONS_MAX_PAR_JOUR)


# --- Mise en forme ------------------------------------------------------------

def date_fr(iso):
    """« 2026-11-17 » -> « 17/11/2026 »."""
    return datetime.date.fromisoformat(iso).strftime("%d/%m/%Y") if iso else "?"


DATES_CONSULTATION = sorted({m["date_consultation"] for m in assistant.index.morceaux if m["date_consultation"]})
CONSULTATION = " et ".join(date_fr(d) for d in DATES_CONSULTATION) or "?"


def formater_sources(extraits):
    lignes = ["### Sources"]
    for n, m in enumerate(extraits, 1):
        ligne = (f"**[{n}]** [{m['titre_page']}]({m['source']})  \n"
                 f"{section_de(m)}  \n"
                 f"<small>Fiche vérifiée le {m['verifie_le']} par service-public, "
                 f"consultée le {date_fr(m['date_consultation'])}")
        if m.get("autres_sections"):
            ligne += f" · texte identique dans {len(m['autres_sections'])} autre(s) section(s)"
        lignes.append(ligne + "</small>")
    return "\n\n".join(lignes)


def formater_details(resultat, secondes):
    texte = (
        f"1. **Reformulation** de la question en vocabulaire officiel : *{resultat['mots_cles']}*\n"
        f"2. **Recherche** BM25 sur la question + la reformulation : "
        f"{len(resultat['extraits'])} extraits retenus (doublons fusionnés)\n"
        f"3. **Réponse** de {config.MODELE_REPONSE}, uniquement à partir de ces extraits\n\n"
        f"Durée : {secondes:.1f} s"
    )
    if resultat["cout_total"] is not None:
        texte += f" · coût estimé : {resultat['cout_total']:.4f} $"
    return texte


# --- La fonction appelée par le bouton ------------------------------------------

# Texte affiché dans la zone de réponse pendant chaque étape annoncée par le moteur.
ETAPES = {
    "reformulation": "⏳ **Étape 1 sur 3** · Je reformule votre question avec le vocabulaire des fiches officielles…",
    "recherche": "⏳ **Étape 2 sur 3** · Je cherche les passages utiles dans les 14 fiches…",
    "redaction": "⏳ **Étape 3 sur 3** · Je rédige la réponse en citant les sources (5 à 10 secondes)…",
}


def repondre(question):
    """Produit (réponse, sources, détails) : trois blocs Markdown.

    C'est un GÉNÉRATEUR : chaque `yield` met à jour la page immédiatement.
    Pendant l'attente, la zone de réponse affiche donc l'étape en cours, puis
    elle est remplacée par la réponse finale.
    """
    question = (question or "").strip()
    if not question:
        yield "Écrivez une question, ou cliquez sur un exemple.", "", ""
        return
    if len(question) > config.LONGUEUR_MAX_QUESTION:
        yield (f"Votre question fait {len(question)} caractères : merci de la raccourcir "
               f"(maximum {config.LONGUEUR_MAX_QUESTION}).", "", "")
        return
    if not compteur.reserver():
        yield ("**Le nombre maximal de questions pour aujourd'hui est atteint** "
               f"({config.QUESTIONS_MAX_PAR_JOUR} questions par jour, pour tous les visiteurs). "
               "Ce plafond protège le budget de cette démonstration. Revenez demain !", "", "")
        return

    debut = time.time()
    try:
        for etape, resultat in assistant.repondre_par_etapes(question):
            if etape != "fini":
                yield ETAPES[etape], "", ""   # affiche l'étape en cours
    except QuestionTropLongue as e:
        compteur.annuler()
        yield str(e), "", ""
        return
    except anthropic.RateLimitError:
        compteur.annuler()
        print("Erreur API : limite de débit (429)")  # journal serveur, sans détail sensible
        yield "Le service est très sollicité en ce moment. Réessayez dans une minute.", "", ""
        return
    except anthropic.APIError as e:
        compteur.annuler()
        print(f"Erreur API : {type(e).__name__} {getattr(e, 'status_code', '')}")
        yield ("Désolé, le service de réponse est momentanément indisponible. "
               "Réessayez un peu plus tard.", "", "")
        return

    yield (resultat["reponse"],
           formater_sources(resultat["extraits"]),
           formater_details(resultat, time.time() - debut))


# --- La page ------------------------------------------------------------------

EXEMPLES = [
    "Mon patron veut que je parte mais je ne veux pas démissionner, il y a une autre solution ?",
    "J'ai 57 ans, mon CDD se termine le 15 décembre, pendant combien de temps vais-je être indemnisé ?",
    "Puis-je toucher le chômage si je démissionne pour me reconvertir ?",
    "Qu'est-ce que je risque si je ne vais pas à un rendez-vous France Travail ?",
]

AVERTISSEMENT = (
    f"⚠️ **Informations générales issues des fiches officielles service-public "
    f"(consultées le {CONSULTATION}). Ne remplace pas un conseiller France Travail.**"
)

with gr.Blocks(title="Assistant chômage : réponses sourcées") as demo:
    gr.Markdown(
        "# Assistant chômage et France Travail\n"
        "Posez une question sur l'allocation chômage, l'inscription, la démission, la rupture "
        "conventionnelle… L'assistant répond **uniquement** à partir de 14 fiches officielles de "
        "service-public.gouv.fr et **cite ses sources** [1], [2]… Il dit « je ne sais pas » quand "
        "l'information n'y est pas."
    )
    gr.Markdown(AVERTISSEMENT)
    question = gr.Textbox(
        label="Votre question",
        placeholder="Ex. : j'ai été licencié, combien de temps vais-je toucher le chômage ?",
        lines=2,
        max_length=config.LONGUEUR_MAX_QUESTION,
        info=f"{config.LONGUEUR_MAX_QUESTION} caractères maximum.",
    )
    bouton = gr.Button("Poser la question", variant="primary")
    gr.Markdown("<small>⏳ Une réponse prend environ 10 secondes : restez sur cette page "
                "pendant la recherche, sinon elle est perdue.</small>")
    gr.Examples(examples=EXEMPLES, inputs=question, label="Exemples (cliquez pour remplir)")
    reponse = gr.Markdown()
    sources = gr.Markdown()
    with gr.Accordion("Comment cette réponse a été trouvée", open=False):
        details = gr.Markdown()
    gr.Markdown(
        "---\n"
        f"Projet de démonstration · [Code source sur GitHub]({config.URL_GITHUB}) · "
        "Données : fiches service-public.gouv.fr, Licence Ouverte Etalab 2.0 · "
        f"Modèle : {config.MODELE_REPONSE} (Anthropic)"
    )

    bouton.click(repondre, inputs=question, outputs=[reponse, sources, details])
    question.submit(repondre, inputs=question, outputs=[reponse, sources, details])


if __name__ == "__main__":
    demo.launch()
