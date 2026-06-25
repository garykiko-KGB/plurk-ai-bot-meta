import os
import requests

API_KEY = os.getenv("FOOTBALL_API_KEY")

BASE_URL = "https://v3.football.api-sports.io"

WORLD_CUP_ID = 1

def get_fixtures():
    headers = {
        "x-apisports-key": API_KEY
    }
    print("===== params =====")
    params = {
        "date": "2026-06-24",
        "league": WORLD_CUP_ID,
        "season": 2026
    }
    print(params)

    response = requests.get(
        f"{BASE_URL}/fixtures",
        headers=headers,
        params=params
    )

    print("===== URL =====")
    print(response.url)

    print("HTTP:", response.status_code)

    data = response.json()
    
    if data.get("errors"):
        print("API 錯誤：", data["errors"])
        return

    print("===== 完整 JSON =====")
    print(data)
    print("====================")

    print("response 數量：", len(data["response"]))

    if len(data["response"]) == 0:
        print("沒有任何比賽資料")
        return

    print("===== 比賽列表 =====")

    for match in data["response"]:
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        date = match["fixture"]["date"]
        status = match["fixture"]["status"]["short"]

        home_score = match["goals"]["home"]
        away_score = match["goals"]["away"]

        print(
            f"{date} | {status} | "
            f"{home} {home_score}-{away_score} {away}"
        )


#    for match in data["response"]:
#        home = match["teams"]["home"]["name"]
#        away = match["teams"]["away"]["name"]
#        date = match["fixture"]["date"]
#
#        print(date, home, "vs", away)

# def get_worldcup_id():
#    headers = {
#        "x-apisports-key": API_KEY
#    }
#
#    response = requests.get(
#        f"{BASE_URL}/leagues?search=World Cup",
#        headers=headers
#    )
#
#    print("HTTP:", response.status_code)
#    
#    data = response.json()
#
#    for league in data["response"]:
#        print(
#            league["league"]["id"],
#            league["league"]["name"]
#        )
