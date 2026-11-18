# Assistant RAG chômage / France Travail

## Objectif
Assistant qui répond aux questions sur le chômage et France Travail en citant les fiches officielles de service-public.gouv.fr. Projet de portfolio pour une reconversion vers le développement IA. V1 EN LIGNE (testable via un lien par un recruteur) avant le samedi 28 novembre 2026. Budget API : quelques euros.

## Façon de travailler
- Toujours en français.
- Une étape à la fois : à la fin de chaque étape, résume, explique simplement (je dois pouvoir en parler en entretien), dis-moi ce que je dois faire à la main, puis attends mon "ok".
- Pas de LangChain ni de LlamaIndex, et rester simple.
- N'installe aucun paquet sans me le dire (uniquement dans .venv, à noter dans requirements.txt avec la version exacte).
- Sécurité : la clé API seulement dans .env (ignoré par Git) et dans les Secrets de l'hébergeur. Jamais dans le code, les commits, les logs ou côté navigateur. Avant chaque push : `git check-ignore -v .env` et `git grep --cached -E "sk-ant-[A-Za-z0-9_-]{20,}"` (ne doit rien trouver).
- Mets à jour NOTIONS.md (tableau d'avancement compris) quand une notion nouvelle apparaît ou qu'une étape se termine, puis régénère le Word : `.venv/bin/python scripts/generer_guide.py`.
- Toute modification de la recherche ou des consignes se juge avec l'évaluation, en comparant avant / après avec le même contrôle.

## Architecture
Python 3.15, venv .venv/ (paquets : anthropic, python-docx). Documents Markdown (documents/, 14 fiches) → découpage (scripts/decouper.py, data/morceaux.jsonl, 308 morceaux) → BM25 maison (scripts/rechercher.py) sur la question d'origine + la reformulation → 8 extraits dédoublonnés (les copies identiques sont fusionnées, avec la liste des sections où le texte apparaît) → réponse sourcée [n] (scripts/demander.py, classe Assistant, sans affichage, réutilisable par l'évaluation et l'interface). Modèle : Haiku (claude-haiku-5-5) pour les deux appels, choisi grâce à l'évaluation. Réglages (modèles, effort, max_tokens, longueur max de question, nombre d'extraits, prix) dans scripts/config.py, chacun remplaçable par une variable d'environnement du même nom.

À savoir : data/ est ignoré par Git. Il faut relancer `scripts/decouper.py` pour recréer data/morceaux.jsonl (à prévoir aussi pour l'hébergement).

## Commandes
- Poser une question : `.venv/bin/python scripts/demander.py "ma question"`
- Recherche seule (gratuit) : `.venv/bin/python scripts/rechercher.py "ma requête"`
- Évaluation : `.venv/bin/python eval/run_eval.py` (`--recherche-seule` ne coûte presque rien ; `--recalculer` renote sans refaire d'appels). La section « Analyse et recommandation » de eval/resultats.md est écrite à la main et conservée par le script.

## État d'avancement
- Fait : collecte (14 fiches), découpage, recherche BM25, génération, dépôt Git/GitHub sécurisé (github.com/Zbiboo/assistant-rag-chomage), réduction des coûts, évaluation (eval/), fusion des doublons.
- Résultat de l'évaluation (15 questions : 13 sur le corpus, 2 hors corpus, Haiku) : 10/13 questions complètes (11/13 après lecture, q12 étant un faux négatif) ; 35/39 éléments clés dans les extraits avec reformulation (27/39 sans) et 35/39 dans les réponses ; 0 citation invalide ; 2/2 « je ne sais pas » hors corpus ; environ 5 s et 0,001 $ par question. Sonnet donne la même qualité pour 13 fois plus cher.
- Échecs restants : q02 (montant), q06 (rupture conventionnelle et chômage), q08 en partie. Ils viennent de la recherche, pas du modèle.
- 19/11 : l'hypothèse « reformulation trop longue » a été testée et réfutée (5 mots-clés : 34,7/39 contre 35,3/39). Vraie cause pour q02 : vocabulaire (le passage utilise les sigles ARE/SJR, sans « calcul »), il arrivait 8e. Avec 8 extraits : 37/39 éléments dans les extraits sur 3 passages, 36/39 dans les réponses, 0,0012 $ par question. Restent q06 et q08 (limite des mots-clés). Les embeddings ne sont pas justifiés à ce stade.

- 19/11, jeu étendu à 20 questions (18 sur le corpus, dont 5 écrites par l'utilisateur) : 49/53 éléments dans les extraits avec reformulation, 13/18 questions vraiment complètes après lecture (le contrôle affiche 14 : q20 est un faux positif sur une négation), 0 citation invalide, 0,0013 $ par question. 5 échecs de recherche connus (q02/q16, q06, q08, q20) : écart de vocabulaire ou passage long. Recherche hybride à envisager APRÈS la V1.

## Prochaines étapes (dans l'ordre)
1. ~~Essai sur la reformulation~~ : fait le 19/11. 5 mots-clés n'apportent rien (abandonné). Passage à 8 extraits retenu (37/39 stable, contre 35,3/39).
2. ~~5 questions écrites par l'utilisateur~~ : faites le 19/11 (q16 à q20). 3/5 bonnes, 2 échecs de recherche (q16 montant, q20 fonctionnaire et rupture conventionnelle). L'assistant n'invente rien dans ces 2 cas.
3. Interface web Gradio (app.py) qui réutilise la classe Assistant : sources cliquables, avertissement "ne remplace pas un conseiller France Travail" avec la date des fiches, questions d'exemple, lien vers le dépôt GitHub, protections anti-abus (longueur max déjà en place, limite de dépense dans la console Anthropic). Gradio est à installer : me demander d'abord.
4. Mise en ligne sur Hugging Face Spaces : clé dans les Secrets du Space, morceaux recréés au démarrage ou fournis, test du lien public.
5. Présentation : README du dépôt (démarche, architecture, résultats de l'évaluation, limites), texte de présentation pour les recruteurs.
