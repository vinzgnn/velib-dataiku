# Vélib' Paris : préparation des données pour la BI avec Dataiku

Projet de bout en bout sur les données ouvertes Vélib' Métropole : collecte automatisée, préparation dans Dataiku, contrôle qualité, dashboard et rapport automatique par mail.

## Objectif

Aider à piloter le rééquilibrage des vélos : où et quand les stations sont vides ou pleines, et quel est l'effet de la météo.

## Architecture

```
GitHub Actions (toutes les 30 min)
        |
   collect.py  -->  data/*.csv (statuts, météo, stations)
        |
   Dataiku : 3 datasets bruts
        |
   Préparation --> Jointures --> Agrégation
        |
   Règles de qualité --> Dashboard --> Scénario --> Mail (PDF)
```

## Sources

- Vélib' Métropole (GBFS) : `station_status.json` et `station_information.json`.
- Open-Meteo : température, précipitations, vent pour Paris.

## Contenu du dépôt

| Élément | Rôle |
|---|---|
| `collect.py` | Récupère statuts, météo et stations, et les écrit en CSV |
| `.github/workflows/collect.yml` | Lance la collecte toutes les 30 minutes |
| `requirements.txt` | Dépendances Python |
| `data/` | CSV collectés (un fichier par jour) |

## Flow Dataiku

1. **Données brutes** : `velib_status_raw`, `stations_raw`, `meteo_raw`.
2. **Préparation** : parsing des dates (fuseau Europe/Paris), conversion des timestamps UNIX, composantes de date, indicateurs `is_empty` et `is_full`.
3. **Jointure avec les stations** : récupération de la capacité, des coordonnées et du `station_code_ref`.
4. **Enrichissement** : `taux_remplissage` (plafonné à 1), `secteur` (arrondissement), `zone` (Paris / Banlieue), `statut_station`, `anomalie_capacite`.
5. **Jointure avec la météo** : `velib_status_meteo`.
6. **Agrégation** : `agg_station_heure` (par station, jour et heure).

## KPIs

- Taux de remplissage par arrondissement et par heure.
- Taux de stations vides et pleines.
- Stations les plus souvent vides ou pleines (hors stations hors service).
- Taux de stations hors service.
- Sensibilité à la météo.

## Qualité des données

5 règles sur `velib_status_meteo` :

- Nombre de lignes supérieur à 1000.
- Aucune valeur vide sur les colonnes clés.
- Taux de remplissage minimum supérieur à 0.
- Taux de remplissage maximum inférieur à 1,5.
- Aucune valeur vide sur `secteur` et `station_code_ref`.

Anomalies détectées et corrigées :

- Taux de remplissage supérieur à 1 (plus de vélos que la capacité déclarée) : plafonné, avec une colonne `anomalie_capacite` pour garder la trace.
- Relevé sans `station_code` : le secteur est désormais calculé à partir de la table des stations.
- Fichiers chargés en double : détectés par le nombre de lignes, corrigés.

## Automatisation

Scénario Dataiku "Rapport Vélib quotidien" :

- Déclencheur temporel quotidien.
- Reconstruction du flux.
- Envoi d'un mail avec le dashboard en PDF (canal SMTP Gmail).

## Limites

- Le chargement des CSV dans Dataiku est manuel.
- GitHub Actions exécute les crons au mieux : des relevés peuvent manquer.
- Le calcul de l'arrondissement repose sur le code station (hypothèse validée sur des stations connues).
- Peu de jours de données : les conclusions sur la météo et les jours de semaine sont des indications.

## Pistes d'amélioration

- Lecture directe des CSV depuis GitHub dans Dataiku.
- Modèle simple de prévision du risque de station vide.
- Alertes sur les règles de qualité en échec.
- Historique conservé en plus de la vue de la veille.

## Auteur

Vincent Génin
