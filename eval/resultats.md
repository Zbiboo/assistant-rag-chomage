# Résultats de l'évaluation

15 questions (13 sur le corpus, 2 hors corpus). Reformulation : claude-haiku-5-5. Extraits par question : 5.

## Recherche : la bonne fiche est-elle parmi les extraits ?

| Méthode | Bonne fiche parmi les extraits | Éléments clés présents dans les extraits | Questions avec tous leurs éléments |
|---|---|---|---|
| BM25 sur la question brute | 13/13 (100 %) | 27/39 (69 %) | 6/13 |
| BM25 + reformulation | 13/13 (100 %) | 35/39 (90 %) | 10/13 |

## Réponses : comparaison des modèles

| | claude-haiku-5-5 |
|---|---|
| Éléments clés trouvés | 90 % |
| Questions avec tous les éléments | 10/13 |
| Réponses avec au moins une citation | 13/13 |
| Citations invalides | 0 |
| Hors corpus : « je ne sais pas » | 2/2 |
| Temps moyen de réponse | 5.3 s |
| Coût moyen par question (reformulation incluse) | 0.0010 $ |
| Questions pour 1 $ | ≈ 977 |

## Détail par question

| Question | Éléments dans les extraits (sans / avec reformulation) | Éléments dans la réponse claude-haiku-5-5 |
|---|---|---|
| q01 Combien de temps faut-il avoir travaillé pour avoir droit au chômage ? | 4/4 / 4/4 | 4/4 |
| q02 Comment est calculé le montant de mon allocation chômage ? | 3/5 / 3/5 | 3/5 |
| q03 J'ai 56 ans et mon contrat s'est terminé en mai 2025. Combien de temps serai-je indemnisé ? | 0/1 / 1/1 | 1/1 |
| q04 Je viens de perdre mon emploi : comment et dans quel délai dois-je m'inscrire à France Travail ? | 1/3 / 3/3 | 3/3 |
| q05 Puis-je toucher le chômage si je démissionne pour me reconvertir ? | 4/4 / 4/4 | 4/4 |
| q06 Si je signe une rupture conventionnelle, aurai-je droit au chômage, et puis-je encore changer d'avis après la signature ? | 1/2 / 1/2 | 1/2 |
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
- Éléments présents : sans reformulation 3/5, avec 3/5
- Sans reformulation : 06-rupture-conventionnelle.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md
- Avec reformulation (mots-clés : allocation d'aide au retour à l'emploi (ARE), montant de l'ARE, salaire journalier de référence (SJR), calcul de l'allocation, allocation journalière, indemnisation chômage, revenus d'activité antérieurs, période de référence, allégement dégressif, plafond de l'ARE, allocation minimale, France Travail) : 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md

**q03** J'ai 56 ans et mon contrat s'est terminé en mai 2025. Combien de temps serai-je indemnisé ?
- Attendu : 03-duree-indemnisation.md, 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 0/1, avec 1/1
- Sans reformulation : 10-actualisation-obligations.md, 13-radiation-france-travail.md, 04-inscription-france-travail.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md
- Avec reformulation (mots-clés : âge 56 ans, fin de contrat mai 2025, durée d'indemnisation, durée de versement de l'ARE, allocation d'aide au retour à l'emploi, fin de contrat de travail, CDD, CDI, âge à l'ouverture des droits, durée maximale d'indemnisation, durée d'affiliation, France Travail) : 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 09-cumul-reprise-emploi.md

**q04** Je viens de perdre mon emploi : comment et dans quel délai dois-je m'inscrire à France Travail ?
- Attendu : 04-inscription-france-travail.md
- Éléments présents : sans reformulation 1/3, avec 3/3
- Sans reformulation : 13-radiation-france-travail.md, 10-actualisation-obligations.md, 12-contrat-engagement-obligations.md, 04-inscription-france-travail.md, 04-inscription-france-travail.md
- Avec reformulation (mots-clés : inscription France Travail, délai d'inscription, demandeur d'emploi, perte d'emploi, fin de contrat, licenciement, inscription en ligne, pièces justificatives, allocation de retour à l'emploi (ARE), date d'inscription, démarches France Travail) : 04-inscription-france-travail.md, 04-inscription-france-travail.md, 04-inscription-france-travail.md, 04-inscription-france-travail.md, 04-inscription-france-travail.md

**q06** Si je signe une rupture conventionnelle, aurai-je droit au chômage, et puis-je encore changer d'avis après la signature ?
- Attendu : 06-rupture-conventionnelle.md
- Éléments présents : sans reformulation 1/2, avec 1/2
- Sans reformulation : 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md
- Avec reformulation (mots-clés : rupture conventionnelle, droits à l'ARE, éligibilité allocation d'aide au retour à l'emploi, conditions d'ouverture de droits, privation involontaire d'emploi, délai de rétractation, rétractation rupture conventionnelle, 15 jours calendaires, homologation rupture conventionnelle, DREETS, date de fin de contrat, indemnité spécifique de rupture conventionnelle) : 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md, 06-rupture-conventionnelle.md

**q07** Je vais suivre une formation validée par France Travail. Est-ce que je continue à toucher une allocation ?
- Attendu : 07-formation-aref.md, 02-montant-are.md
- Éléments présents : sans reformulation 1/3, avec 3/3
- Sans reformulation : 07-formation-aref.md, 13-radiation-france-travail.md, 05-demission-reconversion.md, 14-suppression-allocations.md, 04-inscription-france-travail.md
- Avec reformulation (mots-clés : formation validée par France Travail, maintien de l'ARE, rémunération pendant la formation, allocation d'aide au retour à l'emploi formation, AREF, demandeur d'emploi en formation, stagiaire de la formation professionnelle, rémunération de formation, Fonds paritaire de sécurisation des parcours professionnels, FPSPP, conditions de maintien de l'indemnisation) : 07-formation-aref.md, 07-formation-aref.md, 07-formation-aref.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md

**q08** Je suis fonctionnaire et j'ai été licencié : qui me verse l'allocation chômage ?
- Attendu : 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 1/3, avec 2/3
- Sans reformulation : 08-chomage-agents-publics.md, 05-demission-reconversion.md, 08-chomage-agents-publics.md, 05-demission-reconversion.md, 08-chomage-agents-publics.md
- Avec reformulation (mots-clés : agent public, fonctionnaire, licenciement, allocation d'aide au retour à l'emploi (ARE), indemnisation chômage, employeur public, Pôle emploi, France Travail, contrat de travail, agent contractuel, collectivité territoriale, remboursement, versement de l'ARE) : 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md, 04-inscription-france-travail.md

**q09** Si je reprends un travail à temps partiel, est-ce que je garde une partie de mon allocation chômage ?
- Attendu : 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md
- Éléments présents : sans reformulation 0/2, avec 2/2
- Sans reformulation : 13-radiation-france-travail.md, 13-radiation-france-travail.md, 10-actualisation-obligations.md, 08-chomage-agents-publics.md, 08-chomage-agents-publics.md
- Avec reformulation (mots-clés : cumul ARE et reprise d'activité, travail à temps partiel, salaire, cumul partiel de l'allocation, ARE, allocation d'aide au retour à l'emploi, reprise d'emploi réduite, activité réduite, déclaration de situation mensuelle, actualisation mensuelle, montant de l'ARE, salaire journalier de référence, France Travail) : 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 09-cumul-reprise-emploi.md, 08-chomage-agents-publics.md, 13-radiation-france-travail.md


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
