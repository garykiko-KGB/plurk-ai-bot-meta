from flask import Flask
from plurk_oauth import PlurkAPI
import os
import time

app = Flask(__name__)

# 這些等等去 Render 的 Environment 設定
plurk = PlurkAPI(
    os.environ.get('PLURK_APP_KEY'),
    os.environ.get('PLURK_APP_SECRET'),
    os.environ.get('PLURK_OAUTH_TOKEN'),
    os.environ.get('PLURK_OAUTH_TOKEN_SECRET')
)

# Render 喚醒用，免得睡死
@app.route('/')
def home():
    return '我活著！AI小助手運作中'

# 最簡單的版本：每30秒檢查一次有沒有人@我
def check_mentions():
    last_checked = None
    while True:
        try:
            plurks = plurk.callAPI('/APP/Timeline/getPlurks', {'limit': 5})
            if plurks and 'plurks' in plurks:
                for p in plurks['plurks']:
                    # 只回覆比上次新的，而且有@我的
                    if last_checked is None or p['posted'] > last_checked:
                        if '@plurk-ai-bot-meta' in p['content_raw'].lower(): # 改成你的機器人帳號
                            reply_text = f"@{p['owner_id']} 嗨！我是 AI 小助手，你剛說：{p['content_raw']}"
                            plurk.callAPI('/APP/Responses/responseAdd', {
                                'plurk_id': p['plurk_id'],
                                'content': reply_text,
                                'qualifier': 'says'
                            })
                if plurks['plurks']:
                    last_checked = plurks['plurks'][0]['posted']
        except Exception as e:
            print(f"出錯了: {e}")
        time.sleep(30)

# 讓 Render 知道要跑這個
if __name__ == '__main__':
    import threading
    t = threading.Thread(target=check_mentions)
    t.start()
    app.run(host='0.0.0.0', port=10000)
