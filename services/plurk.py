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
    "test_friend_requests",
]

def publish(content):
    """
    發送 Plurk
    """
    print("services.plurk.publish()")
    print(dir(plurk))
    
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

    return result

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
            print("plurk.error =", repr(plurk.error))
        except:
            pass

        raise


# def test_friend_requests():
#     return plurk.callAPI("/APP/FriendsFans/getFriendRequests")
    
