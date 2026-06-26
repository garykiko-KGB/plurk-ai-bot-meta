"""
AI Anchor 發文總入口

所有平台的發文都由此控制。
"""
from services.plurk import publish as plurk_publish

def publish(content):
    return plurk_publish(content)
