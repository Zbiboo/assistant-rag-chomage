"""Convertit NOTIONS.md en un document Word propre : guide-projet.docx.

Usage :
    .venv/bin/python scripts/generer_guide.py

NOTIONS.md reste la source (on le complète à chaque étape) ; ce script le
relit et produit la version Word. Il ne comprend que le Markdown utilisé dans
ce guide : titres (#, ##, ###), paragraphes, listes (- et 1.), tableaux,
blocs de code (```), **gras**, `code` et [liens](chemin).
"""

import datetime
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "NOTIONS.md"
SORTIE = RACINE / "guide-projet.docx"

POLICE = "Arial"
POLICE_CODE = "Menlo"
BLEU = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = RGBColor(0x5F, 0x63, 0x68)
FOND_CODE = "F2F2F2"
FOND_ENTETE = "DCE6F2"
COULEURS_ETAT = {"Terminé": "2E7D32", "Prochaine étape": "E65100", "À faire": "5F6368"}


# --- Petits utilitaires de mise en forme -------------------------------------

def colorier_fond(element, couleur):
    """Ajoute une couleur de fond à un paragraphe ou une cellule (balise w:shd)."""
    proprietes = element.get_or_add_pPr() if hasattr(element, "get_or_add_pPr") else element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), couleur)
    proprietes.append(shd)


def ajouter_texte(paragraphe, texte, taille=None, couleur=None, italique=False):
    """Écrit du texte en interprétant **gras**, `code` et [liens](chemin)."""
    # On découpe le texte en morceaux : normal / **gras** / `code` / [lien](...)
    for morceau in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))", texte):
        if not morceau:
            continue
        if morceau.startswith("**"):
            run = paragraphe.add_run(morceau[2:-2])
            run.bold = True
        elif morceau.startswith("`"):
            run = paragraphe.add_run(morceau[1:-1])
            run.font.name = POLICE_CODE
            run.font.size = Pt(9)
        elif morceau.startswith("["):
            # Les liens pointent vers des fichiers du projet : on affiche le
            # texte du lien en police « code » pour qu'il soit repérable.
            run = paragraphe.add_run(re.match(r"\[([^\]]+)\]", morceau).group(1))
            run.font.name = POLICE_CODE
            run.font.size = Pt(9)
        else:
            run = paragraphe.add_run(morceau)
        if taille and not run.font.size:
            run.font.size = taille
        if couleur:
            run.font.color.rgb = couleur
        run.italic = italique or None


def configurer_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = POLICE
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    for nom, taille, avant in (("Title", 26, 0), ("Heading 1", 16, 18), ("Heading 2", 13, 12)):
        style = doc.styles[nom]
        style.font.name = POLICE
        style.font.size = Pt(taille)
        style.font.bold = True
        style.font.color.rgb = BLEU
        style.paragraph_format.space_before = Pt(avant)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True
        # Les titres du modèle Word utilisent une police « de thème » qui
        # écraserait la nôtre : on retire ce lien vers le thème.
        polices = style.element.rPr.rFonts
        for attribut in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            polices.attrib.pop(qn(attribut), None)
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Cm(2.2)
        section.left_margin = section.right_margin = Cm(2.3)


# --- Les différents types de blocs -------------------------------------------

def ajouter_bordures(tableau):
    """Bordures fines grises sur tout le tableau (balise w:tblBorders)."""
    bordures = OxmlElement("w:tblBorders")
    for cote in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{cote}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:color"), "BFBFBF")
        bordures.append(b)
    proprietes = tableau._tbl.tblPr
    # w:tblBorders doit venir après w:tblStyle/w:tblW/w:jc et avant w:tblLayout/w:tblLook
    suivant = proprietes.find(qn("w:tblLayout"))
    if suivant is None:
        suivant = proprietes.find(qn("w:tblLook"))
    if suivant is not None:
        suivant.addprevious(bordures)
    else:
        proprietes.append(bordures)


def ajouter_tableau(doc, lignes):
    cellules = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lignes]
    entete, corps = cellules[0], [c for c in cellules[2:]]  # ligne 2 = |---|---|
    tableau = doc.add_table(rows=1 + len(corps), cols=len(entete))
    tableau.style = "Table Grid"
    tableau.alignment = WD_TABLE_ALIGNMENT.CENTER
    tableau.autofit = False
    ajouter_bordures(tableau)
    largeurs = [Cm(3.0), Cm(10.4), Cm(3.0)] if len(entete) == 3 else None
    if largeurs:
        for j, largeur in enumerate(largeurs):
            tableau.columns[j].width = largeur
    for i, ligne in enumerate([entete] + corps):
        for j, texte in enumerate(ligne):
            cellule = tableau.cell(i, j)
            if largeurs:
                cellule.width = largeurs[j]
            p = cellule.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            ajouter_texte(p, texte, taille=Pt(10))
            if i == 0:
                for run in p.runs:
                    run.bold = True
                colorier_fond(cellule._tc, FOND_ENTETE)
            elif texte in COULEURS_ETAT:  # colonne « État » en couleur
                for run in p.runs:
                    run.bold = True
                    run.font.color.rgb = RGBColor.from_string(COULEURS_ETAT[texte])
    doc.add_paragraph()


