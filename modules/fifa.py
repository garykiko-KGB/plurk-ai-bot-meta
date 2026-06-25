import os
import requests

API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = "https://v3.football.api-sports.io"

WORLD_CUP_ID = 1

# def get_worldcup_id():

#    headers = {
#        "x-apisports-key": API_KEY
#    }

#    response = requests.get(
#        f"{BASE_URL}/leagues?search=World Cup",
#        headers=headers
#    )

#    print("HTTP:", response.status_code)
    
#    data = response.json()

#    for league in data["response"]:
#        print(
#            league["league"]["id"],
#            league["league"]["name"]
#        )
