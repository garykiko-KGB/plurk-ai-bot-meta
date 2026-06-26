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

__all__ = ["plurk"]
