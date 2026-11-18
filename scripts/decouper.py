"""Étape 1 du RAG : découper les documents Markdown en morceaux (« chunks »).

Usage :
    python3 scripts/decouper.py

Lit documents/*.md et écrit data/morceaux.jsonl (un morceau JSON par ligne).

Principe :
- on coupe à chaque titre Markdown (#, ##, ###…) : un morceau = le texte
  d'une section, sans ses sous-sections ;
- chaque morceau garde son « fil » de titres (ex. « Vous avez 55 ou 56 ans >
  Quel est le montant de l'ARE ? > Montant brut ») : sans lui, un passage
  comme « Le montant est de 57 % » ne dit pas à qui il s'applique ;
- une section trop longue est coupée entre deux paragraphes ;
- on garde la source (titre, URL, date) pour pouvoir la citer.
"""

import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DOCUMENTS = RACINE / "documents"
FICHIER_SORTIE = RACINE / "data" / "morceaux.jsonl"

MOTS_MAX = 300  # au-delà, on coupe la section en plusieurs morceaux


def lire_document(chemin):
    """Sépare l'en-tête (front matter) du texte et renvoie (métadonnées, texte)."""
    contenu = chemin.read_text(encoding="utf-8")
    _, entete, texte = contenu.split("---\n", 2)
    meta = {}
    for ligne in entete.strip().split("\n"):
        cle, valeur = ligne.split(": ", 1)
        meta[cle] = valeur
    return meta, texte


def est_une_etiquette(paragraphe):
    """Vrai si le paragraphe annonce le bloc suivant et n'a pas de sens seul :
    un label en gras (« **À savoir** ») ou un titre de tableau (« Tableau - … »).
    Sans cette règle, la coupure à 300 mots pourrait séparer un tableau de son
    titre, et le modèle ne saurait plus à quoi le tableau s'applique."""
    return bool(re.fullmatch(r"\*\*[^*]+\*\*", paragraphe)) or (
        paragraphe.startswith("Tableau - ") and "\n" not in paragraphe
    )


def sections(texte):
    """Parcourt le texte et renvoie une liste de (fil_de_titres, paragraphes)."""
    fil = []  # pile de (niveau, titre)
    paragraphes = []
    resultat = []

    def ranger():
        if paragraphes:
            resultat.append(([t for _, t in fil], list(paragraphes)))
            paragraphes.clear()

    # Un « paragraphe » = un bloc séparé par une ligne vide (texte, liste, tableau).
    for bloc in re.split(r"\n\s*\n", texte):
        bloc = bloc.strip()
        if not bloc:
            continue
        titre = re.match(r"^(#+) (.*)$", bloc)
        if titre:
            ranger()
            niveau = len(titre.group(1))
            while fil and fil[-1][0] >= niveau:
                fil.pop()
            fil.append((niveau, titre.group(2)))
        elif paragraphes and est_une_etiquette(paragraphes[-1]):
            # Une étiquette reste collée au texte qui suit (voir est_une_etiquette).
            paragraphes[-1] += "\n\n" + bloc
        else:
            paragraphes.append(bloc)
    ranger()
    return resultat


def couper(paragraphes):
    """Regroupe les paragraphes en paquets d'au plus MOTS_MAX mots."""
    paquets, courant, taille = [], [], 0
    for p in paragraphes:
        n = len(p.split())
        if courant and taille + n > MOTS_MAX:
            paquets.append(courant)
            courant, taille = [], 0
        courant.append(p)
        taille += n
    if courant:
        paquets.append(courant)
    return paquets


def main():
    morceaux = []
    for chemin in sorted(DOSSIER_DOCUMENTS.glob("*.md")):
        meta, texte = lire_document(chemin)
        # La ligne « Vérifié le … » devient une métadonnée, pas du texte à chercher.
        verifie = re.search(r"^Vérifié le (\d+ \S+ \d{4})", texte, re.M)
        texte = re.sub(r"^Vérifié le .*$", "", texte, flags=re.M)
        for fil, paragraphes in sections(texte):
            for paquet in couper(paragraphes):
                morceaux.append({
                    "id": f"{chemin.stem}#{len([m for m in morceaux if m['fichier'] == chemin.name])}",
                    "fichier": chemin.name,
                    "titre_page": meta["titre"],
                    "source": meta["source"],
                    "verifie_le": verifie.group(1) if verifie else None,
                    "date_consultation": meta.get("date_consultation"),
                    # le 1er élément du fil est le titre de page (#) : inutile de le répéter
                    "fil": fil[1:],
                    "texte": "\n\n".join(paquet),
                })
    FICHIER_SORTIE.parent.mkdir(exist_ok=True)
    with FICHIER_SORTIE.open("w", encoding="utf-8") as f:
        for m in morceaux:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    tailles = sorted(len(m["texte"].split()) for m in morceaux)
    print(f"{len(morceaux)} morceaux écrits dans {FICHIER_SORTIE.relative_to(RACINE)}")
    print(f"taille en mots : min {tailles[0]}, médiane {tailles[len(tailles) // 2]}, max {tailles[-1]}")


if __name__ == "__main__":
    main()
