import os
import time
import threading
import requests
from flask import Flask
from plurk_oauth import PlurkAPI
from google import genai

# ======== 環境變數 ========
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PLURK_APP_KEY = os.environ.get("PLURK_APP_KEY")
PLURK_APP_SECRET = os.environ.get("PLURK_APP_SECRET")
PLURK_TOKEN = os.environ.get("PLURK_TOKEN")
PLURK_TOKEN_SECRET = os.environ.get("PLURK_TOKEN_SECRET")
PLURK_MY_USER_ID = os.environ.get("PLURK_MY_USER_ID")

# ======== 設定區 ========
KEYWORDS = ['加班', '好累', '社畜', '下班', '肝', '爆肝', '累死', '想離職', '不想上班']
REPLY_ONLY_TO_FRIENDS = True
AUTO_ADD_FRIEND = True
FRIEND_CACHE_UPDATE_INTERVAL = 600

# ======== 初始化 ========
app = Flask(__name__)

# 新版 google-genai 初始化
client = genai.Client(api_key=GEMINI_API_KEY)

plurk = PlurkAPI(PLURK_APP_KEY, PLURK_APP_SECRET)
plurk.authorize(PLURK_TOKEN, PLURK_TOKEN_SECRET)

MY_USER_ID = int(PLURK_MY_USER_ID) if PLURK_MY_USER_ID else None
FRIEND_IDS = set()
REPLIED_PLURK_IDS = set()

# ======== Gemini 回覆生成 ========
def generate_reply(content):
    prompt = f"""
你是一個溫暖的噗浪機器人，專門安慰上班族。有人發了這則噗：
「{content}」

請用繁體中文回覆，語氣輕鬆、像朋友一樣。30字以內，不要太官方。
範例：拍拍，今天也辛苦了、肝是自己的，下班快休息、社畜抱一個
"""
    try:
        # 新版 google-genai 語法
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini 錯誤：{e}")
        return "拍拍，今天也辛苦了"

# ======== 更新好友列表 ========
def update_friend_cache():
    global FRIEND_IDS
    try:
        friends = plurk.callAPI('/APP/FriendsFans/getFriendsByOffset', {'user_id': MY_USER_ID, 'limit': 1000})
        FRIEND_IDS = set([user['id'] for user in friends])
        print(f"好友快取更新：{len(FRIEND_IDS)} 人")
    except Exception as e:
        print(f"更新好友列表失敗：{e}")

# ======== 自動加好友 ========
def check_friend_requests():
    if not AUTO_ADD_FRIEND:
        return
    try:
        requests_data = plurk.callAPI('/APP/FriendsFans/getFriendRequests')
        for req in requests_data:
            user_id = req['id']
            user_name = req.get('nick_name', '某人')
            try:
                plurk.callAPI('/APP/FriendsFans/becomeFriend', {'user_id': user_id})
                print(f"已自動加好友：{user_name}")
                FRIEND_IDS.add(user_id)
            except Exception as e:
                print(f"加好友失敗 {user_name}：{e}")
    except Exception as e:
        print(f"檢查好友邀請失敗：{e}")

# ======== 主迴圈 ========
def run_bot():
    print("社畜 Bot 啟動中...")
    
    try:
        me = plurk.callAPI('/APP/Users/me')
        global MY_USER_ID
        MY_USER_ID = me['id']
        print(f"Plurk Token 認證成功")
        print(f"Bot 使用者 ID: {MY_USER_ID}，Token 有效")
    except Exception as e:
        print(f"Plurk Token 認證失敗：{e}")
        return

    update_friend_cache()
    last_friend_update = time.time()
    
    print("社畜 Bot 已啟動")
    print(f"關鍵字：{KEYWORDS}")
    print(f"好友限定：{REPLY_ONLY_TO_FRIENDS} ｜ 自動加好友：{AUTO_ADD_FRIEND}")

    while True:
        try:
            if time.time() - last_friend_update > FRIEND_CACHE_UPDATE_INTERVAL:
                update_friend_cache()
                last_friend_update = time.time()

            check_friend_requests()

            plurks = plurk.callAPI('/APP/Timeline/getPlurks', {'limit': 20})
            
            for p in plurks:
                plurk_id = p['plurk_id']
                user_id = p['owner_id']
                content = p.get('content_raw', '')

                if user_id == MY_USER_ID or plurk_id in REPLIED_PLURK_IDS:
                    continue

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
                        print(f"已回覆 {plurk_id}：{reply_text}")
                        REPLIED_PLURK_IDS.add(plurk_id)
                        time.sleep(3)
                    except Exception as e:
                        print(f"回覆失敗 {plurk_id}：{e}")

            time.sleep(30)

        except Exception as e:
            print(f"主迴圈錯誤：{e}")
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
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
