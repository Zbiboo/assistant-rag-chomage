---
title: Assistant chômage sourcé
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.32.0
python_version: 3.12.12
app_file: app.py
pinned: false
short_description: Réponses sourcées sur le chômage (fiches service-public)
---

# Assistant chômage et France Travail : des réponses sourcées

Un assistant qui répond aux questions sur l'allocation chômage et France Travail **uniquement à partir des fiches officielles de service-public.gouv.fr**, en **citant ses sources** [1], [2]… Il dit « je ne sais pas » quand l'information n'y figure pas.

**Démo en ligne :** bientôt disponible sur Hugging Face Spaces (voir [Mise en ligne](#mise-en-ligne)).

> Projet personnel réalisé dans le cadre de ma reconversion vers le développement IA. Tout est codé à la main en Python, sans LangChain ni LlamaIndex, pour comprendre et maîtriser chaque brique d'un système RAG.

⚠️ Il s'agit d'une démonstration : les réponses sont des informations générales et ne remplacent pas un conseiller France Travail.

---

## Ce que fait l'assistant

Exemple : *« Mon patron veut que je parte mais je ne veux pas démissionner, il y a une autre solution ? »*

L'assistant explique la rupture conventionnelle et le droit au chômage qui l'accompagne. Chaque phrase est suivie de sa source [n]. Sous la réponse, la liste des sources donne le titre cliquable de la fiche, la section exacte et la date de vérification par service-public.

## Comment ça marche

C'est un **RAG** (*Retrieval-Augmented Generation*, génération augmentée par la recherche). Le modèle ne répond pas de mémoire : on lui fournit d'abord les bons passages des fiches.

```
 Question de l'utilisateur
 « je me suis fait virer, je touche combien ? »
          │
          ▼
 ┌──────────────────────────────┐
 │ 1. REFORMULATION (Claude)    │  traduit dans le vocabulaire officiel :
 │    appel court, peu coûteux  │  « licenciement, montant de l'ARE, salaire
 └──────────────────────────────┘    journalier de référence… »
          │  question d'origine + mots-clés
          ▼
 ┌──────────────────────────────┐
 │ 2. RECHERCHE BM25 (maison)   │  parmi 308 morceaux des 14 fiches,
 │    sans IA, gratuite         │  garde les 8 meilleurs, sans doublons
 └──────────────────────────────┘
          │  8 extraits numérotés [1]…[8]
          ▼
 ┌──────────────────────────────┐
 │ 3. RÉPONSE (Claude)          │  répond UNIQUEMENT à partir des extraits,
 │                              │  cite [n], dit « je ne sais pas » sinon
 └──────────────────────────────┘
          │
          ▼
 Réponse sourcée + liste des sources (fiche, section, date)
```

En amont, une seule fois :

```
 service-public.gouv.fr ──► collecter_documents.py ──► documents/*.md (14 fiches fidèles)
                                                              │
                                                 decouper.py  ▼
                                    data/morceaux.jsonl (308 morceaux + fil de titres + source)
```

| Fichier | Rôle |
|---|---|
| [scripts/collecter_documents.py](scripts/collecter_documents.py) | Télécharge les fiches et les convertit en Markdown, mot pour mot |
| [scripts/decouper.py](scripts/decouper.py) | Découpe en morceaux de 300 mots maximum, chacun avec son fil de titres (« Vous avez 55 ou 56 ans > Montant brut ») |
| [scripts/rechercher.py](scripts/rechercher.py) | Moteur de recherche BM25 écrit à la main, avec dédoublonnage |
| [scripts/demander.py](scripts/demander.py) | Le moteur (`Assistant`) : reformulation, recherche, réponse sourcée |
| [scripts/config.py](scripts/config.py) | Tous les réglages (modèles, limites, prix), chacun modifiable par une variable d'environnement |
| [app.py](app.py) | Interface web Gradio, qui réutilise le même moteur |
| [eval/](eval/) | Jeu de 20 questions, script d'évaluation et résultats |

## Choix techniques, et pourquoi

**BM25 codé à la main, sans base vectorielle.** Le corpus compte 308 morceaux. À cette échelle, une base vectorielle et des embeddings ajoutent des dépendances, un coût et de l'opacité, sans gain démontré. BM25 est l'algorithme de référence de la recherche par mots-clés. Il tient en une centaine de lignes, il est gratuit et instantané, et on peut expliquer chaque résultat. Réglages standard : k1 = 1,5, b = 0,75. Les mots sont normalisés (minuscules, sans accents ni mots vides) puis tronqués à 6 lettres, une version simple de la racinisation.

**Une reformulation contre l'écart de vocabulaire.** Un utilisateur écrit « je me suis fait virer, combien de temps je serai payé ». Les fiches, elles, parlent de « licenciement » et de « durée de versement de l'ARE ». Un premier appel court à Claude traduit donc la question en mots-clés officiels. La recherche utilise **la question d'origine ET la reformulation**, pour ne rien perdre si la reformulation se trompe. Gain mesuré : les éléments de réponse attendus présents dans les extraits passent de **68 % à 92 %**.

**Les doublons fusionnés.** 195 morceaux sur 308 répètent un texte identique, parce que les fiches reprennent le même paragraphe pour chaque tranche d'âge ou pour le privé et le public. La recherche ne garde donc qu'un exemplaire de chaque texte. Elle indique au modèle toutes les sections où il apparaît, pour qu'il sache à qui la règle s'applique.

**8 extraits plutôt que 5, après mesure.** Sur 3 passages de l'évaluation, les éléments clés présents dans les extraits passent de 35,3/39 en moyenne avec 5 extraits à **37/39** avec 8, pour environ 20 % de coût en plus. Une autre hypothèse, une reformulation plus courte, a été testée puis **rejetée** car elle n'apportait rien (34,7/39).

**Un modèle choisi grâce à l'évaluation : Claude Haiku.** Sur le même jeu de questions, Haiku et Sonnet obtiennent la même qualité : mêmes questions complètes, 0 citation invalide, et « je ne sais pas » hors sujet dans tous les cas. Mais Haiku est **13 fois moins cher**. Les erreurs restantes viennent de la recherche, pas du modèle : un modèle plus puissant ne peut pas citer un passage qu'on ne lui a pas donné.

**Une consigne stricte (prompt système).** Le modèle doit répondre uniquement à partir des extraits, citer chaque information, dire quand il ne sait pas, et tenir compte de la situation (âge, date de fin de contrat, privé ou public), car les règles en dépendent.

**Le moteur séparé de l'affichage.** La classe `Assistant` ne fait rien s'afficher. La ligne de commande, l'évaluation et la page web l'utilisent toutes les trois : l'évaluation mesure donc exactement ce que voient les visiteurs.

**Pas de framework.** Pas de LangChain ni de LlamaIndex : chaque étape est lisible et explicable. Seulement trois paquets : `anthropic`, `gradio`, et `python-docx` pour générer le guide du projet.

## Résultats de l'évaluation

Le jeu compte 20 questions. 18 portent sur le contenu des fiches, dont 5 écrites comme un vrai utilisateur (fautes et familiarités comprises). 2 sont volontairement hors sujet (retraite, APL), pour vérifier que l'assistant sait s'abstenir. Le script [eval/run_eval.py](eval/run_eval.py) vérifie la présence d'éléments clés attendus (« 6 mois », « 24 mois »…) dans les extraits et dans les réponses, et la validité des citations. Les réponses ont aussi été **lues une à une** pour repérer les erreurs du contrôle automatique.

| Mesure (Claude Haiku, 8 extraits) | Résultat |
|---|---|
| Éléments clés présents dans les extraits, sans reformulation | 36/53 (68 %) |
| Éléments clés présents dans les extraits, avec reformulation | **49/53 (92 %)** |
| Questions entièrement correctes (après lecture) | 13/18 |
| Citations invalides (numéro d'extrait inexistant) | **0** |
| Questions hors sujet : « je ne sais pas » | **2/2** |
| Temps moyen de réponse | ≈ 6 s |
| Coût moyen par question | ≈ 0,0013 $ (≈ 770 questions pour 1 $) |

Détail complet et analyse : [eval/resultats.md](eval/resultats.md).

**Les 5 échecs restants viennent tous de la recherche,** jamais d'une invention du modèle. Quand le bon passage manque, l'assistant le signale et renvoie vers France Travail.

## Sécurité et maîtrise des coûts

- **La clé API reste côté serveur.** Elle est lue dans une variable d'environnement : le fichier `.env`, ignoré par Git, en local, et les Secrets de l'hébergeur en ligne. Elle n'est jamais écrite dans le code, les commits ou les journaux, et jamais envoyée au navigateur. La page, la configuration Gradio et le journal du serveur ont été vérifiés.
- **Une vérification avant chaque push :** `git check-ignore -v .env` et une recherche de motif de clé dans les fichiers suivis par Git.
- **Un plafond global de 100 questions par jour,** pour tous les visiteurs ensemble, soit au pire environ 0,13 $ par jour. Le compteur est protégé par un verrou contre les accès simultanés.
- **Une question limitée à 500 caractères,** vérifiée avant tout appel payant.
- **Des erreurs de l'API affichées poliment,** sans détail technique pour le visiteur.
- **Une limite de dépense** fixée dans la console Anthropic, sans recharge automatique.

## Limites connues et pistes

- **L'écart de vocabulaire non résolu.** Les fiches écrivent le montant avec les sigles ARE et SJR, ce qui fait échouer en partie une question familière sur le montant. Le paragraphe qui lie rupture conventionnelle et chômage ressort mal, comme celui sur l'organisme qui paie un fonctionnaire. Une question très longue peut aussi être noyée. C'est la limite d'une recherche par mots-clés.
- **Un corpus restreint et figé.** 14 fiches, consultées le 17/11/2026. Certains sujets, comme la disponibilité d'un fonctionnaire, n'y sont pas. Les règles changent souvent : il faudrait recollecter régulièrement.
- **Une évaluation modeste.** 20 questions, écrites par nous. Le contrôle automatique cherche des mots, et ne distingue pas une information affirmée d'une information niée. D'où la relecture manuelle.
- **Pas de mémoire de conversation :** chaque question est traitée seule.
- **Un plafond journalier en mémoire,** remis à zéro à chaque redémarrage du serveur.

**Pistes, à juger avec le même jeu de questions :**
1. **Une recherche hybride** (BM25 + embeddings), pour retrouver les passages qui expriment la même idée avec d'autres mots.
2. **Un reclassement** (*reranking*) des meilleurs candidats par un modèle.
3. **Un jeu d'évaluation plus large,** avec des questions de vrais utilisateurs.
4. **Une recollecte automatique** des fiches, avec détection des changements.

## Données et licence

- **Source :** fiches pratiques de [service-public.gouv.fr](https://www.service-public.gouv.fr) (Direction de l'information légale et administrative), consultées le 17/11/2026. L'URL de chaque fiche figure en tête de son fichier dans [documents/](documents/).
- **Licence des données :** [Licence Ouverte / Open Licence Etalab 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/). Les textes sont repris fidèlement, sans modification de fond, avec mention de la source et de la date.
- **Licence du code :** [MIT](LICENSE). Elle ne s'applique pas aux fiches de documents/, qui restent sous Licence Ouverte Etalab 2.0.
- Ce projet n'est ni affilié à service-public.gouv.fr ni à France Travail.

## Installation en local

Il faut Python 3.10 ou plus récent et une clé API Anthropic.

```bash
git clone https://github.com/Zbiboo/assistant-rag-chomage.git
cd assistant-rag-chomage
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env          # puis écrire sa clé après ANTHROPIC_API_KEY=
.venv/bin/python scripts/decouper.py      # crée data/morceaux.jsonl
```

Utilisation :

```bash
.venv/bin/python app.py                                   # page web : http://127.0.0.1:7860
.venv/bin/python scripts/demander.py "ma question"        # en ligne de commande
.venv/bin/python scripts/rechercher.py "rupture conventionnelle"   # recherche seule, gratuite
.venv/bin/python eval/run_eval.py --recherche-seule       # évaluation de la recherche (quasi gratuite)
```

Tous les réglages se changent sans toucher au code, par exemple : `MODELE_REPONSE=claude-sonnet-5-5 .venv/bin/python app.py`.

## Mise en ligne

L'application est prévue pour **Hugging Face Spaces** (SDK Gradio). L'en-tête en haut de ce fichier est la configuration du Space. La clé API est placée dans les Secrets du Space, jamais dans les fichiers. Le dossier `data/` n'est pas versionné : l'application le recrée au démarrage à partir de `documents/`.
