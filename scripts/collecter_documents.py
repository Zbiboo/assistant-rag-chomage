"""Télécharge les pages de service-public.gouv.fr et les convertit en Markdown.

Usage :
    python3 scripts/collecter_documents.py            # tous les documents
    python3 scripts/collecter_documents.py 01 06      # seulement certains

N'utilise que la bibliothèque standard de Python (aucune installation).
Le texte est recopié tel quel : seul le balisage HTML est converti en Markdown.
"""

import datetime
import html
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DOCUMENTS = RACINE / "documents"
BASE_URL = "https://www.service-public.gouv.fr/particuliers/vosdroits/"

# Pour chaque fichier : la fiche source et, si besoin, les chapitres à garder
# (numéros des chapitres en accordéon, identiques dans chaque onglet).
# chapitres=None -> on garde toute la page.
DOCUMENTS = [
    ("01-conditions-are.md", "F38881", [1, 2, 3, 4]),
    ("02-montant-are.md", "F38881", [5, 6, 7]),
    ("03-duree-indemnisation.md", "F38881", [8, 10]),
    ("04-inscription-france-travail.md", "F1636", None),
    ("05-demission-reconversion.md", "F89", None),
    ("06-rupture-conventionnelle.md", "F19030", None),
    ("07-formation-aref.md", "F291", None),
    ("08-chomage-agents-publics.md", "F38882", None),
    ("09-cumul-reprise-emploi.md", "F38881", [9]),
    ("10-actualisation-obligations.md", "F1637", None),
    ("11-contester-decision.md", "F2761", None),
    ("12-contrat-engagement-obligations.md", "F14926", None),
    ("13-radiation-france-travail.md", "F1638", None),
    ("14-suppression-allocations.md", "F31197", None),
]

# Repères HTML qui marquent la fin du contenu principal d'une fiche
# (blocs « Où s'informer », « Textes de référence », « Voir aussi », etc.).
MARQUEURS_FIN = [
    'data-test="ou-s-informer"',
    'id="orientation"',
    'data-test="textes-de-reference"',
    'data-test="voir-aussi"',
    'data-test="questions-reponses"',
    'class="sp-notation',
]

BLOCS = {"p", "li", "caption", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "dt", "dd"}


