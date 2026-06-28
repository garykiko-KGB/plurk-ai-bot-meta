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
    "get_friend_requests",
    "become_friend",
    "get_friends",
    "test_friend_requests",
]

# ===== 發文 =====
def publish(content):
    """
    發送 Plurk
    """
    print("services.plurk.publish()")
#     print(dir(plurk))
    
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

# ===== 好友 =====
def get_friend_requests():

    return plurk.callAPI(
        "/APP/FriendsFans/getFriendRequests"
    )

def become_friend(user_id):

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

# ===== 測試 =====
def test_friend_requests():
    print("===== test_friend_requests =====")

    try:
        result = plurk.callAPI("/APP/FriendsFans/getFriendRequests")

        print("SUCCESS")
        print(type(result))
        print(repr(result))

        return result

    except Exception as e:
        print("FAILED")
        print(type(e))
        print(repr(e))

        # 如果 plurk_oauth 有留下 error，就一起印
        try:
            print("plurk.error() =", plurk.error())
#            print("plurk.error =", repr(plurk.error))
        except:
            pass

        raise


# def test_friend_requests():
#     return plurk.callAPI("/APP/FriendsFans/getFriendRequests")
    
