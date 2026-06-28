from plurk_oauth import PlurkAPI
import os

PLURK_APP_KEY = os.environ.get("PLURK_APP_KEY")
PLURK_APP_SECRET = os.environ.get("PLURK_APP_SECRET")
PLURK_TOKEN = os.environ.get("PLURK_TOKEN")
PLURK_TOKEN_SECRET = os.environ.get("PLURK_TOKEN_SECRET")

plurk = PlurkAPI(
    PLURK_APP_KEY,
    PLURK_APP_SECRET
)

plurk.authorize(
    PLURK_TOKEN,
    PLURK_TOKEN_SECRET
)

__all__ = [
    "plurk",
    "publish",

    # Alerts
    "get_alerts",
    "accept_friend_request",
    "deny_friend_request",
    "accept_all_friend_requests",

    # Friends
    "send_friend_request",
    "get_friends",
]


# ===== 發文 =====
def publish(content):
    """
    發送 Plurk
    """
    print("services.plurk.publish()")

    try:
        result = plurk.callAPI(
            "/APP/Timeline/plurkAdd",
            {
                "content": content,
                "qualifier": ":"
            }
        )

        print("callAPI 已回傳")
        print(type(result))
        print(repr(result))

        return True

    except Exception as e:

        print("publish FAILED")
        print(repr(e))

        return False

# ===== 通知Alerts =====
def get_alerts():

    return plurk.callAPI(
        "/APP/Alerts/getActive"
    )


def accept_friend_request(user_id):

    return plurk.callAPI(
        "/APP/Alerts/addAsFriend",
        {
            "user_id": user_id
        }
    )


def deny_friend_request(user_id):

    return plurk.callAPI(
        "/APP/Alerts/denyFriendship",
        {
            "user_id": user_id
        }
    )


def accept_all_friend_requests():

    return plurk.callAPI(
        "/APP/Alerts/addAllAsFriends"
    )

# ===== 好友Friends =====
def send_friend_request(user_id):

    return plurk.callAPI(
        "/APP/FriendsFans/becomeFriend",
        {
            "user_id": user_id
        }
    )


def get_friends(user_id):

    return plurk.callAPI(
        "/APP/FriendsFans/getFriendsByOffset",
        {
            "user_id": user_id,
            "limit": 1000
        }
    )
