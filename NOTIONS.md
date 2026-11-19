# Assistant RAG chômage : guide du projet

Ce guide explique, étape par étape, comment est construit l'assistant qui répond aux questions sur le chômage et France Travail en citant ses sources officielles. Chaque notion est expliquée simplement, avec le fichier du projet où la voir.

## Où en est le projet

| Étape | Ce qu'elle fait | État |
|---|---|---|
| 0. Collecter | Télécharger 14 fiches de service-public.gouv.fr et les convertir en Markdown fidèle | Terminé |
| 1. Découper | Couper les fiches en 308 morceaux, chacun avec son fil de titres et sa source | Terminé |
| 2. Chercher | Retrouver les morceaux pertinents pour une question (BM25, codé à la main) | Terminé |
| 3. Répondre | Claude reformule la question, puis répond à partir des morceaux en citant ses sources | Terminé |
| 4. Publier le code | Dépôt Git sécurisé (clé jamais versionnée), puis GitHub | Terminé |
| 5. Réduire les coûts | Modèles moins chers configurables, limites de taille, coût affiché | Terminé |
| 6. Évaluer | 20 questions types : mesurer la recherche et la qualité des réponses | Terminé |
| 7. Interface web | Une page Gradio avec sources cliquables et protections anti-abus | Terminé |
| 8. Mettre en ligne | Hébergement sur Hugging Face Spaces (ZeroGPU), testable par un lien | En attente : compte Hugging Face trop récent, possible vers le 19/12/2026 |
| 9. Présenter | README du dépôt, texte de présentation pour les recruteurs | Terminé |

Objectif de départ : une V1 en ligne avant le samedi 28 novembre 2026, pour quelques euros d'API au maximum. La mise en ligne est décalée vers le 19 décembre 2026 (voir l'étape 8) ; tout le reste est prêt.

## Comment ça marche

Le principe du **RAG** (Retrieval-Augmented Generation, « génération augmentée par la recherche ») : l'assistant ne répond pas « de mémoire ». Il cherche d'abord les passages pertinents dans une base de documents, puis les donne au modèle d'IA pour qu'il réponde en les citant. La qualité des réponses dépend donc directement de la qualité des documents.

Ce qui se passe quand on pose une question :

