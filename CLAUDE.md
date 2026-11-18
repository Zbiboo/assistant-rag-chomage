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
Python 3.15, venv .venv/ (paquets : anthropic, python-docx). Documents Markdown (documents/, 14 fiches) → découpage (scripts/decouper.py, data/morceaux.jsonl, 308 morceaux) → BM25 maison (scripts/rechercher.py) sur la question d'origine + la reformulation → 5 extraits dédoublonnés (les copies identiques sont fusionnées, avec la liste des sections où le texte apparaît) → réponse sourcée [n] (scripts/demander.py, classe Assistant, sans affichage, réutilisable par l'évaluation et l'interface). Modèle : Haiku (claude-haiku-5-5) pour les deux appels, choisi grâce à l'évaluation. Réglages (modèles, effort, max_tokens, longueur max de question, nombre d'extraits, prix) dans scripts/config.py, chacun remplaçable par une variable d'environnement du même nom.

À savoir : data/ est ignoré par Git. Il faut relancer `scripts/decouper.py` pour recréer data/morceaux.jsonl (à prévoir aussi pour l'hébergement).

## Commandes
- Poser une question : `.venv/bin/python scripts/demander.py "ma question"`
- Recherche seule (gratuit) : `.venv/bin/python scripts/rechercher.py "ma requête"`
- Évaluation : `.venv/bin/python eval/run_eval.py` (`--recherche-seule` ne coûte presque rien ; `--recalculer` renote sans refaire d'appels). La section « Analyse et recommandation » de eval/resultats.md est écrite à la main et conservée par le script.

## État d'avancement
- Fait : collecte (14 fiches), découpage, recherche BM25, génération, dépôt Git/GitHub sécurisé (github.com/Zbiboo/assistant-rag-chomage), réduction des coûts, évaluation (eval/), fusion des doublons.
- Résultat de l'évaluation (15 questions : 13 sur le corpus, 2 hors corpus, Haiku) : 10/13 questions complètes (11/13 après lecture, q12 étant un faux négatif) ; 35/39 éléments clés dans les extraits avec reformulation (27/39 sans) et 35/39 dans les réponses ; 0 citation invalide ; 2/2 « je ne sais pas » hors corpus ; environ 5 s et 0,001 $ par question. Sonnet donne la même qualité pour 13 fois plus cher.
- Échecs restants : q02 (montant), q06 (rupture conventionnelle et chômage), q08 en partie. Ils viennent de la recherche, pas du modèle.
- Cause d'échec restante identifiée : reformulation trop longue (12-13 mots-clés), qui dilue la recherche. Les embeddings ne sont pas justifiés à ce stade.

## Prochaines étapes (dans l'ordre)
1. Essai rapide (1 h maximum) : limiter la reformulation à environ 5 mots-clés, relancer l'évaluation, et garder le changement seulement s'il améliore le résultat.
2. Ajouter au jeu d'évaluation 5 questions écrites par moi avec mes propres mots.
3. Interface web Gradio (app.py) qui réutilise la classe Assistant : sources cliquables, avertissement "ne remplace pas un conseiller France Travail" avec la date des fiches, questions d'exemple, lien vers le dépôt GitHub, protections anti-abus (longueur max déjà en place, limite de dépense dans la console Anthropic). Gradio est à installer : me demander d'abord.
4. Mise en ligne sur Hugging Face Spaces : clé dans les Secrets du Space, morceaux recréés au démarrage ou fournis, test du lien public.
5. Présentation : README du dépôt (démarche, architecture, résultats de l'évaluation, limites), texte de présentation pour les recruteurs.
