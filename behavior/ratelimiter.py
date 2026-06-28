"""
AI Anchor 發文限流器

避免廢文太多被ban掉。
"""
import time
from core.config import (
    POST_COOLDOWN_NORMAL,
    POST_COOLDOWN_SCHEDULED,
    POST_COOLDOWN_SYSTEM,
)
from enum import Enum, auto


# ===== 發文優先權 =====
class PostPriority(Enum):
    NORMAL = auto()
    SCHEDULED = auto()
    SYSTEM = auto()


# ===== 冷卻時間（秒） =====
# 預設廢文要等1800秒，其餘資訊參考 core/config.py
COOLDOWN = {
    PostPriority.NORMAL: POST_COOLDOWN_NORMAL,
    PostPriority.SCHEDULED: POST_COOLDOWN_SCHEDULED,
    PostPriority.SYSTEM: POST_COOLDOWN_SYSTEM,
}


# ===== 上次發文時間 =====
_last_post_time = 0


# ===== 是否允許發文 =====
def can_post(priority=PostPriority.NORMAL):

    global _last_post_time

    cooldown = COOLDOWN[priority]

    if cooldown <= 0:
        return True

    now = time.time()

    return (now - _last_post_time) >= cooldown

# ===== 紀錄成功發文時間 =====
def record_post():

    global _last_post_time

    _last_post_time = time.time()


# ===== 取得剩餘冷卻秒數 =====
def get_remaining_cooldown(priority=PostPriority.NORMAL):

    cooldown = COOLDOWN[priority]

    if cooldown <= 0:
        return 0

    remain = cooldown - (time.time() - _last_post_time)

    return max(0, int(remain))
