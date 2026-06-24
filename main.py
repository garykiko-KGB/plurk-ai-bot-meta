from flask import Flask, request, redirect
from plurk_oauth import PlurkAPI
import os, threading, time, re
from urllib.parse import parse_qs
from google import genai
from google.genai import types

app = Flask(__name__)
plurk = PlurkAPI(os.environ.get('PLURK_APP_KEY'), os.environ.get('PLURK_APP_SECRET'))

# --- 初始化 Gemini，新版 SDK 支援 AQ... Key ---
GEMINI_CLIENT = None
GEMINI_STATUS = "未初始化"

if os.environ.get('GEMINI_API_KEY'):
    try:
        GEMINI_CLIENT = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        # 啟動時測試呼叫一次，確認 Key 能用
        GEMINI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents="test"
        )
        GEMINI_STATUS = "Gemini 連線成功"
        print("Gemini 大腦已連線")
    except Exception as e:
        GEMINI_STATUS = f"Gemini 初始化失敗: {e}"
        print(f"Gemini 初始化失敗: {e}")
else:
    GEMINI_STATUS = "沒偵測到 GEMINI_API_KEY"
    print("沒偵測到 GEMINI_API_KEY，將使用預設回覆")

def ai_reply(content):
    if not GEMINI_CLIENT:
        return f"我大腦裝失敗：{GEMINI_STATUS}"
    try:
        prompt = f"""你是 Plurk 機器人 AI_Anchor，個性呆萌親切。
有人問你：「{content}」
請用繁體中文回覆，30字內，不要講廢話，直接回答問題。可以加1個顏文字。"""
        
        response = GEMINI_CLIENT.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,  # 調高一點比較活潑
                max_output_tokens=60
            )
        )
        if not response.text:
            return "我被 Google 靜音了，換個問題考我 (｡ŏ_ŏ)"
        reply = response.text.strip().replace('\n', ' ')
        return reply[:60] if reply else "腦袋當機...重問一次看看 🤔"
        
    except Exception as e:
        print(f"Gemini API 錯誤: {e}")
        return f"大腦短路了：{str(e)[:25]}"

def bot_loop():
    time.sleep(15)
    token = os.environ.get('PLURK_OAUTH_TOKEN')
    token_secret = os.environ.get('PLURK_OAUTH_TOKEN_SECRET')
    
    if not (token and token_secret):
        print("還沒拿到 Token，機器人待命中...")
        return
        
    print(f"啟動 AI 回話機器人... Gemini狀態: {GEMINI_STATUS}")
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
        
        time.sleep(15) # 15秒掃一次

# --- Flask 路由 ---
@app.route('/')
def home():
    return f'AI_Anchor AI回話版服役中！<br>Gemini 狀態：{GEMINI_STATUS}<br><a href="/login">點我重新授權</a>'

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