def ajouter_code(doc, lignes):
    for k, ligne in enumerate(lignes):
        p = doc.add_paragraph()
        # Le fond doit être posé en premier : dans le XML de Word, la balise de
        # fond (w:shd) doit précéder celles d'espacement et de retrait.
        colorier_fond(p._p, FOND_CODE)
        p.paragraph_format.space_after = Pt(0) if k < len(lignes) - 1 else Pt(8)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Cm(0.3)
        run = p.add_run(ligne)
        run.font.name = POLICE_CODE
        run.font.size = Pt(8.5)


def ajouter_liste(doc, texte, numero=None, niveau=0):
    if numero is None:
        p = doc.add_paragraph(style="List Bullet")
    else:
        # Numéros écrits à la main : les listes numérotées automatiques de Word
        # continueraient la numérotation d'une liste à l'autre (1, 2, 3, 4, 5…).
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.9)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.add_run(f"{numero}.  ").bold = True
    if niveau:
        p.paragraph_format.left_indent = Cm(0.9 + 0.6 * niveau)
    p.paragraph_format.space_after = Pt(3)
    ajouter_texte(p, texte)


def ajouter_voir(doc, texte):
    """Les lignes « → Voir : … » : petites, grises, en italique."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    ajouter_texte(p, texte, taille=Pt(9.5), couleur=GRIS, italique=True)


# --- Lecture du Markdown -----------------------------------------------------

def blocs_markdown(texte):
    """Découpe le Markdown en blocs : (type, contenu)."""
    lignes = texte.split("\n")
    i = 0
    while i < len(lignes):
        ligne = lignes[i]
        if not ligne.strip():
            i += 1
        elif ligne.startswith("```"):
            fin = lignes.index("```", i + 1)
            yield "code", lignes[i + 1:fin]
            i = fin + 1
        elif ligne.startswith("#"):
            niveau = len(ligne) - len(ligne.lstrip("#"))
            yield f"titre{niveau}", ligne.lstrip("#").strip()
            i += 1
        elif ligne.startswith("|"):
            debut = i
            while i < len(lignes) and lignes[i].startswith("|"):
                i += 1
            yield "tableau", lignes[debut:i]
        elif re.match(r"\s*(- |\d+\. )", ligne):
            # Un élément de liste, plus ses lignes de continuation indentées.
            contenu = [ligne]
            i += 1
            while i < len(lignes) and lignes[i].startswith("  ") and not re.match(r"\s*(- |\d+\. )", lignes[i]):
                contenu.append(lignes[i].strip())
                i += 1
            premiere = contenu[0]
            niveau = (len(premiere) - len(premiere.lstrip())) // 2
            m = re.match(r"\s*(?:- |(\d+)\. )(.*)", premiere)
            yield "liste", (m.group(1), " ".join([m.group(2)] + contenu[1:]), niveau)
        else:
            # Paragraphe : on recolle les lignes jusqu'à une ligne vide ou un autre bloc.
            contenu = []
            while i < len(lignes) and lignes[i].strip() and not re.match(r"(#|\||```|\s*- |\s*\d+\. )", lignes[i]):
                contenu.append(lignes[i].strip())
                i += 1
            yield "paragraphe", " ".join(contenu)


def main():
    doc = Document()
    configurer_styles(doc)
    for type_, contenu in blocs_markdown(SOURCE.read_text(encoding="utf-8")):
        if type_ == "titre1":
            doc.add_paragraph(contenu, style="Title")
            p = doc.add_paragraph()
            date = datetime.date.today().strftime("%d/%m/%Y")
            ajouter_texte(p, f"Mis à jour le {date}", couleur=GRIS, italique=True)
        elif type_ == "titre2":
            doc.add_heading(contenu, level=1)
        elif type_ == "titre3":
            doc.add_heading(contenu, level=2)
        elif type_ == "tableau":
            ajouter_tableau(doc, contenu)
        elif type_ == "code":
            ajouter_code(doc, contenu)
        elif type_ == "liste":
            numero, texte, niveau = contenu
            ajouter_liste(doc, texte, numero, niveau)
        elif contenu.startswith("→"):
            ajouter_voir(doc, contenu)
        else:
            ajouter_texte(doc.add_paragraph(), contenu)
    doc.save(SORTIE)
    print(f"Guide écrit : {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
