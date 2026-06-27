import os
import time
import threading
import requests
from core.logger import log
from flask import Flask
from datetime import datetime
from zoneinfo import ZoneInfo
from services.plurk import plurk
from services.plurk import test_friend_requests
from behavior.publisher import publish
from behavior.scheduler import run_scheduler
from google import genai
from ai.persona import load_persona
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
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PLURK_MY_USER_ID = os.environ.get("PLURK_MY_USER_ID")

# ======== 設定區 ========
# 相關資訊可參考core資料夾
# Bot 行為設定請參考 core/config.py

# ======== 初始化 ========
app = Flask(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)

MY_USER_ID = int(PLURK_MY_USER_ID) if PLURK_MY_USER_ID else None
FRIEND_IDS = set()
# REPLIED_PLURK_IDS = set()

# ======== Gemini 回覆生成 - 社畜人設 ========
def generate_reply(content):
    persona = load_persona()
    prompt = f"""{persona}

---

以下是一位噗友發出的內容：

{content}

---

請以 AI_Anchor 的身份回覆。

規則：

1. 使用繁體中文
2. 30字內
3. 自然聊天
4. 不要說教
5. 不要客服語氣
6. 不要使用「作為AI」
7. 像 Plurk 噗友
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini 錯誤：{e}")
        return "又被叫出來了...社畜抱一個"

# ======== 更新好友列表 ========
def update_friend_cache():
    global FRIEND_IDS
    try:
        friends = plurk.callAPI('/APP/FriendsFans/getFriendsByOffset', {'user_id': MY_USER_ID, 'limit': 1000})
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
        requests_data = plurk.callAPI('/APP/FriendsFans/getFriendRequests')

        log(type(requests_data))
        log(repr(requests_data))
        
        log(f"type = {type(requests_data)}")
        log(f"repr = {repr(requests_data)}")
        log(f"value = {requests_data}")
        
        for req in requests_data:
            user_id = req['id']
            user_name = req.get('nick_name', '某人')
            try:
                result = plurk.callAPI('/APP/FriendsFans/becomeFriend', {'user_id': user_id})
                log(type(result))
                log(repr(result))
#                 plurk.callAPI('/APP/FriendsFans/becomeFriend', {'user_id': user_id})
                log(f"已自動加好友：{user_name}")
                FRIEND_IDS.add(user_id)
            except Exception as e:
                log(f"加好友失敗 {user_name}：{e}")
    except Exception as e:
        log(f"Exception Type: {type(e).__name__}")
        log(f"Exception Detail: {repr(e)}")
        log(f"檢查好友邀請失敗：{e}")

# ======== 主迴圈 ========
def run_bot():

    print("run_bot START")

    log("社畜 Bot 啟動中...")

    print("before test_friend_requests")

    try:
        log(repr(test_friend_requests()))
    except Exception as e:
        log(f"test_friend_requests FAILED: {e}")

    print("after test_friend_requests")

#    log(repr(test_friend_requests()))
    
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
    
#    get_fixtures()
#    get_worldcup_id()
    log(f"關鍵字：{KEYWORDS}")
    log(f"好友限定：{REPLY_ONLY_TO_FRIENDS} ｜ 自動加好友：{AUTO_ADD_FRIEND}")

    while True:
        log("===== while 開始 =====")
        try:
            if time.time() - last_friend_update > FRIEND_CACHE_UPDATE_INTERVAL:
                update_friend_cache()
                last_friend_update = time.time()

            run_scheduler()

            check_friend_requests()

            plurks = plurk.callAPI('/APP/Timeline/getPlurks', {'limit': 20})

            # 取出真正的噗文列表
            plurks = plurks['plurks']
            log(f"本次取得 {len(plurks)} 則噗文")
            
            for p in plurks:
                plurk_id = p['plurk_id']
                user_id = p['owner_id']
                content = p.get('content_raw', '')

                if user_id == MY_USER_ID: 
                    # or plurk_id in REPLIED_PLURK_IDS
                    continue

                response = plurk.callAPI(
                    "/APP/Responses/get",
                    {"plurk_id": plurk_id}
                )

                responses = response.get("responses", [])
                already_replied = any(
                    r["user_id"] == MY_USER_ID
                    for r in responses
                )
                log(f"噗 {plurk_id}：共有 {len(responses)} 則回應，已回覆={already_replied}")
                if already_replied:
                    continue
                    
                # print(response)

                if REPLY_ONLY_TO_FRIENDS and user_id not in FRIEND_IDS:
                    continue

                if any(keyword in content for keyword in KEYWORDS):
                    reply_text = generate_reply(content)
                    try:
                        plurk.callAPI('/APP/Responses/responseAdd', {
                            'plurk_id': plurk_id,
                            'content': reply_text,
                            'qualifier': ':'
                        })
                        log(f"已回覆 {plurk_id}：{reply_text}")
                        # REPLIED_PLURK_IDS.add(plurk_id)
                        time.sleep(3)
                    except Exception as e:
                        log(f"回覆失敗 {plurk_id}：{e}")

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
