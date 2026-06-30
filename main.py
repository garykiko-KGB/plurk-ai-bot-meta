import os
import time
import threading
import requests
from core.logger import log
from flask import Flask
from datetime import datetime
from zoneinfo import ZoneInfo
from services.plurk import (
    plurk,
    get_alerts,
    accept_friend_request,
    deny_friend_request,
    accept_all_friend_requests,
    get_friends,
)
from behavior.listener import listen
from behavior.publisher import publish
from behavior.scheduler import run_scheduler
from core.config import (
    KEYWORDS,
    REPLY_ONLY_TO_FRIENDS,
    AUTO_ADD_FRIEND,
    FRIEND_CACHE_UPDATE_INTERVAL,
)
from modules.fifa_report import build_daily_report

# from modules.fifa import (get_fixtures, filter_today, format_today,)
# from plurk_oauth import PlurkAPI
# from modules.fifa import get_fixtures
# from modules.fifa import get_worldcup_id

# ======== 設定時區 ========
TW = ZoneInfo("Asia/Taipei")

# ======== 環境變數 ========
# 相關資訊可參考platform資料夾
# Plurk OAuth 初始化請參考 services/plurk.py
# GEMINI_API_KEY 相關資訊可參考 ai/reply.py
PLURK_MY_USER_ID = os.environ.get("PLURK_MY_USER_ID")

# ======== 設定區 ========
# 相關資訊可參考core資料夾
# Bot 行為設定請參考 core/config.py

# ======== 初始化 ========
# 相關資訊可參考 ai/reply.py
app = Flask(__name__)


MY_USER_ID = int(PLURK_MY_USER_ID) if PLURK_MY_USER_ID else None
FRIEND_IDS = set()
# REPLIED_PLURK_IDS = set()

# ======== Gemini 回覆生成 - 社畜人設 ========
# 相關資訊可參考 ai/reply.py 

# ======== 更新好友列表 ========
def update_friend_cache():
    global FRIEND_IDS
    try:
        friends = get_friends(MY_USER_ID)
        print(type(friends))
        print(friends)
        
        FRIEND_IDS = set([user['id'] for user in friends])
        log(f"好友快取更新：{len(FRIEND_IDS)} 人")
    except Exception as e:
        log(f"更新好友列表失敗：{e}")

# ======== 自動加好友 ========
def check_friend_requests():

    if not AUTO_ADD_FRIEND:
        return

    try:
        alerts = get_alerts()

        if not alerts:
            return

        for alert in alerts:

            if alert.get("type") != "friendship_request":
                continue

            user = alert["from_user"]

            # 確認格式用，亦可直接刪掉
            # print(user, flush=True)  
            
            log(repr(user))
            
            user_id = user["id"]
            user_name = user.get("nick_name", "Unknown")

            log(f"接受好友：{user_name} ({user_id})")

            result = accept_friend_request(user_id)

            log(type(result))
            log(repr(result))

            FRIEND_IDS.add(user_id)

    except Exception as e:
        print(type(e), flush=True)
        print(repr(e), flush=True)
    
        log(f"Exception Type: {type(e).__name__}")
        log(f"Exception Detail: {repr(e)}")
        log(f"CFR ERROR: {e}")
        

# ======== 主迴圈 ========
def run_bot():

    print("run_bot START")

    log("社畜 Bot 啟動中...")
   
    try:
        log("準備驗證 Plurk Token")
        log("開始呼叫 Users/me")
        log(f"開始 Users/me {time.time()}")
        me = plurk.callAPI('/APP/Users/me')
        log(f"結束 Users/me {time.time()}")
        log("Users/me 呼叫完成")
        print(me)
        log("已取得 me 資料")

        global MY_USER_ID
        MY_USER_ID = me['id']

        log(f"Plurk Token 認證成功")
        log(f"Bot 使用者 ID: {MY_USER_ID}，Token 有效")
        log("===== 即將進入 while =====")

    except Exception as e:
        log(f"Plurk Token 認證失敗：{e}")
        return

    update_friend_cache()
    last_friend_update = time.time()
    
    log("社畜 Bot 已啟動")
    publish(
        f"AI Anchor 發文測試成功！\n"
        f"{datetime.now(TW).strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        report = build_daily_report()

        print("=== 今日 FIFA 戰報 ===", flush=True)
        print(report, flush=True)
        log("=== 今日 FIFA 戰報 ===")
        log("\n" + report)

    except Exception as e:
        print(f"FIFA Error: {e}")
        log(f"FIFA Error: {e}")
    
    log(f"關鍵字：{KEYWORDS}")
    log(f"好友限定：{REPLY_ONLY_TO_FRIENDS} ｜ 自動加好友：{AUTO_ADD_FRIEND}")
    
    while True:
        print("===== while 開始 =====", flush=True)
        log("===== while 開始 =====")

        try:
            if time.time() - last_friend_update > FRIEND_CACHE_UPDATE_INTERVAL:
                update_friend_cache()
                last_friend_update = time.time()

            run_scheduler()

            check_friend_requests()

            # 監聽 Timeline 並自動回覆
            listen()
           
            print("===== while 結束 =====", flush=True)
            log("===== while 結束 =====")
            time.sleep(30)

        except Exception as e:
            import traceback
            traceback.print_exc()
            log(f"主迴圈錯誤：{e}")
            time.sleep(60)

# ======== Flask 保活 ========
@app.route('/')
def home():
    return "社畜 Bot 活著"

@app.route('/callback')
def callback():
    return "callback ok"

# ======== 啟動 ========
if __name__ == '__main__':
    port = int(os.environ.get("PORT",10000))
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=port)
