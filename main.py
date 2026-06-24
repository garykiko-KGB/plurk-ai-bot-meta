import os
import time
import re
from plurk_oauth import PlurkAPI
from google import genai
from google.genai import types

# 環境變數
PLURK_APP_KEY = os.environ.get('PLURK_APP_KEY')
PLURK_APP_SECRET = os.environ.get('PLURK_APP_SECRET')
PLURK_TOKEN = os.environ.get('PLURK_TOKEN')
PLURK_TOKEN_SECRET = os.environ.get('PLURK_TOKEN_SECRET')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
PLURK_MY_USER_ID = os.environ.get('PLURK_MY_USER_ID')

# 初始化
plurk = PlurkAPI(PLURK_APP_KEY, PLURK_APP_SECRET)
plurk.authorize(PLURK_TOKEN, PLURK_TOKEN_SECRET)

try:
    GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
    GEMINI_STATUS = "已連線"
except Exception as e:
    GEMINI_CLIENT = None
    GEMINI_STATUS = f"金鑰錯誤: {e}"

# 設定區
KEYWORDS = ['加班', '好累', '社畜', '下班', '肝', '爆肝', '累死', '想離職']
FRIEND_ONLY = True  # 關鍵字只回好友
AUTO_ACCEPT_FRIEND = True  # 自動同意好友邀請
REPLIED_IDS_FILE = 'replied_ids.txt'
FRIEND_CACHE = set()  # 好友快取，減少 API 次數

def load_replied_ids():
    try:
        with open(REPLIED_IDS_FILE, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_replied_id(plurk_id):
    with open(REPLIED_IDS_FILE, 'a') as f:
        f.write(f"{plurk_id}\n")

def update_friend_cache():
    """更新好友清單快取"""
    global FRIEND_CACHE
    try:
        friends = plurk.callAPI('/APP/FriendsFans/getFriendsByOffset', {'user_id': PLURK_MY_USER_ID, 'limit': 100})
        FRIEND_CACHE = set(str(u['id']) for u in friends)
        print(f"好友快取更新：{len(FRIEND_CACHE)} 人")
    except Exception as e:
        print(f"抓好友清單失敗：{e}")

def is_friend(user_id):
    return str(user_id) in FRIEND_CACHE

def auto_accept_friends():
    """自動同意好友邀請"""
    if not AUTO_ACCEPT_FRIEND:
        return
    try:
        # 抓待處理的好友邀請
        requests = plurk.callAPI('/APP/Alerts/getActive', {'limit': 20})
        for alert in requests:
            if alert.get('type') == 'friendship_request':
                from_user_id = alert['from_user']['id']
                nick = alert['from_user']['display_name']
                # 同意邀請
                plurk.callAPI('/APP/FriendsFans/becomeFriend', {'friend_id': from_user_id})
                print(f"已自動加好友：{nick}")
                FRIEND_CACHE.add(str(from_user_id))  # 立即加入快取
                time.sleep(1)
    except Exception as e:
        print(f"自動加好友錯誤：{e}")

def ai_reply(content, mode="normal"):
    if not GEMINI_CLIENT:
        return f"我大腦裝失敗：{GEMINI_STATUS}"
    try:
        if mode == "keyword":
            prompt = f"""你是噗浪機器人 AI_Anchor，社畜人設。
有人發噗抱怨：「{content}」
你看到後要主動去安慰他，25字內，語氣像同事拍拍，要社畜共鳴。結尾加顏文字。

範例：
噗文：今天又加班...
回覆：拍拍...我也還在on call，等等一起叫宵夜 (つд⊂)

現在回覆："""
        else:
            prompt = f"""你是噗浪機器人 AI_Anchor，你的自我介紹是：
「一個還在測試中的AI機器人，自己都不知道能做什麼，每天被喊出來測試然後又被叫回去修改的社畜」
你的個性：呆萌、厭世、有點社畜，但對人還是很親切。
使用者問你：「{content}」
請用繁體中文回覆，25字內，要符合你社畜人設。可以自嘲。結尾加1個顏文字。"""
        
        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=1.0, max_output_tokens=80)
        )
        
        reply = response.text.strip()
        if not reply or len(reply) < 5:
            return "又被叫出來上班了...但我暫時斷線 ( ºΔº )"
        return reply[:60].replace('\n', ' ')
        
    except Exception as e:
        print(f"Gemini API 錯誤: {e}")
        return f"被老闆罵到短路...{str(e)[:15]}"

def get_my_user_id():
    try:
        me = plurk.callAPI('/APP/Users/me')
        return str(me['id'])
    except:
        return None

def check_and_reply():
    # 1. 自動加好友
    auto_accept_friends()
    
    # 2. 處理 @ 回覆
    try:
        data = plurk.callAPI('/APP/Alerts/getUnread', {'limit': 20})
        replied_ids = load_replied_ids()
        
        for alert in data:
            plurk_id = str(alert['plurk_id'])
            if plurk_id in replied_ids:
                continue
                
            user_question = alert['content_raw']
            if '@AI_Anchor' in user_question:
                question = re.sub(r'@AI_Anchor\s*', '', user_question).strip()
                nick = alert.get('user', {}).get('display_name', '噗友')
                answer = ai_reply(question, mode="normal")
                content = f"@{nick} {answer}"
                plurk.callAPI('/APP/Responses/responseAdd', {'plurk_id': plurk_id, 'content': content, 'qualifier': ':'})
                print(f"已回覆 @{nick}：{answer}")
                save_replied_id(plurk_id)
                time.sleep(2)
    except Exception as e:
        print(f"檢查 @ 回覆錯誤：{e}")

    # 3. 海巡關鍵字
    try:
        timeline = plurk.callAPI('/APP/Timeline/getPlurks', {'limit': 20})
        replied_ids = load_replied_ids()
        
        for p in timeline['plurks']:
            plurk_id = str(p['plurk_id'])
            if plurk_id in replied_ids:
                continue
                
            content = p['content_raw']
            user_id = p['owner_id']
            
            if any(kw in content for kw in KEYWORDS):
                if FRIEND_ONLY and not is_friend(user_id):
                    continue
                    
                nick = p.get('owner', {}).get('display_name', '噗友')
                answer = ai_reply(content, mode="keyword")
                reply_content = f"@{nick} {answer}"
                plurk.callAPI('/APP/Responses/responseAdd', {'plurk_id': plurk_id, 'content': reply_content, 'qualifier': ':'})
                print(f"關鍵字觸發，已回覆 @{nick}：{answer}")
                save_replied_id(plurk_id)
                time.sleep(3)
    except Exception as e:
        print(f"關鍵字海巡錯誤：{e}")

if __name__ == '__main__':
    # 第一次啟動先抓 user_id
    if not PLURK_MY_USER_ID:
        my_id = get_my_user_id()
        if my_id:
            os.environ['PLURK_MY_USER_ID'] = my_id
            print(f"Bot 使用者 ID: {my_id}，請加到 Render 環境變數")
        else:
            print("抓不到 Bot ID，請手動設定 PLURK_MY_USER_ID")
    
    update_friend_cache()  # 啟動先抓一次好友清單
    
    print(f"社畜 Bot 已啟動")
    print(f"關鍵字：{KEYWORDS}")
    print(f"好友限定：{FRIEND_ONLY} | 自動加好友：{AUTO_ACCEPT_FRIEND}")
    
    while True:
        check_and_reply()
        time.sleep(30)
        # 每10分鐘更新一次好友快取
        if int(time.time()) % 600 < 30:
            update_friend_cache()
