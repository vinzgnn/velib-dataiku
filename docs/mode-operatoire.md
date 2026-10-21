# Mode opératoire : dashboard Vélib' Paris

## 1. À quoi sert ce dashboard

Il montre où et quand les stations Vélib' sont vides ou pleines, pour aider à décider où rééquilibrer les vélos.

## 2. Accéder au dashboard

1. Ouvrir Dataiku et le projet "Velib Data Prep".
2. Cliquer sur l'icône **Dashboards** dans la barre du haut.
3. Ouvrir "Vélib Paris", page "Vue d'ensemble".

## 3. Lire les graphiques

| Graphique | Ce qu'il montre | Comment l'utiliser |
|---|---|---|
| Taux de remplissage par arrondissement (Paris) | Part moyenne de places occupées par arrondissement | Repérer les arrondissements en tension (taux très bas ou très haut) |
| Taux de remplissage moyen par heure et par zone | Évolution dans la journée, Paris contre banlieue | Identifier les heures de creux et de pointe |
| Stations les plus souvent pleines | Stations où l'on ne peut plus rendre de vélo | Prévoir des retraits de vélos |
| Stations les plus souvent vides | Stations où l'on ne trouve pas de vélo | Prévoir des apports de vélos |

Les stations hors service sont exclues de ces classements.

## 4. Filtrer

- Cliquer sur **AFFICHER LES FILTRES** en haut du dashboard.
- Filtres disponibles : zone, arrondissement, heure, station, statut.
- Les filtres s'appliquent à tous les graphiques.

## 5. Rapport automatique par mail

- Un mail est envoyé chaque jour à 11:30 (heure de Paris) avec le dashboard en PDF.
- Objet : "Rapport Vélib' : Rapport Vélib quotidien (SUCCESS)".
- En cas d'échec, l'objet indique l'état du scénario.

## 6. Actualiser les données (administrateur)

1. Télécharger les derniers CSV depuis le dépôt GitHub (dossier `data/`).
2. Dans Dataiku, ouvrir `velib_status_raw`, puis **Paramètres**, **Fichiers**.
3. Supprimer les anciens fichiers, ajouter les nouveaux, puis **SAVE**.
4. Faire la même chose pour `meteo_raw`.
5. Lancer le scénario "Rapport Vélib quotidien" (**RUN**).

Point d'attention : ne pas laisser un ancien fichier en plus du nouveau, sinon les données sont comptées en double.

## 7. En cas de problème

| Symptôme | Cause probable | Action |
|---|---|---|
| Dashboard vide | Aucune donnée pour la date filtrée | Recharger les CSV, vérifier le pré-filtre de la recette d'agrégation |
| Mail non reçu | Canal SMTP ou mot de passe d'application invalide | Vérifier le canal dans Administration, puis Messaging channels |
| Règle de qualité en rouge | Donnée anormale | Ouvrir l'onglet Qualité des données du dataset concerné |
| Valeurs en double | Fichier chargé deux fois | Contrôler la liste des fichiers du dataset brut |

## 8. Contact

Vincent Génin
