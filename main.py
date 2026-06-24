from flask import Flask, request, redirect
from plurk_oauth import PlurkAPI
import os, threading, time
from urllib.parse import parse_qs

app = Flask(__name__)
plurk = PlurkAPI(os.environ.get('PLURK_APP_KEY'), os.environ.get('PLURK_APP_SECRET'))

@app.route('/')
def home():
    return 'AI小助手活著！<br><a href="/login">點我授權機器人</a>'

@app.route('/login')
def login():
    try:
        # 這次用 requests_oauthlib 拿 token，100% 穩
        import requests
        from requests_oauthlib import OAuth1
        
        key = os.environ.get('PLURK_APP_KEY')
        secret = os.environ.get('PLURK_APP_SECRET')
        auth = OAuth1(key, secret, callback_uri='https://plurk-ai-bot-meta.onrender.com/callback')
        r = requests.post('https://www.plurk.com/OAuth/request_token', auth=auth)
        
        creds = parse_qs(r.text)
        oauth_token = creds.get('oauth_token')[0]
        oauth_token_secret = creds.get('oauth_token_secret')[0]
        
        app.config['REQUEST_TOKEN_SECRET'] = oauth_token_secret
        
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
        return f'Callback 失敗：{str(e)}<br><a href="/login">重試</a>'

def bot_loop():
    time.sleep(15)
    token = os.environ.get('PLURK_OAUTH_TOKEN')
    token_secret = os.environ.get('PLURK_OAUTH_TOKEN_SECRET')
    
    if token and token_secret:
        print("偵測到 Token，啟動機器人...")
        from plurk_oauth import PlurkAPI
        plurk_auth = PlurkAPI(
            os.environ.get('PLURK_APP_KEY'),
            os.environ.get('PLURK_APP_SECRET'),
            token, token_secret
        )
        while True:
            try:
                data = plurk_auth.callAPI('/APP/Alerts/getActive')
                if data:
                    for alert in data:
                        if alert.get('type') == 'mentioned':
                            nick = alert['from_user']['nick_name']
                            plurk_auth.callAPI('/APP/Responses/responseAdd', {
                                'plurk_id': alert['plurk_id'],
                                'content': f"@{nick} 你好！我是AI小助手，終於上線啦～",
                                'qualifier': 'says'
                            })
                    plurk_auth.callAPI('/APP/Alerts/addAllAsRead')
            except Exception as e:
                print(f"Bot 錯誤: {e}")
            time.sleep(20)

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