1. **Reformuler** : Claude traduit la question dans le vocabulaire des fiches officielles (« combien de temps serai-je payé » devient « durée de versement de l'ARE »).
2. **Chercher** : l'algorithme BM25 trouve les 8 morceaux de fiches les plus proches (sans doublons).
3. **Répondre** : Claude reçoit ces 8 extraits et répond uniquement à partir d'eux, en citant [1], [2]…
4. **Afficher** : la réponse, la liste des sources (titre, section, URL, date de vérification) et le coût de la question.

## Lancer l'assistant

Toutes les commandes se tapent dans le terminal, depuis le dossier du projet.

```
.venv/bin/python scripts/demander.py "J'ai 56 ans, combien de temps serai-je indemnisé ?"
.venv/bin/python scripts/demander.py
.venv/bin/python app.py
.venv/bin/python scripts/rechercher.py "contester une radiation"
.venv/bin/python scripts/collecter_documents.py
.venv/bin/python scripts/decouper.py
.venv/bin/python scripts/generer_guide.py
```

Dans l'ordre : poser une question ; mode interactif (plusieurs questions, Entrée pour quitter) ; lancer la page web (puis ouvrir http://127.0.0.1:7860 dans le navigateur) ; tester la recherche seule, sans IA ni coût ; re-télécharger les fiches ; refaire le découpage ; régénérer ce guide au format Word.

## Le projet en 5 minutes (récap pour l'entretien)

Cette partie résume tout le projet, pour le réviser et pouvoir le raconter. Le détail de chaque notion est dans les étapes plus bas.

### L'histoire en une phrase
J'ai construit, sans framework, un assistant qui répond aux questions sur le chômage en s'appuyant uniquement sur 14 fiches officielles. Il cite ses sources et sait dire « je ne sais pas ». Chaque choix technique a été mesuré avec une évaluation que j'ai écrite.

### Les 6 grandes étapes
1. **Collecter** : télécharger 14 fiches de service-public.gouv.fr et les convertir en Markdown, mot pour mot. Si les documents sont mauvais, l'assistant le sera aussi.
2. **Découper** : couper les fiches en 308 morceaux. Chacun garde son « fil de titres » (« Vous avez 55 ou 56 ans > Montant brut »), sans quoi « le montant est de 57 % » ne veut rien dire.
3. **Chercher** : BM25 codé à la main, qui note chaque morceau selon les mots en commun avec la question. Les mots rares comptent plus, les morceaux longs sont un peu pénalisés.
4. **Répondre** : deux appels à Claude. Le premier reformule la question en vocabulaire officiel, le second répond à partir des 8 meilleurs extraits, en citant [n].
5. **Évaluer** : 20 questions avec les éléments de réponse attendus. Chaque changement est jugé avant / après avec le même contrôle.
6. **Montrer** : une page web Gradio protégée (clé côté serveur, plafond par jour, erreurs polies) et un README.

### Les chiffres à retenir
- 14 fiches, 308 morceaux, dont 195 doublons fusionnés.
- Reformulation : 68 % → 92 % des éléments attendus présents dans les extraits.
- 8 extraits au lieu de 5 : 35,3 → 37 sur 39 (mesuré 3 fois).
- 13 questions sur 18 entièrement correctes, 0 citation inventée, 2 « je ne sais pas » sur 2 pour les questions hors sujet.
- Haiku au lieu de Sonnet : même qualité, 13 fois moins cher. Environ 0,0013 $ et 6 secondes par question.

### Les questions probables en entretien
- **Pourquoi ne pas utiliser LangChain ?** Pour comprendre chaque brique et pouvoir l'expliquer. Le projet est petit : un framework aurait caché la logique sans rien apporter.
- **Pourquoi pas d'embeddings ni de base vectorielle ?** 308 morceaux, c'est petit. L'évaluation montrait que les échecs venaient surtout des doublons et du vocabulaire, que le dédoublonnage et la reformulation ont corrigés en grande partie. Les embeddings sont la prochaine piste, sous forme de recherche hybride, et seront jugés avec le même jeu de questions.
- **Comment évitez-vous les hallucinations ?** Une consigne stricte (répondre uniquement à partir des extraits, citer chaque information, dire quand on ne sait pas), le contrôle des citations par l'évaluation, et des questions hors sujet pour vérifier que l'assistant s'abstient.
- **Comment avez-vous choisi le modèle ?** Par la mesure : Haiku et Sonnet sur les mêmes questions donnent la même qualité, à un prix 13 fois plus bas pour Haiku. Les erreurs venaient de la recherche, qu'un plus gros modèle ne corrige pas.
- **Une idée qui n'a pas marché ?** Raccourcir la reformulation à 5 mots-clés. L'hypothèse a été testée sur 3 passages (34,7 contre 35,3 sur 39), puis rejetée. La vraie cause, trouvée en lisant le classement, était les sigles ARE et SJR.
- **Comment protégez-vous la clé et le budget ?** La clé est dans une variable d'environnement côté serveur, jamais dans Git ni dans la page. La page a un plafond global de questions par jour, une question limitée à 500 caractères, et la console Anthropic a une limite de dépense.
- **Les limites ?** La recherche par mots-clés rate quand le vocabulaire est très différent. Le corpus est petit et daté. L'évaluation compte 20 questions, et son contrôle par mots ne voit pas les négations.
- **Qu'est-ce que vous feriez ensuite ?** Une recherche hybride, un jeu de questions plus grand venant de vrais utilisateurs, et une recollecte automatique des fiches.

## Étape 0 : collecter les documents

### Web scraping (extraction de pages web)
Télécharger le HTML d'une page, puis en extraire le contenu utile en retirant menus, boutons et pieds de page.
- `urllib.request` (bibliothèque standard Python) télécharge la page.
- `html.parser.HTMLParser` lit le HTML balise par balise : on réagit à chaque ouverture (`handle_starttag`), fermeture (`handle_endtag`) et morceau de texte (`handle_data`).

→ Voir : [scripts/collecter_documents.py](scripts/collecter_documents.py)

### Bibliothèque standard ou paquets externes
Python est livré avec des modules prêts à l'emploi (`urllib`, `html`, `re`…). Pour la collecte, on a évité BeautifulSoup (un paquet externe) pour ne rien installer.

### Expressions régulières (`re`)
Un petit langage pour chercher des motifs dans du texte. Par exemple `r"chapitre(\d+)"` récupère le numéro d'un chapitre.

→ Voir : [scripts/collecter_documents.py](scripts/collecter_documents.py)

### Front matter
Le bloc entre deux lignes `---` en haut d'un fichier Markdown. Il contient des métadonnées lisibles par un programme (titre, source, date de consultation), séparées du texte. C'est lui qui permet à l'assistant d'afficher la source d'un passage.

→ Voir : l'en-tête de [documents/01-conditions-are.md](documents/01-conditions-are.md)

### Titres Markdown
`#`, `##`, `###`… marquent la hiérarchie des sections. Le découpage s'appuie dessus : il ne faut donc pas sauter de niveau (passer de ## à #####).

→ Voir : `blocs_vers_markdown` dans [scripts/collecter_documents.py](scripts/collecter_documents.py)

### Vérifier la fidélité
Sur un sujet juridique, le texte doit être exactement celui de la page officielle. Un script compare chaque paragraphe produit au texte brut de la page : aucun mot ajouté ni modifié.

## Étape 1 : découper en morceaux

### Le découpage (« chunking »)
On coupe chaque document à chaque titre : un morceau correspond à une section. Une section trop longue (plus de 300 mots) est coupée entre deux paragraphes. Les morceaux font environ 93 mots en médiane.

→ Voir : [scripts/decouper.py](scripts/decouper.py), résultat dans `data/morceaux.jsonl`

### Le fil de titres
Chaque morceau garde la suite des titres qui le contiennent, par exemple « Vous avez 55 ou 56 ans > Quel est le montant de l'ARE ? ». Sans ce fil, un passage comme « 57 % du salaire » ne dit plus à qui il s'applique.

### Les étiquettes
Un titre de tableau (« Tableau - … ») ou un label « **À savoir** » n'a pas de sens seul. Le découpage les garde collés au bloc qui suit ; sinon un tableau peut arriver sans son titre, et le modèle ne sait plus à quoi il s'applique.

→ Voir : `est_une_etiquette` dans [scripts/decouper.py](scripts/decouper.py)

### JSON Lines (.jsonl)
Un fichier texte où chaque ligne est un objet JSON complet. Pratique pour stocker une liste d'éléments qu'on relit ligne par ligne.

→ Voir : `data/morceaux.jsonl`

## Étape 2 : chercher les bons passages

### BM25, la recherche par mots-clés
L'algorithme classique des moteurs de recherche. Un morceau gagne des points pour chaque mot de la question qu'il contient, en tenant compte de trois choses :
- **la rareté du mot (IDF)** : « démission » compte plus que « allocation », présent partout ;
- **la saturation** : répéter un mot 10 fois ne rapporte pas 10 fois plus ;
- **la longueur** : un long texte est un peu pénalisé, car il contient « par hasard » plus de mots.

→ Voir : classe `IndexBM25` dans [scripts/rechercher.py](scripts/rechercher.py)

### Normaliser les mots
Avant de comparer, on met en minuscules, on retire les accents, on enlève les « mots vides » (le, de, vous…) et on ne garde que les 6 premières lettres (« troncature »), pour que « démissionne » et « démission » deviennent le même mot : `demiss`.

→ Voir : fonction `mots` dans [scripts/rechercher.py](scripts/rechercher.py)

### La limite de la troncature
Couper à 6 lettres est une méthode « aveugle » : elle ne connaît pas la grammaire. Elle fait deux types d'erreurs, vérifiées sur notre fonction `mots` :
- **Elle confond des mots différents** : « formation », « format » et « formateur » deviennent tous `format`. De même, « prestation » et « prestataire » deviennent `presta`. Une question sur un « format de document » remonterait des passages sur la formation.
- **Elle sépare des mots de même famille** : « droit » et « droits » restent différents (mots trop courts pour être coupés), comme « radiation » (`radiat`) et « radié » (`radie`), ou « salarié » (`salari`) et « salaire » (`salair`).

**La solution standard est un « stemmer »** (racinisateur), par exemple **Snowball**, le plus utilisé pour le français. Au lieu de couper à une longueur fixe, il retire les terminaisons connues de la langue (pluriels, -ation, -ement, -ité…) selon des règles. Il traite donc mieux les pluriels et les mots de même famille. Aucun outil n'est parfait : un stemmer peut lui aussi rapprocher deux mots de sens différents. Il faudrait le comparer à la troncature avec notre évaluation. Il s'installe avec un petit paquet Python (`snowballstemmer`) ; on ne l'a pas fait pour garder zéro dépendance à cette étape.

### Les réglages de BM25 : k1 et b
BM25 a deux réglages. On utilise les valeurs classiques des ouvrages de référence :
- **k1 = 1,5** règle la **saturation**, c'est-à-dire l'effet d'un mot répété. Avec k1 = 0, être présent une fois ou dix fois revient au même. Plus k1 est grand, plus la répétition compte. Les valeurs habituelles vont de 1,2 à 2 (Elasticsearch utilise 1,2 par défaut).
- **b = 0,75** règle la **pénalité de longueur**. Avec b = 0, la longueur d'un morceau ne compte pas ; avec b = 1, la pénalité est maximale. 0,75 est la valeur standard, la même qu'Elasticsearch.

Ces valeurs n'ont pas été ajustées pour notre corpus. On pourrait les tester avec l'évaluation (`--recherche-seule`, qui ne coûte presque rien).

→ Voir : `K1` et `B` en haut de [scripts/rechercher.py](scripts/rechercher.py)

### Pourquoi 8 extraits, 300 mots, 6 lettres ?
300 mots et 6 lettres sont des **choix raisonnables faits à la main au début du projet, pas des valeurs mesurées**. Le nombre d'extraits, lui, a été mesuré. Voici le raisonnement :
- **8 extraits** : c'est un compromis. Trop peu, et on risque de rater l'information. Trop, et on paie plus de tokens et on noie le modèle sous des passages hors sujet. Le projet a commencé avec 5, un choix fait à la main. Le passage à 8 a été **mesuré** (voir « Tester une hypothèse » à l'étape 6) : la recherche devient meilleure et plus stable, pour environ 5 600 tokens envoyés au lieu de 3 700, soit +20 % de coût (0,0012 $ par question).
- **300 mots maximum par morceau** : la plupart des sections sont plus courtes (93 mots en médiane), donc la limite ne coupe que 24 sections sur 274. Elle évite d'envoyer un très long morceau dont seule une phrase est utile.
- **6 lettres** : testé à la main sur « démissionne » et « démission » (les deux donnent `demiss`). Assez long pour garder le sens de la plupart des mots, assez court pour rapprocher les terminaisons. Voir ses limites plus haut.

Avec l'évaluation, on peut maintenant comparer d'autres valeurs (3 ou 8 extraits, 5 ou 7 lettres…) au lieu de deviner.

→ Voir : `NB_EXTRAITS` dans [scripts/config.py](scripts/config.py), `MOTS_MAX` dans [scripts/decouper.py](scripts/decouper.py), `LETTRES_GARDEES` dans [scripts/rechercher.py](scripts/rechercher.py)

### La limite : les synonymes
« Combien de temps serai-je indemnisé ? » ne trouve pas « durée de versement », car aucun mot n'est commun. Deux solutions : la recherche **sémantique** (des « embeddings » comparent le sens des phrases) ou la **reformulation** de la question par le modèle. Le projet utilise la reformulation (étape 3).

## Étape 3 : faire répondre Claude

### Deux appels à l'API
Pour chaque question, le script appelle Claude deux fois :
1. **Reformulation de la requête** : traduire la question en vocabulaire officiel, pour aider BM25.
2. **Réponse ancrée** : répondre à partir des 8 meilleurs extraits numérotés, en citant [1], [2]…

→ Voir : [scripts/demander.py](scripts/demander.py)

### La recherche utilise la question d'origine ET la reformulation
BM25 cherche avec la question telle qu'elle a été posée, **suivie** des mots-clés de la reformulation : `chercher(f"{question} {mots_cles}")`.

**Le risque si on cherchait avec la reformulation seule** : tout reposerait sur le modèle. S'il oublie un détail de la question (l'âge « 56 ans », « agent public »…) ou s'il la comprend de travers, la recherche part dans la mauvaise direction, et on ne peut plus rattraper l'erreur. Garder la question d'origine assure un filet de sécurité : ses mots comptent toujours.

**Un effet à connaître** : un mot présent dans la question ET dans les mots-clés compte **double** dans le score. La fonction `score` parcourt tous les mots de la requête, répétitions comprises. C'est plutôt utile, car ce mot est confirmé deux fois. Mais une reformulation trop longue a l'effet inverse : beaucoup de mots-clés secondaires diluent la question. C'est ce qui a fait échouer la question sur le montant dans l'évaluation (13 mots-clés, dont « revenus d'activité », qui a attiré la fiche sur le cumul).

→ Voir : méthode `chercher` dans [scripts/demander.py](scripts/demander.py), méthode `score` dans [scripts/rechercher.py](scripts/rechercher.py)

### Le prompt système (la consigne)
Le paramètre `system` donne à Claude son rôle et ses règles, séparés de la question. Ici : ne jamais utiliser ses propres connaissances, citer chaque information, dire « je ne sais pas » plutôt que deviner, et signaler quand la réponse dépend d'une situation non précisée (âge, date de fin de contrat…).

→ Voir : `CONSIGNE_REPONSE` dans [scripts/demander.py](scripts/demander.py)

### Hallucination et ancrage
Un modèle peut inventer une réponse plausible mais fausse : on dit qu'il « hallucine ». Le RAG réduit ce risque en ancrant la réponse dans des extraits, et les citations permettent de vérifier. Test fait : à la question « montant du RSA » (absent des documents), l'assistant répond qu'il ne trouve pas l'information au lieu d'inventer un chiffre.

### Tokens et coût
L'API facture au **token**, un morceau de mot (environ 3/4 de mot en français). Une question envoie environ 5 600 tokens (surtout les 8 extraits) et en reçoit 1 000 à 1 500, réflexion du modèle comprise. Le coût exact dépend du modèle (voir plus bas). `response.usage` donne les chiffres exacts.

### L'effort
`output_config={"effort": ...}` règle combien Claude réfléchit avant de répondre : `low` pour la reformulation (tâche simple), `medium` pour la réponse (réglable dans config.py). Plus d'effort donne une meilleure qualité possible, mais c'est plus lent et plus cher.

### Choisir le modèle selon le coût
Anthropic propose plusieurs tailles de modèles. Prix vérifiés le 17/11/2026 dans la documentation officielle, en dollars par million de tokens (entrée / sortie) :

| Modèle | Identifiant | Prix |
|---|---|---|
| Haiku 5.5 | claude-haiku-5-5 | 0,10 / 0,50 |
| Sonnet 5.5 | claude-sonnet-5-5 | 2 / 10 |
| Opus 5.5 | claude-opus-5-5 | 4 / 20 |

Avec Haiku pour les deux appels, une question coûte environ 0,001 $ (près de 900 questions pour 1 $), contre 0,04 $ avec Opus : 34 fois moins cher. La qualité sera mesurée à l'étape « Évaluer ».

### La configuration (config.py)
Tous les réglages sont regroupés dans un seul fichier : modèles, effort, limites, prix. Chaque réglage peut être changé sans toucher au code, avec une variable d'environnement du même nom :

```
MODELE_REPONSE=claude-sonnet-5-5 .venv/bin/python scripts/demander.py "ma question"
```

→ Voir : [scripts/config.py](scripts/config.py)

### Limiter les coûts et les abus
- **max_tokens** plafonne la longueur de ce que produit le modèle, réflexion comprise : 1 000 tokens pour la reformulation, 2 500 pour la réponse. Si la limite est atteinte, la réponse le signale.
- **Longueur maximale d'une question** : 500 caractères. Au-delà, la question est refusée avant tout appel payant.
- **Limite de dépense mensuelle** : à régler dans la console Anthropic. C'est le filet de sécurité ultime, même en cas de bug.

### Séparer le moteur de l'affichage
`demander.py` contient d'un côté le **moteur** (la classe `Assistant`, qui renvoie la réponse, les extraits et les coûts sans rien afficher), de l'autre l'**affichage** en ligne de commande. L'évaluation et la page web réutilisent le même moteur : le code n'est écrit qu'une fois.

→ Voir : classe `Assistant` dans [scripts/demander.py](scripts/demander.py)

## Étape 6 : évaluer

### Pourquoi évaluer
Sans mesure, on ne sait pas si une modification améliore ou dégrade l'assistant. Un **jeu d'évaluation** est une liste de questions dont on connaît la bonne réponse. On le relance après chaque changement, comme un examen blanc.

→ Voir : [eval/questions.json](eval/questions.json), [eval/run_eval.py](eval/run_eval.py), [eval/resultats.md](eval/resultats.md)

### Ce qu'on mesure
- **La recherche** : les informations utiles sont-elles dans les extraits donnés au modèle ? Sans elles, même le meilleur modèle ne peut pas bien répondre.
- **La réponse** : contient-elle les éléments clés attendus (« 685 jours », « 15 jours »…) ?
- **Les citations** : chaque [n] renvoie-t-il à un extrait réellement fourni ? Une citation inventée serait grave.
- **L'honnêteté** : aux questions hors sujet (retraite, APL), répond-il « je ne sais pas » ?

### Critère indulgent ou strict
« La bonne fiche est parmi les extraits » donnait 100 % : trop indulgent, car la fiche peut être là sans le bon passage. Le critère strict, « les éléments clés sont dans le texte des extraits », a montré le vrai effet de la reformulation : de 64 % à 90 %.

### Faux négatifs : lire les réponses
Un contrôle automatique « mot pour mot » se trompe : « tribunal administratif » au lieu de « juge administratif » était compté comme une erreur alors que c'est juste. Il faut lire les réponses en échec avant de conclure, puis corriger le contrôle. L'option `--recalculer` refait la notation sans repayer les appels à l'API.

### Non-déterminisme
Le modèle ne répond pas exactement pareil à chaque fois : la reformulation, donc les extraits, peuvent varier d'une exécution à l'autre. Il faut regarder les tendances, pas un point isolé.

### Le résultat : Haiku suffit
Haiku et Sonnet obtiennent la même qualité sur ce jeu de questions, mais Haiku coûte 13 fois moins cher (≈ 0,0009 $ contre 0,012 $ par question). Les erreurs restantes viennent de la recherche, pas du modèle : un modèle plus cher n'y changerait rien.

### Les doublons, et leur correction
63 % des morceaux ont un texte identique à un autre, car les fiches répètent le même texte pour chaque tranche d'âge et pour le privé comme le public. Ils occupaient plusieurs des 5 places d'extraits (8 aujourd'hui).

**Correction (18/11/2026) : fusionner plutôt que supprimer.** La recherche ne garde qu'un exemplaire de chaque texte, mais l'extrait retenu liste toutes les sections où il apparaît. Supprimer simplement les copies aurait été dangereux : le modèle aurait cru qu'une règle ne vaut que pour « moins de 55 ans » alors qu'elle vaut pour tous les âges.

**Résultat mesuré : gain modeste.** Les réponses passent de 34 à 35 éléments clés sur 39, et le nombre de questions complètes ne change pas (10/13). La cause restante est une reformulation trop longue, qui dilue la recherche. Les embeddings ne sont toujours pas justifiés.

→ Voir : méthode `chercher` dans [scripts/rechercher.py](scripts/rechercher.py), `formater_extraits` dans [scripts/demander.py](scripts/demander.py)

### Comparer « avant / après » avec le même instrument
Pour savoir si une modification aide, il faut mesurer avant et après avec **le même contrôle**. Ici, le contrôle avait été amélioré entre-temps (mots entiers, variante trop vague retirée). On a donc renoté l'ancienne exécution avec le nouveau contrôle, sans repayer, grâce aux réponses gardées dans Git. Sinon, on aurait comparé des chiffres mesurés différemment.

### Faux positifs
L'inverse des faux négatifs : le contrôle compte « trouvé » un élément qui ne devrait pas l'être. Deux cas rencontrés :
- un mot court trouvé à l'intérieur d'un autre (« are » dans « déclarer »), corrigé en cherchant des mots entiers ;
- un élément cité dans une phrase négative (« les extraits ne parlent pas de l'allocation chômage »). Ce cas reste une limite du contrôle automatique : d'où l'importance de lire les réponses.

### Tester une hypothèse, et accepter qu'elle soit fausse
Hypothèse du 18/11 : « la reformulation est trop longue (11 mots-clés), elle dilue la recherche ». Test du 19/11 : limiter à 5 mots-clés. Résultat : aucune amélioration (34,7/39 contre 35,3/39). **Le changement a été abandonné**, comme prévu : on ne garde que ce qui améliore la mesure.

L'analyse des scores BM25 (gratuite) a ensuite montré la vraie cause pour la question sur le montant : le bon passage est écrit avec des **sigles** (« ARE », « SJR ») et sans le mot « calcul ». Une autre fiche, qui contient « est calculé d'après la formule », passait donc devant. Le bon passage arrivait 8e, juste hors des 5 extraits.

### Répéter les mesures
La reformulation varie d'un appel à l'autre, donc les extraits aussi. Une seule mesure peut tromper : avec 5 extraits, trois passages ont donné 34, 37 puis 35 éléments sur 39. On mesure donc **3 fois avant et 3 fois après**, et on compare les moyennes et la stabilité :

| Réglage | 3 passages | Moyenne |
|---|---|---|
| 5 extraits | 34 / 37 / 35 | 35,3/39 |
| 5 extraits + reformulation courte | 34 / 35 / 35 | 34,7/39 |
| **8 extraits (retenu)** | 37 / 37 / 37 | **37,0/39** |

Avec 8 extraits, le résultat est meilleur et ne varie plus. Les réponses passent de 35 à 36 éléments clés sur 39.

### Ce qui reste hors de portée des mots-clés
Deux questions échouent dans tous les essais : q06 (« aurai-je droit au chômage après une rupture conventionnelle ? ») et q08 (« qui verse l'allocation d'un fonctionnaire ? »). Le bon passage existe, mais avec d'autres mots que la question. C'est la limite naturelle de BM25. La piste suivante serait une recherche « par le sens » (embeddings), à n'envisager que si de nouvelles questions montrent le même problème.

### Des questions écrites par un vrai utilisateur
Les 15 premières questions avaient été écrites en connaissant les fiches, donc avec leur vocabulaire. Cinq questions écrites « comme on parle » (« je me suis fait virer », « j'ai zappé de m'actualiser ») ont révélé deux échecs de recherche sur cinq. C'est le vrai test : un utilisateur ne connaît pas les mots des fiches.

### Faux positif sur une négation, constaté
Pour q20, la réponse disait « les extraits ne disent rien sur une rupture conventionnelle avec un employeur public ». Le contrôle a compté « rupture conventionnelle » comme trouvé : 3 éléments sur 3, alors que la réponse passait à côté de l'essentiel. Seule la lecture l'a montré. Un score automatique se lit toujours avec les réponses sous les yeux.

### Un passage long est pénalisé
Le passage qui répondait à q20 est une liste de toutes les situations ouvrant droit à l'ARE : 168 mots, plus du double de la moyenne. BM25 pénalise la longueur (réglage b = 0,75), et « rupture conventionnelle » n'y est qu'une ligne parmi d'autres : le passage n'arrivait que 20e. Pistes possibles : découper les longues listes, ou une recherche par le sens.

### Bilan de la recherche, et la suite
Sur 18 questions du corpus, 5 échecs de recherche, tous dus à un écart de vocabulaire ou à un passage long. Dans ces 5 cas, l'assistant n'invente rien : il dit ce qui lui manque. Pour la V1, on garde BM25 et on documente la limite. Après la V1, la piste la plus prometteuse est une **recherche hybride** (BM25 + embeddings), à juger avec ce même jeu de 20 questions.

## Étape 7 : l'interface web

### Gradio
**Gradio** est une bibliothèque Python qui fabrique une page web à partir de quelques lignes de code : champs, boutons, zones de texte. Pas besoin d'écrire de HTML ni de JavaScript. Hugging Face Spaces, l'hébergeur prévu, sait la faire tourner directement.
- `gr.Blocks()` : la page, dans laquelle on empile les éléments dans l'ordre d'affichage.
- `gr.Textbox`, `gr.Button`, `gr.Markdown` : un champ de saisie, un bouton, un texte mis en forme.
- `gr.Examples` : des questions d'exemple ; un clic remplit le champ.
- `bouton.click(fonction, inputs=…, outputs=…)` : un **événement**. Quand on clique, Gradio appelle la fonction Python avec le contenu du champ et affiche ce qu'elle renvoie.

→ Voir : [app.py](app.py)

### Réutiliser le moteur, sans dupliquer
`app.py` ne contient que l'interface. Il appelle `Assistant.repondre()`, exactement comme la ligne de commande et l'évaluation. Une amélioration du moteur profite donc partout, et l'évaluation mesure bien ce que voient les visiteurs.

### Serveur et navigateur : où est la clé ?
Le code Python tourne sur le **serveur**. Le navigateur du visiteur ne reçoit que la page et les réponses, jamais la clé, qui reste dans une variable d'environnement du serveur. Test fait : la page, la configuration envoyée au navigateur et le journal du serveur ont été fouillés, et aucune clé n'y figure.

### Protections contre les abus
- **Longueur maximale** : 500 caractères, vérifiée avant tout appel payant (et bloquée dès la saisie dans le champ).
- **Plafond global par jour** : 100 questions par jour **pour tous les visiteurs ensemble** (réglage `QUESTIONS_MAX_PAR_JOUR`), soit au pire environ 0,13 $ par jour. Au-delà, un message clair invite à revenir le lendemain. Le compteur est en mémoire : il repart de zéro à minuit et à chaque redémarrage du serveur. C'est suffisant pour une démonstration.
- **Verrou (`threading.Lock`)** : deux visiteurs peuvent poser une question au même moment. Le verrou garantit qu'ils ne modifient pas le compteur en même temps, ce qui pourrait fausser le compte.
- **Erreurs de l'API** : un problème chez Anthropic (clé refusée, service saturé…) affiche un message poli au visiteur. Le journal du serveur ne note que le type d'erreur (par exemple `AuthenticationError 401`), sans détail sensible. La place réservée dans le compteur est rendue.
- **Limite de dépense** de 10 $ par mois dans la console Anthropic, sans recharge automatique : le filet de sécurité final.

→ Voir : `CompteurJournalier` et `repondre` dans [app.py](app.py)

### Comment la réponse arrive dans le navigateur
Quand on clique sur « Poser la question », le navigateur envoie la question (`queue/join`), puis **garde une connexion ouverte** (`queue/data`) sur laquelle le serveur envoie des nouvelles : « traitement commencé », la progression, et enfin la réponse. Cette technique s'appelle **SSE** (Server-Sent Events, « événements envoyés par le serveur »).

**Piège rencontré :** si l'on quitte la page pendant l'attente (lien du bas de page, « Run history », retour en arrière), le navigateur ferme cette connexion. Le serveur termine quand même son travail, donc l'appel à Claude est payé, mais la réponse est perdue. Gradio affiche alors « Connection errored out ».

**Comment on l'a trouvé :** en lançant le serveur avec un **journal des requêtes**, qui note chaque échange avec le navigateur. Il montrait que Safari coupait la connexion au bout de 5,4 secondes, au moment même où il ouvrait la page « Run history ». Le serveur, lui, n'avait aucune erreur. Leçon : quand « ça ne marche pas », il faut d'abord savoir **qui** coupe, le navigateur ou le serveur, avant de toucher au code.

### Afficher l'étape en cours (générateur)
Une réponse prend environ 10 secondes. Sans signe d'activité, on croit que c'est bloqué et on clique ailleurs. La zone de réponse affiche donc l'étape en cours (« ⏳ Étape 1 sur 3 · Je reformule votre question… », puis 2 et 3), remplacée ensuite par la réponse.

**Premier essai raté :** la barre de progression intégrée à Gradio (`gr.Progress()`) envoyait bien ses messages, mais elle restait invisible. Elle se superpose aux zones de résultat, or nos blocs de texte étaient vides, sans cadre et sans hauteur : la barre n'avait pas de place pour s'afficher. Plutôt que de retoucher une mise en page que je ne pouvais pas voir, on a choisi une solution visible à coup sûr : écrire l'étape directement dans la zone de réponse.

**L'outil : le générateur.** Une fonction normale renvoie un seul résultat (`return`). Un **générateur** en produit plusieurs, l'un après l'autre, avec `yield`. Gradio met la page à jour à chaque `yield`.
- `Assistant.repondre_par_etapes()` produit `("reformulation", None)`, `("recherche", None)`, `("redaction", None)`, puis `("fini", résultat)`. Le moteur annonce les étapes mais ne sait rien de l'affichage.
- `repondre()` dans `app.py` traduit chaque étape en texte affiché.
- `Assistant.repondre()` garde son comportement habituel (le résultat final seulement) : la ligne de commande et l'évaluation ne changent pas.

→ Voir : `repondre_par_etapes` dans [scripts/demander.py](scripts/demander.py), `ETAPES` et `repondre` dans [app.py](app.py)

### Raccourcis de rechargement
Dans Safari, **Cmd+R** recharge la page et **Cmd+Option+R** la recharge sans le cache. Attention : **Cmd+Maj+R**, qui sert à recharger dans Chrome et Firefox, ouvre le mode Lecteur dans Safari.

### La date des informations
La page affiche que les fiches ont été consultées le 17/11/2026, et chaque source donne sa date de vérification par service-public. Sur un sujet où les règles changent, l'utilisateur doit savoir de quand datent les informations.

### Compatibilité des versions de Python
Le Mac utilise Python 3.15, mais l'hébergeur peut proposer une version plus ancienne. Le code est vérifié avec Python 3.9 (`python3 -m py_compile`) : il n'utilise aucune syntaxe trop récente.

## Étape 8 : mettre en ligne (en attente)

### Héberger une application
Pour qu'un recruteur teste l'assistant par un simple lien, le code doit tourner sur un **serveur** allumé en permanence, pas sur le Mac. Un **hébergeur** fournit ce serveur. On lui envoie le code, il installe les paquets de requirements.txt, lance `app.py` et donne une adresse publique.

### Hugging Face Spaces
Un **Space** est un dépôt Git hébergé par Hugging Face, qui sait lancer une application Gradio. À chaque `git push` vers ce dépôt, le Space réinstalle et redémarre l'application. La clé API se range dans les **Secrets** du Space (Settings). Elle y est lue comme une variable d'environnement, exactement comme avec `.env` en local. Un secret ne se relit pas une fois enregistré, et il n'est pas copié quand quelqu'un duplique le Space.

### L'en-tête du README : la configuration du Space
Hugging Face lit la configuration du Space dans un bloc YAML placé tout en haut de README.md, entre deux lignes `---` (le même principe que le front matter des fiches) :
- `sdk: gradio` et `sdk_version: 6.32.0` : Gradio, dans la même version qu'en local ;
- `python_version: 3.12.12` : l'une des deux seules versions acceptées par ZeroGPU ;
- `app_file: app.py` : le fichier à lancer.
GitHub affiche ce bloc sous forme d'un petit tableau en haut du README : c'est normal.

→ Voir : [README.md](README.md)

### Piège : les règles des hébergeurs changent
Le plan initial supposait un Space gratuit sur « CPU basic ». La documentation lue le 19/11/2026 dit autre chose : créer un Space Gradio demande maintenant l'abonnement PRO (9 $ par mois). Seule exception gratuite : 2 Spaces sur **ZeroGPU** (des GPU partagés), réservés aux comptes de plus de 30 jours avec un e-mail vérifié. Le compte a été créé le 19/11, d'où une mise en ligne vers le 19/12/2026. Alternatives écartées : PRO (9 $ par mois), et Render, gratuit mais qui s'endort après 15 minutes sans visite et met environ 1 minute à se réveiller.

Leçon : vérifier la documentation **actuelle** avant de bâtir un plan, et non ce qu'on croit savoir.

### Ce qui reste à vérifier le jour de la mise en ligne
- **Une app sans GPU sur ZeroGPU :** la documentation ne dit pas explicitement qu'une app qui n'utilise jamais de GPU fonctionne. C'est probable, car un GPU n'est attribué qu'aux fonctions qui le demandent, mais il faudra le tester.
- **Le dossier data/** n'est pas dans Git : `app.py` le recrée au démarrage à partir de `documents/`.
- **Le compteur de questions** repart de zéro à chaque redémarrage du Space.

## Étape 9 : présenter le projet

### Le README
Le README est la vitrine du dépôt : c'est la première chose qu'un recruteur lit sur GitHub. Il répond dans l'ordre à : à quoi ça sert, comment ça marche (schéma), pourquoi ces choix, est-ce que ça marche (chiffres de l'évaluation), est-ce que c'est sûr, quelles limites, comment l'installer. Un recruteur lit en diagonale : il faut des titres clairs, des chiffres et des limites assumées. Montrer qu'on connaît les faiblesses de son projet inspire plus confiance qu'un projet présenté comme parfait.

### Justifier un choix par une mesure
Chaque choix du README s'appuie sur un chiffre de l'évaluation : la reformulation (68 % → 92 %), les 8 extraits, Haiku plutôt que Sonnet. Les réglages pris sans mesure (k1 et b de BM25, 300 mots par morceau, troncature à 6 lettres) sont présentés comme des valeurs standard ou raisonnables, pas comme des optimums.

→ Voir : [README.md](README.md)

## Outils et environnement

### Environnement virtuel (venv) et pip
Un **venv** est un dossier (`.venv/`) qui contient une copie de Python et les paquets propres au projet, sans toucher au reste du Mac. Il utilise Python 3.15 (installé par Homebrew), car le Python du système (3.9) est trop ancien pour le paquet `anthropic`.
- Installer un paquet : `.venv/bin/python -m pip install nom-du-paquet`
- Lancer un script : `.venv/bin/python scripts/…`
- Ou bien `source .venv/bin/activate`, pour que `python` désigne ce Python-là dans le terminal courant.

### requirements.txt
La liste des paquets du projet, avec leur version exacte (`anthropic==2.10.0`). Elle permet de tout réinstaller à l'identique : `.venv/bin/python -m pip install -r requirements.txt`.

→ Voir : [requirements.txt](requirements.txt)

### Clé API, fichier .env et variables d'environnement
Une **clé API** est un mot de passe qui identifie ton compte (et ta facture) auprès d'Anthropic. Elle ne doit jamais être écrite dans le code ni publiée.
- Elle est rangée dans `.env` (une ligne `ANTHROPIC_API_KEY=…`), un fichier lisible par ton seul compte.
- Au démarrage, `charger_env()` copie cette ligne dans les **variables d'environnement** du programme ; le paquet `anthropic` y lit la clé tout seul.
- `.gitignore` liste les fichiers à ne jamais publier (`.env`, `.venv/`).
- Sur macOS, un fichier dont le nom commence par un point est caché dans le Finder (Cmd+Maj+point pour l'afficher).

→ Voir : [scripts/config.py](scripts/config.py), [.gitignore](.gitignore)

### Git : l'historique du projet
**Git** enregistre l'historique des fichiers du projet. Un **commit** est une photo de l'état des fichiers à un instant, avec un message qui dit ce qui a changé. On peut revenir à n'importe quelle photo.
- `git init` : transforme le dossier en dépôt Git (crée le dossier caché `.git/`).
- `git add` : choisit les fichiers à mettre dans la prochaine photo.
- `git status` : montre ce qui a changé et ce qui sera enregistré.
- `git commit -m "message"` : prend la photo.
- `git push` : envoie l'historique vers un serveur, comme **GitHub**, qui l'héberge en ligne et le rend visible (par exemple pour un recruteur).

### .gitignore et .env.example
`.gitignore` liste ce que Git doit ignorer : les secrets (`.env`), l'environnement Python (`.venv/`), les fichiers générés (`data/`, le guide Word) et ceux du système (`.DS_Store`). `.env.example` montre le **nom** de la variable attendue sans sa valeur : quelqu'un qui récupère le projet sait quoi créer, sans jamais voir ta clé.

Avant chaque publication, deux vérifications :
- `git check-ignore -v .env` doit répondre que `.env` est ignoré ;
- `git grep --cached -E "sk-ant-[A-Za-z0-9_-]{20,}"` ne doit rien trouver : les clés Anthropic commencent par ce préfixe, suivi d'une longue suite de caractères. (Chercher le seul préfixe trouverait aussi ce guide, qui en parle.)

Pourquoi c'est important : une clé publiée sur GitHub est repérée par des robots en quelques minutes, et quelqu'un peut alors dépenser ton crédit.

→ Voir : [.gitignore](.gitignore), [.env.example](.env.example)

### CLAUDE.md : la mémoire de l'assistant de code
Claude Code ne se souvient pas des sessions précédentes. Le fichier `CLAUDE.md` à la racine est lu automatiquement au début de chaque session : il résume l'objectif, les règles de travail, l'architecture, l'état d'avancement et les prochaines étapes. C'est une « fiche de passation », à tenir à jour comme ce guide. Il se distingue de `NOTIONS.md` : ce guide explique le projet à une personne qui apprend, `CLAUDE.md` donne à l'assistant le contexte pour continuer le travail.

→ Voir : [CLAUDE.md](CLAUDE.md)

### Générer ce guide en Word
Ce guide est écrit en Markdown (`NOTIONS.md`), puis converti en fichier Word par un script qui utilise le paquet `python-docx`. Il suffit de le relancer après chaque mise à jour.

→ Voir : [scripts/generer_guide.py](scripts/generer_guide.py)

## Pièges rencontrés

- **Changement d'adresse du site** : service-public.fr redirige vers service-public.gouv.fr ; on enregistre l'adresse finale.
- **Onglets et accordéons** : tout le texte est présent dans le HTML, simplement masqué ; on peut donc récupérer tous les onglets.
- **Texte d'interface caché** : les infobulles contiennent un texte fictif (« : titleContent ») rempli par JavaScript ; il faut les ignorer.
- **HTML mal fermé** : certaines cellules de tableau ne sont pas fermées ; le script remonte la pile des balises pour rester cohérent.
- **Réglementation qui change** : il existe des fiches « avant » et « après le 1er avril 2025 » ; il faut prendre celle en vigueur (F38881) et non l'ancienne (F14860).
- **Règles datées dans une même page** : certaines fiches ont des onglets « Avant / Depuis le 1er juin 2025 ». Le fil de titres de chaque morceau garde cette date, pour que l'assistant ne cite pas une règle périmée.
- **Un tableau séparé de son titre** : la coupure à 300 mots tombait parfois entre les deux ; corrigé grâce aux étiquettes (étape 1).
