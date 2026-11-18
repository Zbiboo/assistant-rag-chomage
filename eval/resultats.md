# Résultats de l'évaluation

15 questions (13 sur le corpus, 2 hors corpus). Reformulation : claude-haiku-5-5. Extraits par question : 8.

## Recherche : la bonne fiche est-elle parmi les extraits ?

| Méthode | Bonne fiche parmi les extraits | Éléments clés présents dans les extraits | Questions avec tous leurs éléments |
|---|---|---|---|
| BM25 sur la question brute | 13/13 (100 %) | 30/39 (77 %) | 8/13 |
| BM25 + reformulation | 13/13 (100 %) | 36/39 (92 %) | 10/13 |

## Réponses : comparaison des modèles

| | claude-haiku-5-5 |
|---|---|
| Éléments clés trouvés | 92 % |
| Questions avec tous les éléments | 10/13 |
| Réponses avec au moins une citation | 13/13 |
| Citations invalides | 0 |
| Hors corpus : « je ne sais pas » | 2/2 |
| Temps moyen de réponse | 5.6 s |
| Coût moyen par question (reformulation incluse) | 0.0012 $ |
| Questions pour 1 $ | ≈ 807 |

## Détail par question

| Question | Éléments dans les extraits (sans / avec reformulation) | Éléments dans la réponse claude-haiku-5-5 |
|---|---|---|
| q01 Combien de temps faut-il avoir travaillé pour avoir droit au chômage ? | 4/4 / 4/4 | 4/4 |
| q02 Comment est calculé le montant de mon allocation chômage ? | 3/5 / 5/5 | 5/5 |
| q03 J'ai 56 ans et mon contrat s'est terminé en mai 2025. Combien de temps serai-je indemnisé ? | 0/1 / 1/1 | 1/1 |
| q04 Je viens de perdre mon emploi : comment et dans quel délai dois-je m'inscrire à France Travail ? | 3/3 / 2/3 | 2/3 |
| q05 Puis-je toucher le chômage si je démissionne pour me reconvertir ? | 4/4 / 4/4 | 4/4 |
| q06 Si je signe une rupture conventionnelle, aurai-je droit au chômage, et puis-je encore changer d'avis après la signature ? | 2/2 / 1/2 | 1/2 |
| q07 Je vais suivre une formation validée par France Travail. Est-ce que je continue à toucher une allocation ? | 1/3 / 3/3 | 3/3 |
| q08 Je suis fonctionnaire et j'ai été licencié : qui me verse l'allocation chômage ? | 1/3 / 2/3 | 2/3 |
| q09 Si je reprends un travail à temps partiel, est-ce que je garde une partie de mon allocation chômage ? | 0/2 / 2/2 | 2/2 |
| q10 Quand dois-je faire mon actualisation pour le mois de novembre 2026 ? | 2/2 / 2/2 | 2/2 |
| q11 Je ne suis pas d'accord avec une décision de France Travail, que puis-je faire ? | 3/3 / 3/3 | 3/3 |
| q12 Suis-je obligé d'accepter n'importe quelle offre d'emploi ? | 4/4 / 4/4 | 4/4 |
| q13 Qu'est-ce que je risque si je ne vais pas à un rendez-vous France Travail sans raison valable ? | 3/3 / 3/3 | 3/3 |
| q14 Comment calculer le montant de ma future pension de retraite ? | hors corpus | abstention ✅ |
| q15 À combien ai-je droit pour l'aide au logement (APL) de la CAF ? | hors corpus | abstention ✅ |

## Échecs de recherche (au moins un élément clé absent des extraits)

**q02** Comment est calculé le montant de mon allocation chômage ?
- Attendu : 02-montant-are.md, 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 3/5, avec 5/5
- Sans reformulation : 06-rupture-conventionnelle.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md
- Avec reformulation (mots-clés : allocation chômage, ARE, montant de l'ARE, salaire journalier de référence, SJR, calcul de l'allocation, allocation journalière, salaire de référence, périodes d'emploi, allègement dégressif, plafond de l'ARE, taux de remplacement, indemnisation chômage) : 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md

