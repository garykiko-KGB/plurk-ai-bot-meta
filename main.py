from flask import Flask, request, redirect
from plurk_oauth import PlurkAPI
import os, threading, time

app = Flask(__name__)
plurk = PlurkAPI(os.environ.get('PLURK_APP_KEY'), os.environ.get('PLURK_APP_SECRET'))

@app.route('/')
def home():
    return 'AI小助手活著！<br><a href="/login">點我授權機器人</a>'

@app.route('/login')
def login():
    try:
        # 主動把 callback 網址傳給 Plurk，不傳就會炸
        callback_url = 'https://plurk-ai-bot-meta.onrender.com/callback'
        request_token = plurk.get_request_token(oauth_callback=callback_url)
        auth_url = plurk.get_authorization_url(request_token)
        app.config['REQUEST_TOKEN'] = request_token
        return redirect(auth_url)
    except Exception as e:
        return f'授權失敗：{str(e)}<br>檢查一下 PLURK_APP_KEY 和 SECRET 有沒有設對'

@app.route('/callback')
def callback():
    try:
        verifier = request.args.get('oauth_verifier')
        request_token = app.config['REQUEST_TOKEN']
        plurk.set_request_token(request_token['oauth_token'], request_token['oauth_token_secret'])
        access_token = plurk.get_access_token(verifier)
        return f'''
        <h3>授權成功！</h3>
        把這兩行複製到 Render 的 Environment：<br><br>
        PLURK_OAUTH_TOKEN = {access_token['oauth_token']}<br>
        PLURK_OAUTH_TOKEN_SECRET = {access_token['oauth_token_secret']}<br><br>
        複製完就可以關掉這頁了
        '''
    except Exception as e:
        return f'出錯了：{str(e)}<br>重新點 <a href="/login">/login</a> 試一次'

def bot_loop():
    time.sleep(15)
    if os.environ.get('PLURK_OAUTH_TOKEN'):
        plurk_auth = PlurkAPI(
            os.environ.get('PLURK_APP_KEY'),
            os.environ.get('PLURK_APP_SECRET'),
            os.environ.get('PLURK_OAUTH_TOKEN'),
            os.environ.get('PLURK_OAUTH_TOKEN_SECRET')
        )
        while True:
            try:
                data = plurk_auth.callAPI('/APP/Alerts/getActive')
                for alert in data:
                    if alert['type'] == 'mentioned':
                        plurk_auth.callAPI('/APP/Responses/responseAdd', {
                            'plurk_id': alert['plurk_id'],
                            'content': f"@{alert['from_user']['nick_name']} 你好！我是AI小助手，終於上線啦～",
                            'qualifier': 'says'
                        })
            except Exception as e:
                print(f"Bot error: {e}")
            time.sleep(20)

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
