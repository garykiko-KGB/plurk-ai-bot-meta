import os
import requests

API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = "https://v3.football.api-sports.io"

def get_worldcup_id():

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(
        f"{BASE_URL}/leagues?search=World Cup",
        headers=headers
    )

    print("HTTP:", response.status_code)
    print(response.json())

# def test():
#    headers = {
#        "x-apisports-key": API_KEY
#    }
#
#    url = f"{BASE_URL}/status"
#
#    response = requests.get(url, headers=headers)
#
#    print("HTTP:", response.status_code)
#    print(response.text)
#
#    return response.status_code