def telecharger(fiche):
    req = urllib.request.Request(BASE_URL + fiche, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as rep:
        return rep.read().decode("utf-8"), rep.geturl()


def contenu_principal(page):
    """Garde la partie de l'article entre le titre (h1) et le premier bloc annexe."""
    debut = page.index('<h1 id="titlePage"')
    fin = len(page)
    for marqueur in MARQUEURS_FIN:
        pos = page.find(marqueur, debut)
        if pos != -1:
            fin = min(fin, page.rfind("<", debut, pos))
    return page[debut:fin]


class VersMarkdown(HTMLParser):
    """Convertit le HTML d'une fiche en une liste de blocs (type, niveau, texte)."""

    def __init__(self, chapitres=None):
        super().__init__(convert_charrefs=True)
        self.chapitres = chapitres
        self.pile = []  # (balise, ignorer) pour chaque élément ouvert
        self.ignore = 0  # profondeur d'éléments ignorés
        self.blocs = []  # (type, niveau, texte)
        self.texte = []
        self.bloc_courant = None  # (type, niveau)
        self.listes = 0
        self.ligne_tableau = None
        self.cellule = None
        self.en_tete_tableau = False
        self.chapitre_exclu = False
        self.dans_titre_chapitre = False

    # --- éléments à ignorer -------------------------------------------------
    def a_ignorer(self, balise, attrs):
        classes = attrs.get("class", "")
        if balise in ("script", "style", "svg", "form", "noscript", "fieldset"):
            return True
        if "fr-tooltip" in classes:  # infobulles vides (« : titleContent »)
            return True
        if attrs.get("id") in ("autreCas", "rg_layout", "infosNoPerso"):
            # lien « Autres cas ? », sélecteur « Quelle est votre situation ? »
            return True
        if attrs.get("data-test") == "button-video-version-text":  # bouton vidéo
            return True
        if "fr-tabs__list" in classes:  # boutons des onglets
            return True
        if "sp-chapter-intro" in classes:  # bouton « Tout déplier »
            return True
        if "sp-accordion-chapter-btn-number" in classes:  # icône du chapitre
            return True
        if attrs.get("data-test") == "date-maj":
            return False
        if balise == "p" and "fr-sr-only" in classes:  # consigne d'interface
            return True
        if "sp-share" in classes or "sp-toolbar" in classes:
            return True
        return False

    # --- gestion des blocs --------------------------------------------------
    def ouvrir_bloc(self, type_, niveau=0):
        self.fermer_bloc()
        self.bloc_courant = (type_, niveau)
        self.texte = []

    def fermer_bloc(self):
        if self.bloc_courant is None:
            return
        texte = " ".join("".join(self.texte).split())
        if texte and not self.chapitre_exclu:
            self.blocs.append((self.bloc_courant[0], self.bloc_courant[1], texte))
        self.bloc_courant = None
        self.texte = []

    def handle_starttag(self, balise, attrs_liste):
        attrs = {k: (v or "") for k, v in attrs_liste}
        if balise in ("br", "img", "input", "hr", "meta", "link"):
            if balise == "br":
                self.texte.append(" ")
            return
        ignorer = self.ignore > 0 or self.a_ignorer(balise, attrs)
        self.pile.append((balise, ignorer, attrs))
        if ignorer:
            self.ignore += 1
            return

        # Début d'un chapitre en accordéon : décide s'il est gardé.
        if balise == "section" and "fr-accordion" in attrs.get("class", ""):
            self.fermer_bloc()
            self.chapitre_exclu = False
        if balise == "button" and attrs.get("id", "").startswith("accordion-chapter-btn-chapitre"):
            num = int(re.search(r"chapitre(\d+)", attrs["id"]).group(1))
            if self.chapitres is not None and num not in self.chapitres:
                self.chapitre_exclu = True
        if balise == "div" and attrs.get("id", "").startswith("tab-content-situation"):
            self.fermer_bloc()
            self.chapitre_exclu = False

        if balise in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.ouvrir_bloc("titre", int(balise[1]))
        elif balise in ("ul", "ol"):
            self.fermer_bloc()
            self.listes += 1
        elif balise == "li":
            self.ouvrir_bloc("puce", self.listes)
        elif balise == "p":
            if self.cellule is not None:
                if self.cellule:
                    self.cellule.append(" ")
                return
            gras = "fr-text--bold" in attrs.get("class", "")
            if self.bloc_courant and self.bloc_courant[0] == "puce" and "".join(self.texte).strip():
                self.texte.append(" ")
                return
            if not (self.bloc_courant and self.bloc_courant[0] == "puce"):
                self.ouvrir_bloc("gras" if gras else "para")
        elif balise == "caption":
            self.ouvrir_bloc("para")
        elif balise == "tr":
            self.fermer_bloc()
            self.ligne_tableau = []
        elif balise in ("td", "th"):
            self.fermer_cellule()
            self.cellule = []
            self.en_tete_tableau = balise == "th"
        elif balise == "div" and self.bloc_courant and self.bloc_courant[0] in ("para", "gras"):
            self.fermer_bloc()

    def fermer_cellule(self):
        if self.cellule is not None and self.ligne_tableau is not None:
            self.ligne_tableau.append(" ".join("".join(self.cellule).split()))
        self.cellule = None

    def handle_endtag(self, balise):
        if balise in ("br", "img", "input", "hr", "meta", "link"):
            return
        # remonte la pile jusqu'à la balise correspondante (HTML parfois mal fermé)
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i][0] == balise:
                break
        else:
            return
        while len(self.pile) > i:
            b, ignorer, attrs = self.pile.pop()
            if ignorer:
                self.ignore -= 1
                continue
            self.fin_element(b)

    def fin_element(self, balise):
        if balise in ("h1", "h2", "h3", "h4", "h5", "h6", "li", "caption"):
            self.fermer_bloc()
        elif balise == "p":
            if self.cellule is None and not (self.bloc_courant and self.bloc_courant[0] == "puce"):
                self.fermer_bloc()
        elif balise in ("ul", "ol"):
            self.fermer_bloc()
            self.listes -= 1
        elif balise in ("td", "th"):
            self.fermer_cellule()
        elif balise == "tr":
            self.fermer_cellule()
            if self.ligne_tableau and not self.chapitre_exclu:
                type_ = "entete" if self.en_tete_tableau else "ligne"
                self.blocs.append((type_, 0, self.ligne_tableau))
            self.ligne_tableau = None
        elif balise == "div":
            if self.bloc_courant and self.bloc_courant[0] in ("para", "gras"):
                self.fermer_bloc()

    def handle_data(self, data):
        if self.ignore:
            return
        if self.cellule is not None:
            self.cellule.append(data)
        elif self.bloc_courant is not None:
            self.texte.append(data)
        elif data.strip():
            # texte « orphelin » directement dans une div : on en fait un paragraphe
            self.ouvrir_bloc("para")
            self.texte.append(data)


