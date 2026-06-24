from flask import Flask, request
from plurk_oauth import PlurkAPI
import os, threading, time

app = Flask(__name__)
plurk = PlurkAPI(os.environ.get('PLURK_APP_KEY'), os.environ.get('PLURK_APP_SECRET'))

@app.route('/')
def home():
    return 'AI小助手活著！<br><a href="/login">點我授權機器人</a>'

@app.route('/login')
def login():
    request_token = plurk.get_request_token()
    auth_url = plurk.get_authorization_url(request_token)
    app.config['REQUEST_TOKEN'] = request_token
    return f'請用機器人帳號 AI_Anchor 登入，然後點這個連結授權：<br><a href="{auth_url}">{auth_url}</a>'

@app.route('/callback')
def callback():
    verifier = request.args.get('oauth_verifier')
    request_token = app.config['REQUEST_TOKEN']
    plurk.set_request_token(request_token['oauth_token'], request_token['oauth_token_secret'])
    access_token = plurk.get_access_token(verifier)
    return f'''
    授權成功！把這兩行複製到 Render 的 Environment：<br><br>
    PLURK_OAUTH_TOKEN = {access_token['oauth_token']}<br>
    PLURK_OAUTH_TOKEN_SECRET = {access_token['oauth_token_secret']}<br><br>
    複製完就可以關掉這頁了
    '''

def bot_loop():
    time.sleep(10)
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
                            'content': f"@{alert['from_user']['nick_name']} 你好！我是AI小助手，你剛@我了。功能測試中～",
                            'qualifier': 'says'
                        })
            except: pass
            time.sleep(20)

if __name__ == '__main__':
    threading.Thread(target=bot_loop).start()
    app.run(host='0.0.0.0', port=10000)
