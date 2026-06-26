import os
import requests
from datetime import datetime, timezone

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

def get_fixtures():

    headers = {
        "X-Auth-Token": API_KEY
    }

    response = requests.get(
        "https://api.football-data.org/v4/competitions/WC/matches",
        headers=headers
    )

#    print("HTTP:", response.status_code)
    response.raise_for_status()
    
    data = response.json()

    return data["matches"]

def filter_today(matches):

    today = datetime.now(timezone.utc).date()

    print("TODAY =", today)
    
    today_matches = []

    for match in matches:

        print(
            "UTC:",
            match["utcDate"],
            "| status:",
            match["status"],
            "|",
            match["homeTeam"]["name"],
            "-",
            match["awayTeam"]["name"]
        )

        match_date = datetime.fromisoformat(
            match["utcDate"].replace("Z", "+00:00")
        ).date()

        if match_date == today:
            print("MATCH!!", match["utcDate"])
            today_matches.append(match)

    return today_matches
    
def format_today(matches):
    
    lines = []

    for match in matches:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        score = match["score"]["fullTime"]

        home_score = score["home"]
        away_score = score["away"]

        if home_score is None:
            continue

        lines.append(
            f"{home} {home_score}-{away_score} {away}"
        )

    return "\n".join(lines)

#    print("共", len(data["matches"]), "場")
#
#    for match in data["matches"][:5]:
#        home = match["homeTeam"]["name"]
#        away = match["awayTeam"]["name"]
#
#        home_score = match["score"]["fullTime"]["home"] or "-"
#        away_score = match["score"]["fullTime"]["away"] or "-"
#
#        print(f"{home} {home_score}-{away_score} {away}")
