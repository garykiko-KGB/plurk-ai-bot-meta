"""
Bot 執行期間的共享狀態（Runtime State）
只存放會被多個模組共同使用、且會變動的資料。
"""
STATE = {
    "plurk": {
        "my_user_id": None,
        "friend_ids": set(),
    },
}
