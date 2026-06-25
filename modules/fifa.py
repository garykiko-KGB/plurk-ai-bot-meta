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
    print(response.json())
