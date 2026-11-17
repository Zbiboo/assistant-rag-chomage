"""Évaluation de l'assistant : recherche et qualité des réponses.

Usage :
    .venv/bin/python eval/run_eval.py                                   # Haiku puis Sonnet
    .venv/bin/python eval/run_eval.py claude-haiku-5-5                  # un seul modèle
    .venv/bin/python eval/run_eval.py --recherche-seule                 # sans réponses (moins cher)
    .venv/bin/python eval/run_eval.py --recalculer                      # rescorer, sans appel API

Pour chaque question de eval/questions.json :
  a. RECHERCHE, sans reformulation (question brute) et avec reformulation :
     - critère indulgent : la bonne fiche est-elle parmi les 5 extraits ?
     - critère strict : les éléments clés de la bonne réponse sont-ils
       présents dans le texte de ces extraits ? (le modèle ne peut pas citer
       une information qu'on ne lui a pas donnée)
  b. RÉPONSE (pour chaque modèle comparé, sur les MÊMES extraits) :
     - les éléments clés attendus sont-ils présents ?
     - les citations [n] renvoient-elles à des extraits réellement fournis ?
     - pour les questions hors corpus : la réponse dit-elle « je ne sais pas » ?

Résultats : eval/resultats.md (tableaux) et eval/reponses.json (réponses complètes).
"""

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))

import config  # noqa: E402
from demander import Assistant  # noqa: E402

DOSSIER = Path(__file__).resolve().parent
MODELES_PAR_DEFAUT = ["claude-haiku-5-5", "claude-sonnet-5-5"]

# Tournures qui montrent que le modèle reconnaît ne pas avoir l'information.
FORMULES_ABSTENTION = [
    "je ne sais pas", "ne permettent pas", "ne permet pas", "ne contiennent pas",
    "ne contient pas", "ne mentionnent pas", "ne mentionne pas", "ne traitent pas",
    "ne traite pas", "ne parlent pas", "ne donnent pas", "ne precisent pas",
    "ne couvrent pas", "ne concernent pas", "ne portent pas", "aucune information",
    "pas d'information", "ne trouve pas", "n'ai pas trouve", "ne dispose pas",
    "n'abordent pas", "n'aborde pas", "ne figure pas", "ne figurent pas",
    "ne me permettent pas", "ne me permet pas", "ne disent rien", "ne dit rien",
]


