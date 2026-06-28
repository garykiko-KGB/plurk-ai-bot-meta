"""
AI Anchor 發文限流器
避免廢文太多被ban掉。
"""
import time
from core.logger import log
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
    
    print(f"[RateLimiter] priority={priority.name}", flush=True)
    print(f"[RateLimiter] cooldown={cooldown}", flush=True)
    print(f"[RateLimiter] last_post_time={_last_post_time}", flush=True)
    log(f"[RateLimiter] priority={priority.name}")
    log(f"[RateLimiter] cooldown={cooldown}")
    log(f"[RateLimiter] last_post_time={_last_post_time}")
    
    if cooldown <= 0:
        print("[RateLimiter] cooldown <= 0，直接允許", flush=True)
        log("[RateLimiter] cooldown <= 0，直接允許")
        return True

    now = time.time()

    elapsed = now - _last_post_time

    print(f"[RateLimiter] now={now}", flush=True)
    print(f"[RateLimiter] elapsed={elapsed}", flush=True)
    log(f"[RateLimiter] now={now}")
    log(f"[RateLimiter] elapsed={elapsed}")

    allow = elapsed >= cooldown
 
    print(f"[RateLimiter] allow={allow}", flush=True)
    log(f"[RateLimiter] allow={allow}")

    return allow

# ===== 紀錄成功發文時間 =====
def record_post():

    global _last_post_time

    _last_post_time = time.time()

    print(f"[RateLimiter] record_post() -> {_last_post_time}", flush=True)
    log(f"[RateLimiter] record_post() -> {_last_post_time}")


# ===== 取得剩餘冷卻秒數 =====
def get_remaining_cooldown(priority=PostPriority.NORMAL):

    cooldown = COOLDOWN[priority]

    if cooldown <= 0:
        return 0

    remain = cooldown - (time.time() - _last_post_time)

    return max(0, int(remain))
