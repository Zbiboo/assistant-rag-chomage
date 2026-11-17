"""Chargement de la configuration secrète (clé API) depuis le fichier .env.

Le fichier .env (à la racine du projet, jamais publié) contient des lignes
NOM=valeur. On les place dans les « variables d'environnement » du programme :
le paquet anthropic y lit automatiquement ANTHROPIC_API_KEY, donc la clé
n'apparaît jamais dans le code.
"""

import os
from pathlib import Path

FICHIER_ENV = Path(__file__).resolve().parent.parent / ".env"


def charger_env():
    if not FICHIER_ENV.exists():
        return
    for ligne in FICHIER_ENV.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        nom, valeur = ligne.split("=", 1)
        # Une variable déjà définie dans le terminal reste prioritaire.
        os.environ.setdefault(nom.strip(), valeur.strip())