def blocs_vers_markdown(blocs):
    # Les niveaux de titres HTML (h2..h6) sont renumérotés sans « trou » :
    # sous le titre de la page (#), le premier niveau devient ##, puis ###, etc.
    # On garde une pile des niveaux HTML ouverts pour connaître la profondeur.
    pile_titres = []
    lignes = []
    dans_tableau = False
    for type_, niveau, texte in blocs:
        if type_ in ("entete", "ligne"):
            cellules = [c.replace("|", "\\|") for c in texte]
            if not dans_tableau:
                lignes.append("")
                if type_ == "entete":
                    lignes.append("| " + " | ".join(cellules) + " |")
                    lignes.append("|" + "---|" * len(cellules))
                else:  # tableau sans en-tête
                    lignes.append("| " + " | ".join([""] * len(cellules)) + " |")
                    lignes.append("|" + "---|" * len(cellules))
                    lignes.append("| " + " | ".join(cellules) + " |")
                dans_tableau = True
            else:
                lignes.append("| " + " | ".join(cellules) + " |")
            continue
        if dans_tableau:
            lignes.append("")
            dans_tableau = False
        if type_ == "titre":
            if niveau == 1:
                n = 1
            else:
                while pile_titres and pile_titres[-1] >= niveau:
                    pile_titres.pop()
                pile_titres.append(niveau)
                n = len(pile_titres) + 1
            lignes += ["", "#" * n + " " + texte, ""]
        elif type_ == "puce":
            precedente = lignes[-1] if lignes else ""
            if precedente.strip() and not precedente.lstrip().startswith("- "):
                lignes.append("")  # ligne vide avant le début d'une liste
            lignes.append("  " * (niveau - 1) + "- " + texte)
        elif type_ == "gras":
            lignes += ["", "**" + texte + "**", ""]
        else:
            lignes += ["", texte, ""]
    md = "\n".join(lignes)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md


def retirer_titres_vides(md):
    """Supprime les titres d'onglets/chapitres dont tout le contenu a été exclu."""
    lignes = md.split("\n")
    resultat = []
    for i, ligne in enumerate(lignes):
        m = re.match(r"(#+) ", ligne)
        if m:
            niveau = len(m.group(1))
            suite = [l for l in lignes[i + 1:] if l.strip()]
            prochain = suite[0] if suite else ""
            m2 = re.match(r"(#+) ", prochain)
            if not suite or (m2 and len(m2.group(1)) <= niveau):
                continue
        resultat.append(ligne)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(resultat))


def convertir(page, chapitres=None):
    titre = html.unescape(re.search(r'<h1 id="titlePage"[^>]*>(.*?)</h1>', page, re.S).group(1))
    titre = " ".join(re.sub(r"<[^>]+>", "", titre).split())
    p = VersMarkdown(chapitres)
    p.feed(contenu_principal(page))
    p.close()
    p.fermer_bloc()
    md = blocs_vers_markdown(p.blocs)
    if chapitres is not None:
        md = retirer_titres_vides(md)
    return titre, md


def main(selection):
    date = datetime.date.today().isoformat()
    DOSSIER_DOCUMENTS.mkdir(exist_ok=True)
    cache = {}
    for nom, fiche, chapitres in DOCUMENTS:
        if selection and nom[:2] not in selection:
            continue
        if fiche not in cache:
            cache[fiche] = telecharger(fiche)
        page, url = cache[fiche]
        titre, md = convertir(page, chapitres)
        entete = f"---\ntitre: {titre}\nsource: {url}\ndate_consultation: {date}\n---\n\n"
        (DOSSIER_DOCUMENTS / nom).write_text(entete + md, encoding="utf-8")
        print(f"{nom}: {len(md.split())} mots ({fiche})")


if __name__ == "__main__":
    main(sys.argv[1:])
