from core.logger import log
from core.config import (
    KEYWORDS,
    REPLY_ONLY_TO_FRIENDS,
)

from core.state import STATE

from services.plurk import (
    plurk,
)

from ai.reply import generate_reply

def listen():
    
    # ===== 在噗浪上找前面的公開噗文 ====
    my_user_id = STATE["plurk"]["my_user_id"]
    friend_ids = STATE["plurk"]["friend_ids"]

    plurks = plurk.callAPI("/APP/Timeline/getPlurks", {"limit": 20},)

    plurks = plurks["plurks"]
  
    print(f"本次取得 {len(plurks)} 則噗文", flush=True)
    log(f"本次取得 {len(plurks)} 則噗文")

    for p in plurks:

        plurk_id = p["plurk_id"]
        user_id = p["owner_id"]
        content = p.get("content_raw", "")

        # 跳過自己的噗
        if user_id == my_user_id:
            continue

        # 檢查是否已回覆
        response = plurk.callAPI("/APP/Responses/get", {"plurk_id": plurk_id,},)

        responses = response.get("responses", [])

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

            plurk.callAPI(
                "/APP/Responses/responseAdd",
                {
                    "plurk_id": plurk_id,
                    "content": reply_text,
                    "qualifier": ":",
                },
            )

            print(f"已回覆 {plurk_id}：{reply_text}", flush=True)
            log(f"已回覆 {plurk_id}：{reply_text}")

        except Exception as e:

            log(f"回覆失敗 {plurk_id}：{e}")