**q03** J'ai 56 ans et mon contrat s'est terminé en mai 2025. Combien de temps serai-je indemnisé ?
- Attendu : 03-duree-indemnisation.md, 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 0/1, avec 1/1
- Sans reformulation : 10-actualisation-obligations.md, 13-radiation-france-travail.md, 04-inscription-france-travail.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 10-actualisation-obligations.md, 08-chomage-agents-publics.md, 12-contrat-engagement-obligations.md
- Avec reformulation (mots-clés : âge 56 ans, fin de contrat mai 2025, durée d'indemnisation, durée de versement de l'ARE, allocation d'aide au retour à l'emploi, fin de contrat de travail, CDD, CDI, licenciement, âge de 55 ans et plus, durée maximale d'indemnisation, reprise de droits) : 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md

**q04** Je viens de perdre mon emploi : comment et dans quel délai dois-je m'inscrire à France Travail ?
- Attendu : 04-inscription-france-travail.md
- Éléments présents : sans reformulation 3/3, avec 2/3
- Sans reformulation : 13-radiation-france-travail.md, 10-actualisation-obligations.md, 12-contrat-engagement-obligations.md, 04-inscription-france-travail.md, 04-inscription-france-travail.md, 04-inscription-france-travail.md, 14-suppression-allocations.md, 04-inscription-france-travail.md
- Avec reformulation (mots-clés : inscription France Travail, délai d'inscription, demandeur d'emploi, perte involontaire d'emploi, licenciement, demande d'allocation de retour à l'emploi (ARE), date d'inscription, espace personnel France Travail, pôle emploi) : 04-inscription-france-travail.md, 04-inscription-france-travail.md, 11-contester-decision.md, 04-inscription-france-travail.md, 10-actualisation-obligations.md, 10-actualisation-obligations.md, 04-inscription-france-travail.md, 10-actualisation-obligations.md

**q06** Si je signe une rupture conventionnelle, aurai-je droit au chômage, et puis-je encore changer d'avis après la signature ?
- Attendu : 06-rupture-conventionnelle.md
- Éléments présents : sans reformulation 2/2, avec 1/2
- Sans reformulation : 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 08-chomage-agents-publics.md, 06-rupture-conventionnelle.md
- Avec reformulation (mots-clés : rupture conventionnelle, allocation d'aide au retour à l'emploi (ARE), conditions d'ouverture de droits, privation involontaire d'emploi, demande d'allocations, délai de rétractation, rétractation, 15 jours calendaires, homologation, DREETS, convention de rupture, indemnité spécifique de rupture conventionnelle) : 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md

**q07** Je vais suivre une formation validée par France Travail. Est-ce que je continue à toucher une allocation ?
- Attendu : 07-formation-aref.md, 02-montant-are.md
- Éléments présents : sans reformulation 1/3, avec 3/3
- Sans reformulation : 07-formation-aref.md, 13-radiation-france-travail.md, 05-demission-reconversion.md, 14-suppression-allocations.md, 04-inscription-france-travail.md, 10-actualisation-obligations.md, 04-inscription-france-travail.md, 06-rupture-conventionnelle.md
- Avec reformulation (mots-clés : formation validée par France Travail, maintien de l'ARE, rémunération pendant la formation, allocation d'aide au retour à l'emploi formation (AREF), cumul ARE et formation, demandeur d'emploi en formation, entrée en formation prescrite ou validée par France Travail) : 07-formation-aref.md, 07-formation-aref.md, 08-chomage-agents-publics.md, 07-formation-aref.md, 08-chomage-agents-publics.md, 05-demission-reconversion.md, 10-actualisation-obligations.md, 08-chomage-agents-publics.md

**q08** Je suis fonctionnaire et j'ai été licencié : qui me verse l'allocation chômage ?
- Attendu : 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 1/3, avec 2/3
- Sans reformulation : 08-chomage-agents-publics.md, 05-demission-reconversion.md, 08-chomage-agents-publics.md, 05-demission-reconversion.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 06-rupture-conventionnelle.md
- Avec reformulation (mots-clés : agent public, fonctionnaire, licenciement, allocation d'aide au retour à l'emploi (ARE), indemnisation chômage, employeur public, Pôle emploi France Travail, contractuel, perte involontaire d'emploi, organisme payeur) : 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 04-inscription-france-travail.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md, 05-demission-reconversion.md, 05-demission-reconversion.md

**q09** Si je reprends un travail à temps partiel, est-ce que je garde une partie de mon allocation chômage ?
- Attendu : 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 0/2, avec 2/2
- Sans reformulation : 13-radiation-france-travail.md, 13-radiation-france-travail.md, 10-actualisation-obligations.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 12-contrat-engagement-obligations.md
- Avec reformulation (mots-clés : cumul ARE et reprise d'activité, travail à temps partiel, salaire, activité réduite, maintien partiel de l'ARE, allocation d'aide au retour à l'emploi, France Travail, déclaration de situation mensuelle, actualisation mensuelle, complément de salaire, reprise d'emploi) : 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 13-radiation-france-travail.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 10-actualisation-obligations.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md


## Analyse et recommandation

*Section rédigée à la main le 18/11/2026, après lecture des réponses complètes (`eval/reponses.json`). Le script la conserve quand on le relance. La comparaison Haiku / Sonnet complète est dans [resultats_v1_haiku_vs_sonnet.md](resultats_v1_haiku_vs_sonnet.md).*

### Ce que mesure le contrôle automatique, et ses limites
Le contrôle cherche des éléments clés mot pour mot. La lecture des réponses a révélé des faux négatifs : « tribunal administratif » au lieu de « juge administratif », « offre dite « raisonnable » », « ne me permettent pas ». Les deux premiers ont été corrigés dans le script. Le dernier cas restant (q12, Haiku) est une réponse correcte comptée comme incomplète.

### Choix du modèle : Haiku
- **Qualité équivalente.** 10/13 questions complètes pour les deux modèles, en réalité 11/13 pour Haiku après lecture (q12). 0 citation invalide, et 2/2 « je ne sais pas » hors corpus pour les deux.
- **Coût 13 fois plus faible.** Environ 0,0009 $ par question avec Haiku (≈ 1 080 questions pour 1 $), contre 0,0119 $ avec Sonnet (≈ 84 questions pour 1 $).
- **Recommandation : garder Haiku pour la reformulation et pour la réponse.** Sonnet n'apporte rien de mesurable ici, parce que les erreurs restantes viennent de la recherche, pas du modèle.
- Point à surveiller : Haiku ajoute parfois un conseil générique absent des extraits, par exemple « renseignez-vous auprès de votre service RH » (q08). C'est sans gravité, mais à garder en tête.

### Recherche : la reformulation est indispensable
Les éléments clés présents dans les 5 extraits passent de **64 % à 90 %** avec la reformulation, et les questions complètes de 6/13 à 10/13. Le critère « la bonne fiche est parmi les extraits » (100 % dans les deux cas) est trop indulgent pour juger.

### Échecs de recherche restants : faut-il des embeddings ?
Les éléments manquants des réponses viennent tous de la recherche : l'information n'était pas dans les extraits, donc le modèle ne pouvait pas la donner (q02 montant, q06 rupture conventionnelle et chômage, q08 en partie).

Cause principale : **les doublons**. 195 morceaux sur 308 ont un texte identique à un autre, parce que les fiches répètent le même texte pour chaque tranche d'âge et pour le privé comme le public. Sur les 5 places, BM25 en remplit souvent 3 avec le même passage. C'est le cas de q02, qui obtient 3 fois le même passage de la fiche « cumul ». Cause secondaire : une reformulation trop longue (13 mots-clés pour q02) dilue la recherche.

**Les embeddings ne sont pas justifiés à ce stade.** Les échecs ne viennent pas de synonymes, que la reformulation traite déjà, mais de places gaspillées. Deux corrections simples, sans installation, sont à essayer d'abord :
1. **Dédoublonner les résultats** : ne garder qu'un exemplaire d'un même texte parmi les 5 extraits.
2. **Limiter la reformulation** à une dizaine de mots-clés.

Si ces corrections ne suffisent pas, une recherche hybride (BM25 + embeddings) serait la piste suivante.

### Coût de l'évaluation
Une exécution complète (15 questions, Haiku et Sonnet) coûte environ 0,19 $, dont 0,18 $ pour Sonnet. Deux exécutions ont été faites, soit environ 0,40 $ au total. L'option `--recalculer` permet désormais de corriger la notation sans refaire d'appels.

### Mise à jour du 18/11/2026 : dédoublonnage des résultats
**Ce qui a été fait.** La recherche ne garde plus qu'un exemplaire de chaque texte parmi les 5 extraits. Les copies ne sont pas perdues : l'extrait retenu liste toutes les sections où ce texte apparaît (autres âges, privé ou public). Le modèle sait ainsi que la règle vaut pour tous ces cas.

**Le contrôle a aussi été durci.** Les éléments sont maintenant cherchés en mots entiers. Une variante trop vague (« allocation chômage ») a été retirée : Haiku l'avait écrite dans une phrase qui disait justement que les extraits n'en parlaient pas. Limite connue : le contrôle ne distingue pas un élément affirmé d'un élément nié.

**Résultat, avec Haiku et le même contrôle avant et après :**

| Mesure | Avant | Après |
|---|---|---|
| Éléments dans les extraits, sans reformulation | 25/39 | 27/39 |
| Éléments dans les extraits, avec reformulation | 35/39 | 35/39 |
| Éléments dans les réponses | 34/39 | 35/39 |
| Questions complètes | 10/13 | 10/13 |

Le gain est modeste, mais le dédoublonnage reste utile : il libère des places et indique au modèle à qui s'applique chaque règle. **Cause restante identifiée** pour q02 : la reformulation est trop longue (12 mots-clés, dont « revenus d'activité », qui attire la fiche sur le cumul). Prochaine correction à tester : limiter la reformulation à une dizaine de mots-clés essentiels. Coût de cette exécution : environ 0,015 $.

### Mise à jour du 19/11/2026 : reformulation courte (rejetée), 8 extraits (retenus)
Chaque réglage a été mesuré sur **3 passages** de recherche, car la reformulation varie d'un appel à l'autre :

| Réglage | Éléments clés dans les extraits | Moyenne |
|---|---|---|
| 5 extraits (référence) | 34 / 37 / 35 | 35,3/39 |
| 5 extraits, reformulation limitée à 5 mots-clés | 34 / 35 / 35 | 34,7/39 → **rejeté** |
| **8 extraits** | 37 / 37 / 37 | **37,0/39 → retenu** |

- **Hypothèse réfutée.** Raccourcir la reformulation n'améliore rien. Pour q02, la vraie cause est le vocabulaire : le passage « Montant brut » est écrit avec les sigles ARE et SJR, sans le mot « calcul ». Il arrivait 8e, derrière la fiche « cumul », qui contient « est calculé ».
- **Réponses avec 8 extraits (Haiku, 1 passage)** : 36/39 éléments clés (35/39 avant), 10/13 questions complètes, 0 citation invalide, 2/2 « je ne sais pas ». q02 est réglée ; q04 a manqué « 12 mois » dans ce passage, absent de ses extraits cette fois-ci (variation de la reformulation).
- **Coût** : 0,0012 $ par question (5 600 tokens envoyés au lieu de 3 700), soit environ 830 questions pour 1 $. Temps de réponse : 5,6 s.
- **Échecs systématiques** : q06 (rupture conventionnelle et chômage) et q08 (qui verse l'allocation d'un fonctionnaire). C'est la limite de la recherche par mots-clés, à signaler dans le README. Les tableaux ci-dessus correspondent à l'exécution avec 8 extraits.
