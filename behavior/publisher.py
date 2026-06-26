"""
AI Anchor 發文總入口

所有平台的發文都由此控制。
"""
from core.logger import log
from services.plurk import publish as plurk_publish

def publish(content):
    log("publisher() 被呼叫")
    result = plurk_publish(content)
    log(f"publisher() 完成：{result}")
    return result

# def publish(content):
#     return plurk_publish(content)
