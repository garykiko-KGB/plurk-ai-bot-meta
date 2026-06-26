import os
import requests
from datetime import datetime, timezone

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

# ==== 取得 FIFA API =====
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

# ==== 找出今日比賽 ====
def filter_today(matches):

    print("開始尋找今天賽程...")

    anchor_time = None

    # 1. 先找正在比賽
    for match in matches:
        if match["status"] == "IN_PLAY":
            anchor_time = datetime.fromisoformat(
                match["utcDate"].replace("Z", "+00:00")
            )
            print("Anchor = IN_PLAY", match["homeTeam"]["name"], "-", match["awayTeam"]["name"])
            break

    # 2. 如果沒有，就找第一場尚未開始
    if anchor_time is None:
        for match in matches:
            if match["status"] == "TIMED":
                anchor_time = datetime.fromisoformat(
                    match["utcDate"].replace("Z", "+00:00")
                )
                print("Anchor = TIMED", match["homeTeam"]["name"], "-", match["awayTeam"]["name"])
                break

    # 3. 如果完全沒有，代表今天沒有比賽
    if anchor_time is None:
        print("今天沒有任何比賽")
        return []

    start_time = anchor_time - timedelta(hours=12)
    end_time = anchor_time + timedelta(hours=12)

    print("Window =", start_time, "~", end_time)

    today_matches = []

    for match in matches:

        match_time = datetime.fromisoformat(
            match["utcDate"].replace("Z", "+00:00")
        )

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

        if start_time <= match_time <= end_time:
            print("MATCH!!", match["utcDate"])
            today_matches.append(match)

    return today_matches

# ==== 格式化比分 ====
def format_today(matches):
    
    lines = []

    for match in matches:

        print("=" * 60)
        print(match["homeTeam"]["name"], "-", match["awayTeam"]["name"])
        print("status =", match["status"])
        print("score =", match["score"])
        
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        print("score object =", match["score"])
        score = match["score"]["fullTime"]

        home_score = score["home"]
        away_score = score["away"]

        if home_score is None:
            continue

        lines.append(
            f"{home} {home_score}-{away_score} {away}"
        )

    return "\n".join(lines)
