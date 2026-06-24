from flask import Flask, request, redirect
from plurk_oauth import PlurkAPI
import os, threading, time

app = Flask(__name__)

# 從 Render 環境變數讀取 KEY 和 SECRET
plurk = PlurkAPI(
    os.environ.get('PLURK_APP_KEY'), 
    os.environ.get('PLURK_APP_SECRET')
)

@app.route('/')
def home():
    return 'AI小助手活著！<br><a href="/login">點我授權機器人</a>'

@app.route('/login')
def login():
    try:
        # plurk-oauth 套件不吃 oauth_callback 參數，靠 Plurk 後台的設定
        request_token = plurk.get_request_token()
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
        
        # 用 request_token + verifier 換 access_token
        plurk.set_request_token(
            request_token['oauth_token'], 
            request_token['oauth_token_secret']
        )
        access_token = plurk.get_access_token(verifier)
        
        return f'''
        <h3>授權成功！</h3>
        把這兩行複製到 Render 的 Environment：<br><br>
        PLURK_OAUTH_TOKEN = {access_token['oauth_token']}<br>
        PLURK_OAUTH_TOKEN_SECRET = {access_token['oauth_token_secret']}<br><br>
        複製完就可以關掉這頁，機器人會自動上線
        '''
    except Exception as e:
        return f'出錯了：{str(e)}<br>重新點 <a href="/login">/login</a> 試一次'

def bot_loop():
    # 等 15 秒讓 Flask 先啟動，避免 Render 健康檢查失敗
    time.sleep(15)
    
    # 只有拿到 Token 才啟動機器人迴圈
    if os.environ.get('PLURK_OAUTH_TOKEN') and os.environ.get('PLURK_OAUTH_TOKEN_SECRET'):
        print("偵測到 Token，啟動機器人...")
        plurk_auth = PlurkAPI(
            os.environ.get('PLURK_APP_KEY'),
            os.environ.get('PLURK_APP_SECRET'),
            os.environ.get('PLURK_OAUTH_TOKEN'),
            os.environ.get('PLURK_OAUTH_TOKEN_SECRET')
        )
        
        while True:
            try:
                # 抓未讀通知
                data = plurk_auth.callAPI('/APP/Alerts/getActive')
                if data:
                    for alert in data:
                        # 只回應被 @ 的通知
                        if alert.get('type') == 'mentioned':
                            nick_name = alert['from_user']['nick_name']
                            plurk_id = alert['plurk_id']
                            
                            plurk_auth.callAPI('/APP/Responses/responseAdd', {
                                'plurk_id': plurk_id,
                                'content': f"@{nick_name} 你好！我是AI小助手，終於上線啦～",
                                'qualifier': 'says'
                            })
                            print(f"已回覆 {nick_name}")
                            
                    # 把通知標為已讀，避免重複回
                    plurk_auth.callAPI('/APP/Alerts/addAllAsRead')
                            
            except Exception as e:
                print(f"Bot 迴圈錯誤: {e}")
            
            # 每 20 秒檢查一次
            time.sleep(20)
    else:
        print("還沒拿到 Token，機器人待命中...")

if __name__ == '__main__':
    # 背景執行機器人
    threading.Thread(target=bot_loop, daemon=True).start()
    # Flask 跑在 Render 指定的 port
    app.run(host='0.0.0.0', port=10000)