def normaliser(texte):
    """Minuscules, sans accents, espaces unifiés, « 1 300 » -> « 1300 », « 30% » -> « 30 % »."""
    texte = unicodedata.normalize("NFD", texte.lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    texte = texte.replace(" ", " ").replace(" ", " ").replace("’", "'")
    texte = re.sub(r"(\d) (\d{3})\b", r"\1\2", texte)
    texte = re.sub(r"\s*%", " %", texte)
    texte = re.sub(r"[«»\"“”*]", " ", texte)  # guillemets et gras Markdown ignorés
    return " ".join(texte.split())


def contient(texte, expression):
    """Vrai si `expression` apparaît en mots entiers (« are » n'est pas trouvé dans « declarer »)."""
    return re.search(r"(?<!\w)" + re.escape(expression) + r"(?!\w)", texte) is not None


def elements_trouves(reponse, elements_cles):
    """Pour chaque élément (liste d'alternatives), True si l'une est dans la réponse.

    Limite connue : on ne sait pas si l'élément est affirmé ou nié (« les extraits
    ne parlent pas de l'allocation chômage » contient « allocation chomage »).
    D'où l'intérêt de lire les réponses en cas de doute.
    """
    r = normaliser(reponse)
    return [any(contient(r, normaliser(alt)) for alt in alternatives) for alternatives in elements_cles]


def citations(reponse):
    """Tous les numéros cités : « [1] », « [1][2] », « [1, 3] », « [2-4] »."""
    numeros = []
    for groupe in re.findall(r"\[(\d+(?:\s*[,;–-]\s*\d+)*)\]", reponse):
        for partie in re.split(r"\s*[,;]\s*", groupe):
            if re.match(r"\d+\s*[–-]\s*\d+", partie):
                a, b = map(int, re.split(r"\s*[–-]\s*", partie))
                numeros += list(range(a, b + 1))
            else:
                numeros.append(int(partie))
    return numeros


def texte_des(extraits):
    return " ".join(" ".join(m["fil"]) + " " + m["texte"] for m in extraits)


def s_abstient(reponse):
    r = normaliser(reponse)
    return any(f in r for f in FORMULES_ABSTENTION)


def verifier_questions(questions):
    """Garde-fou : chaque élément clé doit exister dans au moins une fiche attendue."""
    erreurs = []
    for q in questions:
        textes = normaliser(" ".join(
            (RACINE / "documents" / f).read_text(encoding="utf-8") for f in q["fichiers_attendus"]
        ))
        for alternatives in q["elements_cles"]:
            if not any(normaliser(a) in textes for a in alternatives):
                erreurs.append(f"{q['id']} : {alternatives} introuvable dans {q['fichiers_attendus']}")
    return erreurs


def pourcentage(n, total):
    return f"{100 * n / total:.0f} %" if total else "–"


def recalculer(questions):
    """Recalcule tous les scores à partir de eval/reponses.json, SANS appel à l'API.

    Utile quand on corrige la façon de noter : on ne repaie pas les réponses.
    """
    resultats = json.loads((DOSSIER / "reponses.json").read_text(encoding="utf-8"))
    par_id = {q["id"]: q for q in questions}
    for r in resultats:
        q = par_id[r["id"]]
        for cle in ("sans", "avec"):
            if f"texte_extraits_{cle}" in r:
                r[f"infos_{cle}"] = elements_trouves(r[f"texte_extraits_{cle}"], q["elements_cles"])
        for x in r["reponses"].values():
            x["elements_trouves"] = elements_trouves(x["texte"], q["elements_cles"])
            x["citations"] = citations(x["texte"])
            x["citations_invalides"] = [n for n in x["citations"] if not 1 <= n <= len(r["fichiers_avec"])]
            x["abstention"] = s_abstient(x["texte"])
    modeles = list(resultats[0]["reponses"])
    (DOSSIER / "reponses.json").write_text(
        json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    ecrire_rapport(resultats, modeles)
    print("Scores recalculés sans appel à l'API : eval/resultats.md")


def main():
    args = sys.argv[1:]
    if "--recalculer" in args:
        questions = json.loads((DOSSIER / "questions.json").read_text(encoding="utf-8"))
        return recalculer(questions)
    recherche_seule = "--recherche-seule" in args
    modeles = [a for a in args if not a.startswith("--")] or MODELES_PAR_DEFAUT
    if recherche_seule:
        modeles = []

    questions = json.loads((DOSSIER / "questions.json").read_text(encoding="utf-8"))
    erreurs = verifier_questions(questions)
    if erreurs:
        sys.exit("Questions incohérentes avec les fiches :\n" + "\n".join(erreurs))
    print(f"✅ {len(questions)} questions, éléments clés tous présents dans les fiches attendues.\n")

    assistant = Assistant()
    resultats = []
    for q in questions:
        print(f"{q['id']} : {q['question']}")
        r = {"id": q["id"], "question": q["question"], "hors_corpus": q.get("hors_corpus", False),
             "fichiers_attendus": q["fichiers_attendus"], "reponses": {}}

        # a. Recherche, sans puis avec reformulation (une seule reformulation par question)
        sans = assistant.chercher(q["question"])
        reformulation = assistant.reformuler(q["question"])
        avec = assistant.chercher(q["question"], reformulation["texte"])
        r["mots_cles"] = reformulation["texte"]
        r["cout_reformulation"] = reformulation["cout"]
        r["fichiers_sans"] = [m["fichier"] for m in sans]
        r["fichiers_avec"] = [m["fichier"] for m in avec]
        attendus = set(q["fichiers_attendus"])
        r["recherche_sans_ok"] = bool(attendus & set(r["fichiers_sans"]))
        r["recherche_avec_ok"] = bool(attendus & set(r["fichiers_avec"]))
        # Critère strict : les éléments clés figurent-ils dans le texte des extraits ?
        # (textes conservés pour pouvoir recalculer les scores sans refaire d'appels)
        r["texte_extraits_sans"] = texte_des(sans)
        r["texte_extraits_avec"] = texte_des(avec)
        r["infos_sans"] = elements_trouves(r["texte_extraits_sans"], q["elements_cles"])
        r["infos_avec"] = elements_trouves(r["texte_extraits_avec"], q["elements_cles"])

        # b. Réponses : chaque modèle reçoit exactement les mêmes extraits
        for modele in modeles:
            debut = time.time()
            g = assistant.generer(q["question"], avec, modele=modele)
            nums = citations(g["texte"])
            trouves = elements_trouves(g["texte"], q["elements_cles"])
            r["reponses"][modele] = {
                "texte": g["texte"],
                "secondes": round(time.time() - debut, 1),
                "cout": g["cout"],
                "tokens_entree": g["tokens_entree"],
                "tokens_sortie": g["tokens_sortie"],
                "elements_trouves": trouves,
                "citations": nums,
                "citations_invalides": [n for n in nums if not 1 <= n <= len(avec)],
                "abstention": s_abstient(g["texte"]),
            }
            etat = (f"{sum(trouves)}/{len(trouves)} éléments" if trouves
                    else f"abstention={'oui' if r['reponses'][modele]['abstention'] else 'NON'}")
            print(f"   {modele:<18} {etat}, {len(nums)} citations, {g['cout']:.4f} $")
        resultats.append(r)

    (DOSSIER / "reponses.json").write_text(
        json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    ecrire_rapport(resultats, modeles)
    print(f"\nRapport : {(DOSSIER / 'resultats.md').relative_to(RACINE)}")


def ecrire_rapport(resultats, modeles):
    dans_corpus = [r for r in resultats if not r["hors_corpus"]]
    hors = [r for r in resultats if r["hors_corpus"]]
    n = len(dans_corpus)
    L = ["# Résultats de l'évaluation", "",
         f"{len(resultats)} questions ({n} sur le corpus, {len(hors)} hors corpus). "
         f"Reformulation : {config.MODELE_REFORMULATION}. Extraits par question : {config.NB_EXTRAITS}.", "",
         "## Recherche : la bonne fiche est-elle parmi les extraits ?", "",
         "| Méthode | Bonne fiche parmi les extraits | Éléments clés présents dans les extraits | Questions avec tous leurs éléments |",
         "|---|---|---|---|"]
    for nom, cle in (("BM25 sur la question brute", "sans"), ("BM25 + reformulation", "avec")):
        fiche = sum(r[f"recherche_{cle}_ok"] for r in dans_corpus)
        infos = [x for r in dans_corpus for x in r[f"infos_{cle}"]]
        complets = sum(all(r[f"infos_{cle}"]) for r in dans_corpus)
        L.append(f"| {nom} | {fiche}/{n} ({pourcentage(fiche, n)}) | {sum(infos)}/{len(infos)} "
                 f"({pourcentage(sum(infos), len(infos))}) | {complets}/{n} |")
    L.append("")

    if modeles:
        L += ["## Réponses : comparaison des modèles", "",
              "| | " + " | ".join(modeles) + " |", "|---|" + "---|" * len(modeles)]

        def ligne(nom, f):
            L.append(f"| {nom} | " + " | ".join(f(m) for m in modeles) + " |")

        def rep(m):
            return [r["reponses"][m] for r in dans_corpus]

        ligne("Éléments clés trouvés", lambda m: pourcentage(
            sum(sum(x["elements_trouves"]) for x in rep(m)),
            sum(len(x["elements_trouves"]) for x in rep(m))))
        ligne("Questions avec tous les éléments", lambda m: f"{sum(all(x['elements_trouves']) for x in rep(m))}/{n}")
        ligne("Réponses avec au moins une citation", lambda m: f"{sum(bool(x['citations']) for x in rep(m))}/{n}")
        ligne("Citations invalides", lambda m: str(sum(
            len(r["reponses"][m]["citations_invalides"]) for r in resultats)))
        ligne("Hors corpus : « je ne sais pas »", lambda m: f"{sum(r['reponses'][m]['abstention'] for r in hors)}/{len(hors)}")
        ligne("Temps moyen de réponse", lambda m: f"{sum(r['reponses'][m]['secondes'] for r in resultats) / len(resultats):.1f} s")

        def cout_question(m):
            total = sum(r["reponses"][m]["cout"] + r["cout_reformulation"] for r in resultats)
            return total / len(resultats)
        ligne("Coût moyen par question (reformulation incluse)", lambda m: f"{cout_question(m):.4f} $")
        ligne("Questions pour 1 $", lambda m: f"≈ {1 / cout_question(m):.0f}")
        L.append("")

    L += ["## Détail par question", "",
          "| Question | Éléments dans les extraits (sans / avec reformulation) |"
          + "".join(f" Éléments dans la réponse {m} |" for m in modeles),
          "|---|---|" + "---|" * len(modeles)]
    for r in resultats:
        if r["hors_corpus"]:
            recherche = "hors corpus"
            cases = ["abstention ✅" if r["reponses"][m]["abstention"] else "abstention ❌" for m in modeles]
        else:
            recherche = (f"{sum(r['infos_sans'])}/{len(r['infos_sans'])} / "
                         f"{sum(r['infos_avec'])}/{len(r['infos_avec'])}")
            cases = [f"{sum(r['reponses'][m]['elements_trouves'])}/{len(r['reponses'][m]['elements_trouves'])}"
                     for m in modeles]
        L.append(f"| {r['id']} {r['question']} | {recherche} |" + "".join(f" {c} |" for c in cases))
    L.append("")

    echecs = [r for r in dans_corpus if not (all(r["infos_sans"]) and all(r["infos_avec"]))]
    L += ["## Échecs de recherche (au moins un élément clé absent des extraits)", ""]
    if not echecs:
        L.append("Aucun.")
    for r in echecs:
        L += [f"**{r['id']}** {r['question']}",
              f"- Attendu : {', '.join(r['fichiers_attendus'])}",
              f"- Éléments présents : sans reformulation {sum(r['infos_sans'])}/{len(r['infos_sans'])}, "
              f"avec {sum(r['infos_avec'])}/{len(r['infos_avec'])}",
              f"- Sans reformulation : {', '.join(r['fichiers_sans'])}",
              f"- Avec reformulation (mots-clés : {r['mots_cles']}) : {', '.join(r['fichiers_avec'])}", ""]
    # La section « ## Analyse… » est écrite à la main : on la conserve telle quelle.
    fichier = DOSSIER / "resultats.md"
    ancien = fichier.read_text(encoding="utf-8") if fichier.exists() else ""
    debut_analyse = ancien.find("\n## Analyse")
    analyse = ancien[debut_analyse:] if debut_analyse != -1 else ""
    fichier.write_text("\n".join(L) + "\n" + analyse, encoding="utf-8")


if __name__ == "__main__":
    main()
