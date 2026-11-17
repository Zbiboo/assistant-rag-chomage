"""Configuration du projet : clé API (secrète) et réglages des modèles.

1. La clé API est lue dans le fichier .env (jamais publié) et placée dans les
   « variables d'environnement » : le paquet anthropic l'y lit tout seul, donc
   elle n'apparaît jamais dans le code.
2. Les réglages des modèles sont regroupés ici. Chacun peut être remplacé sans
   toucher au code, par une variable d'environnement du même nom, par exemple :
       MODELE_REPONSE=claude-sonnet-5-5 .venv/bin/python scripts/demander.py "…"
"""

import os
from pathlib import Path

FICHIER_ENV = Path(__file__).resolve().parent.parent / ".env"


def charger_env():
    if not FICHIER_ENV.exists():
        return  # en ligne (Hugging Face), la clé vient directement de l'environnement
    for ligne in FICHIER_ENV.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        nom, valeur = ligne.split("=", 1)
        # Une variable déjà définie dans le terminal reste prioritaire.
        os.environ.setdefault(nom.strip(), valeur.strip())


charger_env()


def _reglage(nom, defaut, type_=str):
    """Valeur de la variable d'environnement `nom` si elle existe, sinon `defaut`."""
    return type_(os.environ.get(nom, defaut))


# --- Modèles -----------------------------------------------------------------
# Identifiants vérifiés le 2026-11-17 dans la documentation officielle
# (platform.claude.com/docs/en/about-claude/models/overview) et via l'API.
MODELE_REFORMULATION = _reglage("MODELE_REFORMULATION", "claude-haiku-5-5")
MODELE_REPONSE = _reglage("MODELE_REPONSE", "claude-haiku-5-5")

# « Effort » = combien le modèle réfléchit avant de répondre (low, medium, high…).
EFFORT_REFORMULATION = _reglage("EFFORT_REFORMULATION", "low")
EFFORT_REPONSE = _reglage("EFFORT_REPONSE", "medium")

# --- Limites (coût et abus) ---------------------------------------------------
# max_tokens plafonne la longueur de ce que le modèle produit (réflexion comprise).
MAX_TOKENS_REFORMULATION = _reglage("MAX_TOKENS_REFORMULATION", 1000, int)
MAX_TOKENS_REPONSE = _reglage("MAX_TOKENS_REPONSE", 2500, int)
LONGUEUR_MAX_QUESTION = _reglage("LONGUEUR_MAX_QUESTION", 500, int)  # caractères
NB_EXTRAITS = _reglage("NB_EXTRAITS", 5, int)

# --- Prix en dollars par million de tokens : (entrée, sortie) -----------------
# Source : platform.claude.com/docs/en/about-claude/pricing (vérifié le 2026-11-17).
# Haiku 5.5 : tarif valable jusqu'à 100 000 tokens par requête (nos requêtes en
# font environ 4 000) ; au-delà il passe à 0,50 / 2,50.
PRIX = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}

# Modèles pour lesquels on active le « repli » automatique : si le modèle refuse
# de répondre (filtre de sécurité), l'API relance la demande sur un autre modèle.
# Haiku 5.5 ne le propose pas.
MODELES_AVEC_REPLI = {"claude-opus-5-5", "claude-sonnet-5-5"}


def cout_en_dollars(modele, tokens_entree, tokens_sortie):
    """Coût estimé d'un appel. None si le prix du modèle n'est pas connu."""
    if modele not in PRIX:
        return None
    prix_entree, prix_sortie = PRIX[modele]
    return (tokens_entree * prix_entree + tokens_sortie * prix_sortie) / 1_000_000
