from flask import Flask, request, redirect
from plurk_oauth import PlurkAPI
import os, threading, time, re
from urllib.parse import parse_qs
import google.generativeai as genai

app = Flask(__name__)
plurk = PlurkAPI(os.environ.get('PLURK_APP_KEY'), os.environ.get('PLURK_APP_SECRET'))

# --- 初始化 Gemini ---
GEMINI_CLIENT = None
if os.environ.get('GEMINI_API_KEY'):
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    GEMINI_CLIENT = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini 大腦已連線")
else:
    print("沒偵測到 GEMINI_API_KEY，將使用預設回覆")

def ai_reply(content):
    """把用戶問題丟給 Gemini，回 20 字內中文"""
    if not GEMINI_CLIENT:
        return "我聽到囉，但主人還沒幫我裝 AI 大腦 🧠"
    
    try:
        prompt = f"""你是 AI_Anchor，一個在 Plurk 上的可愛機器人助理。
使用者對你說：{content}
規則：
1. 用繁體中文
2. 20 字以內
3. 語氣親切、可愛、有點呆萌
4. 不要用 markdown"""
        
        res = GEMINI_CLIENT.generate_content(prompt)
        reply = res.text.strip().replace('\n', ' ')
        # Plurk 回覆上限 140 字，這裡保險砍到 60
        return reply[:60] if reply else "我一時想不到怎麼回耶 🤔"
        
    except Exception as e:
        print(f"Gemini API 錯誤: {e}")
        return "我大腦短路了，呼叫主人維修 🛠️"

def bot_loop():
    time.sleep(15)
    token = os.environ.get('PLURK_OAUTH_TOKEN')
    token_secret = os.environ.get('PLURK_OAUTH_TOKEN_SECRET')
    
    if not (token and token_secret):
        print("還沒拿到 Token，機器人待命中...")
        return
        
    print("偵測到 Token，啟動 AI 回話機器人...")
    plurk_auth = PlurkAPI(
        os.environ.get('PLURK_APP_KEY'),
        os.environ.get('PLURK_APP_SECRET'),
        token, token_secret
    )
    
    while True:
        try:
            alerts = plurk_auth.callAPI('/APP/Alerts/getActive')
            if alerts:
                for alert in alerts:
                    if alert.get('type') == 'mentioned':
                        nick = alert['from_user']['nick_name']
                        plurk_id = alert['plurk_id']
                        
                        # 抓被 @ 的那則噗，取原始內容
                        plurk_data = plurk_auth.callAPI('/APP/Timeline/getPlurk', {'plurk_id': plurk_id})
                        raw_content = plurk_data['plurk']['content_raw']
                        
                        # 把 @AI_Anchor 拿掉，剩下的問題丟給 AI
                        user_question = re.sub(r'@AI_Anchor\s*', '', raw_content).strip()
                        if not user_question:
                            user_question = "跟我打個招呼"
                            
                        print(f"收到 {nick} 提問: {user_question}")
                        answer = ai_reply(user_question)
                        
                        # 回文
                        plurk_auth.callAPI('/APP/Responses/responseAdd', {
                            'plurk_id': plurk_id,
                            'content': f"@{nick} {answer}",
                            'qualifier': 'says'
                        })
                        print(f"已回覆 {nick}: {answer}")
                        
                # 全部標已讀，避免重複回
                plurk_auth.callAPI('/APP/Alerts/addAllAsRead')
                        
        except Exception as e:
            print(f"Bot 迴圈錯誤: {e}")
        
        time.sleep(15) # 15秒掃一次，比較即時

# --- Flask 路由 ---
@app.route('/')
def home():
    status = "Gemini 已連線" if GEMINI_CLIENT else "未設定 GEMINI_API_KEY"
    return f'AI_Anchor AI回話版服役中！<br>狀態：{status}<br><a href="/login">點我重新授權</a>'

@app.route('/login')
def login():
    try:
        import requests
        from requests_oauthlib import OAuth1
        key = os.environ.get('PLURK_APP_KEY')
        secret = os.environ.get('PLURK_APP_SECRET')
        auth = OAuth1(key, secret, callback_uri='https://plurk-ai-bot-meta.onrender.com/callback')
        r = requests.post('https://www.plurk.com/OAuth/request_token', auth=auth)
        creds = parse_qs(r.text)
        oauth_token = creds.get('oauth_token')[0]
        app.config['REQUEST_TOKEN_SECRET'] = creds.get('oauth_token_secret')[0]
        auth_url = f"https://www.plurk.com/OAuth/authorize?oauth_token={oauth_token}"
        return redirect(auth_url)
    except Exception as e:
        return f'授權失敗：{str(e)}'

@app.route('/callback')
def callback():
    try:
        import requests
        from requests_oauthlib import OAuth1
        verifier = request.args.get('oauth_verifier')
        token = request.args.get('oauth_token')
        auth = OAuth1(
            os.environ.get('PLURK_APP_KEY'),
            os.environ.get('PLURK_APP_SECRET'),
            resource_owner_key=token,
            resource_owner_secret=app.config['REQUEST_TOKEN_SECRET'],
            verifier=verifier
        )
        r = requests.post('https://www.plurk.com/OAuth/access_token', auth=auth)
        creds = parse_qs(r.text)
        token = creds.get('oauth_token')[0]
        token_secret = creds.get('oauth_token_secret')[0]
        return f'''
        <h3>授權成功！機器人即將上線</h3>
        把這兩行貼到 Render → Environment：<br><br>
        PLURK_OAUTH_TOKEN = {token}<br>
        PLURK_OAUTH_TOKEN_SECRET = {token_secret}<br><br>
        貼完按 Save，機器人 20 秒內自動啟動
        '''
    except Exception as e:
        return f'Callback 失敗：{str(e)}'

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
