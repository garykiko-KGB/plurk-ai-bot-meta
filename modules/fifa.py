import os
import requests

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

def get_fixtures():

    headers = {
        "X-Auth-Token": API_KEY
    }

    response = requests.get(
        "https://api.football-data.org/v4/competitions/WC/matches",
        headers=headers
    )

    print("HTTP:", response.status_code)
    response.raise_for_status()
    
    data = response.json()

    print("共", len(data["matches"]), "場")

    for match in data["matches"][:5]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        home_score = match["score"]["fullTime"]["home"] or "-"
        away_score = match["score"]["fullTime"]["away"] or "-"

        print(f"{home} {home_score}-{away_score} {away}")
