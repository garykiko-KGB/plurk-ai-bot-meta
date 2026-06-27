from datetime import datetime
from zoneinfo import ZoneInfo
from core.logger import log
from modules.fifa import (
    get_fixtures,
    filter_today,
    LIVE_STATUS,
)
from modules.team_name import team_zh

# ===== 台灣時區 =====
TW = ZoneInfo("Asia/Taipei")


def build_daily_report():

    matches = get_fixtures()
    today_matches = filter_today(matches)

    if not today_matches:
        return (
            "=== FIFA 世界盃每日戰報 ===\n"
            f"更新時間：{datetime.now(TW).strftime('%Y-%m-%d %H:%M')}（台灣時間）\n\n"
            "今日沒有世界盃賽事。"
        )

    finished = []
    playing = []
    upcoming = []

    # ===== 分類 =====
    for match in today_matches:

        status = match["status"]
        
        # 以下是蒐集 API 真正所有會回傳的 status
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        log(f"{home} vs {away} -> {status}")
        # 以上是蒐集 API 真正所有會回傳的 status
        
        if status == "FINISHED":
            finished.append(match)

        elif status in LIVE_STATUS:
            playing.append(match)

        else:
            upcoming.append(match)

    lines = []

    # ===== 標題 =====
    lines.append("=== FIFA 世界盃每日戰報 ===")
    lines.append(
        f"更新時間：{datetime.now(TW).strftime('%Y-%m-%d %H:%M')}（台灣時間）"
    )
    lines.append("")

    # ===== 已完賽 =====
    if finished:

        lines.append("【已完賽】")

        for match in finished:

            home = team_zh(match["homeTeam"]["name"])
            away = team_zh(match["awayTeam"]["name"])

            score = match["score"]["fullTime"]

            home_score = score["home"]
            away_score = score["away"]

            lines.append(
                f"{home} {home_score}-{away_score} {away}"
            )

        lines.append("")

    # ===== 進行中 =====
    if playing:

        lines.append("【進行中】")

        for match in playing:

            home = team_zh(match["homeTeam"]["name"])
            away = team_zh(match["awayTeam"]["name"])

            score = match["score"]["fullTime"]

            home_score = score["home"] or 0
            away_score = score["away"] or 0

            lines.append(
                f"{home} {home_score}-{away_score} {away}"
            )

        lines.append("")

    # ===== 即將開踢 =====
    if upcoming:

        lines.append("【即將開踢】")

        for match in upcoming:

            home = team_zh(match["homeTeam"]["name"])
            away = team_zh(match["awayTeam"]["name"])

            utc_time = datetime.fromisoformat(
                match["utcDate"].replace("Z", "+00:00")
            )

            tw_time = utc_time.astimezone(TW)

            lines.append(
                f"{tw_time.strftime('%H:%M')}　{home} vs {away}"
            )

        lines.append("")

    return "\n".join(lines)
