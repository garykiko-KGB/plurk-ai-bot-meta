"""
AI Anchor 發文總入口
所有平台的發文都由此控制。
"""
from core.logger import log
from services.plurk import publish as plurk_publish
from behavior.ratelimiter import (
    can_post,
    record_post,
)

def publish(content):
    
    print("publisher() 被呼叫", flush=True)
    log("publisher() 被呼叫")

    allow = can_post()
    
    print(f"can_post = {allow}", flush=True)
    log(f"can_post = {allow}")
    
    if not allow:
        print("RateLimiter：冷卻中，取消發文", flush=True)
        log("RateLimiter：冷卻中，取消發文")
        return False

    result = plurk_publish(content)
    print("publisher() 發文了", flush=True)
    log("publisher() 發文了")

    if result:
        print("publisher() 發文成功，更新冷卻時間", flush=True)
        log("publisher() 發文成功，更新冷卻時間")
        record_post()
    else:
        print("publisher() 發文失敗", flush=True)
        log("publisher() 發文失敗")

    log(f"publisher() 完成：{result}")

    return result
