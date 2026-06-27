from datetime import datetime

from modules.fifa import (
    get_fixtures,
    filter_today,
)

def build_daily_report():

    matches = get_fixtures()
    today_matches = filter_today(matches)

    if not today_matches:
        return "⚽ 今日沒有世界盃賽事。"

    finished = []
    playing = []
    upcoming = []

    for match in today_matches:

        status = match["status"]

        if status == "FINISHED":
            finished.append(match)

        elif status in ("IN_PLAY", "PAUSED"):
            playing.append(match)

        else:
            upcoming.append(match)

    lines = []

    lines.append("⚽ FIFA 世界盃每日戰報")
    lines.append(datetime.utcnow().strftime("%Y-%m-%d"))
    lines.append("")

    # ===== 已完賽 ======
    if finished:

        lines.append("🏁 已完賽")

        for match in finished:

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            score = match["score"]["fullTime"]

            home_score = score["home"]
            away_score = score["away"]

            lines.append(
                f"• {home} {home_score}-{away_score} {away}"
            )

        lines.append("")

    # ====== 進行中 ======
    if playing:

        lines.append("🔴 進行中")

        for match in playing:

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            score = match["score"]["fullTime"]

            home_score = score["home"] or 0
            away_score = score["away"] or 0

            lines.append(
                f"• {home} {home_score}-{away_score} {away}"
            )

        lines.append("")

    # ===== 尚未開始 =====
    if upcoming:

        lines.append("⏰ 即將開踢")

        for match in upcoming:

            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            utc = datetime.fromisoformat(
                match["utcDate"].replace("Z", "+00:00")
            )

            lines.append(
                f"• {utc.strftime('%H:%M')} UTC　{home} vs {away}"
            )

    return "\n".join(lines)
