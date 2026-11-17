"""Étape 2 du RAG : retrouver les morceaux les plus pertinents pour une question.

Usage :
    python3 scripts/rechercher.py "J'ai 56 ans, combien de temps serai-je indemnisé ?"

Méthode : BM25, l'algorithme classique des moteurs de recherche par mots-clés.
Pour chaque mot de la question, un morceau gagne des points :
- s'il contient ce mot (et un peu plus s'il le contient plusieurs fois,
  mais avec un plafond : 10 fois le mot ne vaut pas 10 fois plus) ;
- d'autant plus que le mot est RARE dans l'ensemble des morceaux
  (« démission » est plus parlant que « allocation », présent partout) ;
- un peu moins si le morceau est long (un long texte contient « par hasard »
  plus de mots).
"""

import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FICHIER_MORCEAUX = RACINE / "data" / "morceaux.jsonl"

# Mots trop courants pour aider à distinguer les morceaux (« mots vides »).
MOTS_VIDES = set("""
a au aux avec ce ces cet cette comment dans de des du elle en est et etre
il ils je la le les leur lui ma mais me mes moi mon ne nos notre nous on ou
par pas pour qu que qui quoi quel quelle quels quelles sa se ses si son sur
ta te tes toi ton tu un une vos votre vous y d l j m n s t c qu ai as avez
suis sont peut peux puis faut dois doit est-ce
""".split())

# Réglages standards de BM25.
K1 = 1.5  # plafond de l'effet « mot répété »
B = 0.75  # force de la pénalité « texte long »
LETTRES_GARDEES = 6  # troncature des mots (voir la fonction mots)


def mots(texte):
    """Transforme un texte en liste de mots normalisés.

    « Démissionné, l'ARE » -> ["demissionne", "are"]
    On met en minuscules, on retire les accents (pour que « indemnisé » et
    « indemnise » se rejoignent), on coupe sur tout ce qui n'est pas une
    lettre ou un chiffre, et on enlève les mots vides.

    Enfin on ne garde que les 6 premières lettres de chaque mot (« troncature ») :
    « démissionne », « démission » et « démissionner » deviennent tous « demiss ».
    C'est une version très simple de la « racinisation » (stemming).
    """
    texte = unicodedata.normalize("NFD", texte.lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return [m[:LETTRES_GARDEES] for m in re.findall(r"[a-z0-9]+", texte) if m not in MOTS_VIDES]


def texte_indexe(morceau):
    """Ce sur quoi on cherche : le fil de titres + le texte du morceau."""
    return " ".join(morceau["fil"]) + " " + morceau["texte"]


class IndexBM25:
    def __init__(self, morceaux):
        self.morceaux = morceaux
        self.comptes = [Counter(mots(texte_indexe(m))) for m in morceaux]
        self.longueurs = [sum(c.values()) for c in self.comptes]
        self.longueur_moyenne = sum(self.longueurs) / len(self.longueurs)
        # Dans combien de morceaux apparaît chaque mot ?
        presence = Counter()
        for c in self.comptes:
            presence.update(c.keys())
        n = len(morceaux)
        # IDF = « rareté » d'un mot : grand si le mot est dans peu de morceaux.
        self.idf = {mot: math.log(1 + (n - df + 0.5) / (df + 0.5)) for mot, df in presence.items()}

    def score(self, i, mots_question):
        total = 0.0
        for mot in mots_question:
            f = self.comptes[i].get(mot, 0)
            if f == 0:
                continue
            normalisation = 1 - B + B * self.longueurs[i] / self.longueur_moyenne
            total += self.idf[mot] * f * (K1 + 1) / (f + K1 * normalisation)
        return total

    def chercher(self, question, n=5):
        q = mots(question)
        scores = [(self.score(i, q), i) for i in range(len(self.morceaux))]
        scores.sort(reverse=True)
        return [(s, self.morceaux[i]) for s, i in scores[:n] if s > 0]


def charger_index():
    with FICHIER_MORCEAUX.open(encoding="utf-8") as f:
        return IndexBM25([json.loads(ligne) for ligne in f])


def main():
    question = " ".join(sys.argv[1:])
    if not question:
        sys.exit('Usage : python3 scripts/rechercher.py "votre question"')
    index = charger_index()
    print(f"Mots cherchés : {mots(question)}\n")
    for rang, (score, m) in enumerate(index.chercher(question), 1):
        print(f"{rang}. [score {score:.1f}] {m['id']}")
        print(f"   {' > '.join(m['fil']) or m['titre_page']}")
        print(f"   {m['texte'][:160].replace(chr(10), ' ')}…\n")


if __name__ == "__main__":
    main()
