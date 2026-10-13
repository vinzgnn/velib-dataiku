"""Collecte des disponibilités Vélib' et de la météo à Paris."""

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

URL_STATUS = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"
URL_INFO = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json"
URL_METEO = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=48.8566&longitude=2.3522"
    "&current=temperature_2m,apparent_temperature,precipitation,rain,wind_speed_10m,weather_code"
    "&timezone=UTC"
)

DOSSIER_DATA = Path(__file__).parent / "data"
TIMEOUT = 30

CHAMPS_STATUS = [
    "collected_at",
    "station_id",
    "station_code",
    "num_bikes_available",
    "mechanical",
    "ebike",
    "num_docks_available",
    "is_installed",
    "is_renting",
    "is_returning",
    "last_reported",
]
CHAMPS_STATIONS = ["station_id", "station_code", "name", "lat", "lon", "capacity"]
CHAMPS_METEO = [
    "collected_at",
    "temperature_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "weather_code",
]


def recuperer_json(url):
    """Appelle une URL et renvoie le JSON, avec une erreur claire en cas d'échec."""
    reponse = requests.get(url, timeout=TIMEOUT)
    reponse.raise_for_status()
    return reponse.json()


def types_velos(station):
    """Extrait le nombre de vélos mécaniques et électriques d'une station."""
    resultat = {"mechanical": 0, "ebike": 0}
    for element in station.get("num_bikes_available_types", []):
        for cle, valeur in element.items():
            if cle in resultat:
                resultat[cle] = valeur
    return resultat


def ecrire_csv(chemin, champs, lignes, ecraser=False):
    """Écrit des lignes dans un CSV, avec en-tête si le fichier est nouveau."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if ecraser else "a"
    nouveau = ecraser or not chemin.exists()
    with open(chemin, mode, newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=champs)
        if nouveau:
            writer.writeheader()
        writer.writerows(lignes)


def collecter_status(horodatage, jour):
    donnees = recuperer_json(URL_STATUS)
    lignes = []
    for station in donnees["data"]["stations"]:
        types = types_velos(station)
        lignes.append(
            {
                "collected_at": horodatage,
                "station_id": station["station_id"],
                "station_code": station.get("stationCode"),
                "num_bikes_available": station.get("num_bikes_available"),
                "mechanical": types["mechanical"],
                "ebike": types["ebike"],
                "num_docks_available": station.get("num_docks_available"),
                "is_installed": station.get("is_installed"),
                "is_renting": station.get("is_renting"),
                "is_returning": station.get("is_returning"),
                "last_reported": station.get("last_reported"),
            }
        )
    ecrire_csv(DOSSIER_DATA / f"velib_status_{jour}.csv", CHAMPS_STATUS, lignes)
    return len(lignes)


def collecter_stations():
    """Rafraîchit la table de référence des stations (écrasée à chaque run)."""
    donnees = recuperer_json(URL_INFO)
    lignes = [
        {
            "station_id": s["station_id"],
            "station_code": s.get("stationCode"),
            "name": s.get("name"),
            "lat": s.get("lat"),
            "lon": s.get("lon"),
            "capacity": s.get("capacity"),
        }
        for s in donnees["data"]["stations"]
    ]
    ecrire_csv(DOSSIER_DATA / "stations.csv", CHAMPS_STATIONS, lignes, ecraser=True)
    return len(lignes)


def collecter_meteo(horodatage, jour):
    donnees = recuperer_json(URL_METEO)["current"]
    ligne = {"collected_at": horodatage}
    for champ in CHAMPS_METEO[1:]:
        ligne[champ] = donnees.get(champ)
    ecrire_csv(DOSSIER_DATA / f"meteo_{jour}.csv", CHAMPS_METEO, [ligne])


def main():
    maintenant = datetime.now(timezone.utc)
    horodatage = maintenant.strftime("%Y-%m-%dT%H:%M:%SZ")
    jour = maintenant.strftime("%Y-%m-%d")
    erreurs = []

    try:
        nb = collecter_status(horodatage, jour)
        print(f"Status : {nb} stations collectées")
    except Exception as e:
        erreurs.append(f"status : {e}")

    try:
        collecter_meteo(horodatage, jour)
        print("Météo : relevé ajouté")
    except Exception as e:
        erreurs.append(f"météo : {e}")

    # La table des stations est rafraîchie une fois par jour (premier run de la journée UTC)
    if not (DOSSIER_DATA / "stations.csv").exists() or maintenant.hour == 0 and maintenant.minute < 30:
        try:
            nb = collecter_stations()
            print(f"Stations : {nb} stations de référence")
        except Exception as e:
            erreurs.append(f"stations : {e}")

    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR {erreur}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
