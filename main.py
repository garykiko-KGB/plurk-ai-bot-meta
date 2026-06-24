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
        import requests
        from requests_oauthlib import OAuth1
        
        key = os.environ.get('PLURK_APP_KEY')
        secret = os.environ.get('PLURK_APP_SECRET')
        
        auth = OAuth1(key, secret, callback_uri='https://plurk-ai-bot-meta.onrender.com/callback')
        r = requests.post('https://www.plurk.com/OAuth/request_token', auth=auth)
        
        return f'''
        <h3>Plurk 原始回應</h3>
        HTTP 狀態碼: {r.status_code}<br>
        回應內容: <pre>{r.text}</pre><br><br>
        <b>Render 用的 KEY:</b> {key}<br>
        <b>Render 用的 SECRET:</b> {secret}<br>
        '''
    except Exception as e:
        return f'程式錯誤：{str(e)}'

@app.route('/callback')
def callback():
    return 'callback ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
