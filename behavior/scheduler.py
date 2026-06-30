import json
import os
from datetime import datetime

from zoneinfo import ZoneInfo

from behavior.publisher import publish
from behavior.ratelimiter import PostPriority
from modules.fifa_report import build_daily_report

# ===== 台灣時區 =====
TW = ZoneInfo("Asia/Taipei")

# ===== 排程紀錄檔 =====
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SCHEDULER_FILE = os.path.join(BASE_DIR, "data", "scheduler.json")

# ===== FIFA 發文時間 =====
FIFA_REPORT_TIMES = {
    "03:00",
    "08:00",
    "13:00",
    "16:00",
}


# ===== 建立 scheduler.json =====
def load_scheduler():

    if not os.path.exists(SCHEDULER_FILE):

        os.makedirs(os.path.dirname(SCHEDULER_FILE), exist_ok=True)

        data = {
            "fifa_report": ""
        }

        with open(SCHEDULER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    with open(SCHEDULER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ===== 儲存 scheduler.json =====
def save_scheduler(data):

    with open(SCHEDULER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ===== FIFA 戰報排程 =====
def run_scheduler():

    now = datetime.now(TW)

    current_time = now.strftime("%H:%M")
    current_slot = now.strftime("%Y-%m-%d %H:%M")

    # 不是排程時間
    if current_time not in FIFA_REPORT_TIMES:
        return

    scheduler = load_scheduler()

    # 本時段已發
    if scheduler.get("fifa_report") == current_slot:
        return

    report = build_daily_report()

    if not report:
        return

    if publish(report, priority=PostPriority.SCHEDULED):

        scheduler["fifa_report"] = current_slot

        save_scheduler(scheduler)
