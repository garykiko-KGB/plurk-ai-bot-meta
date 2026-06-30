from core.logger import log
from core.config import (
    KEYWORDS,
    REPLY_ONLY_TO_FRIENDS,
)

from core.state import STATE

from services.plurk import (
    get_recent_plurks,
    get_responses,
    reply,
)

from ai.reply import generate_reply

def listen():
    
    # ===== 在噗浪上找前面的公開噗文 ====
    my_user_id = STATE["plurk"]["my_user_id"]
    friend_ids = STATE["plurk"]["friend_ids"]

    # 取得 Timeline
    plurks = get_recent_plurks()
  
    print(f"本次取得 {len(plurks)} 則噗文", flush=True)
    log(f"本次取得 {len(plurks)} 則噗文")

    for p in plurks:

        plurk_id = p["plurk_id"]
        user_id = p["owner_id"]
        content = p.get("content_raw", "")

        # 跳過自己的噗
        if user_id == my_user_id:
            continue

        # 取得Responses並檢查是否已回覆
        responses = get_responses(plurk_id)

        already_replied = any(
            r["user_id"] == my_user_id
            for r in responses
        )

        print(f"噗 {plurk_id}：共有 {len(responses)} 則回應，已回覆={already_replied}", flush=True)
        log(f"噗 {plurk_id}：共有 {len(responses)} 則回應，已回覆={already_replied}")

        if already_replied:
            continue

        # 好友限定
        if (
            REPLY_ONLY_TO_FRIENDS
            and user_id not in friend_ids
        ):
            continue

        # 關鍵字過濾
        if not any(
            keyword in content
            for keyword in KEYWORDS
        ):
            continue

        reply_text = generate_reply(content)

        try:
            # 嘗試回覆
            reply(plurk_id, reply_text)

            print(f"已回覆 {plurk_id}：{reply_text}", flush=True)
            log(f"已回覆 {plurk_id}：{reply_text}")

        except Exception as e:

            log(f"回覆失敗 {plurk_id}：{e}")
