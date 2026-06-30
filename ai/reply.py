import os

from google import genai

from ai.persona import load_persona

# ===== Gemini =====
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


# ===== 使用 AI_Anchor 人設產生回覆 =====
def generate_reply(content):

    persona = load_persona()

    prompt = f"""{persona}

---

以下是一位網友發出的內容：

{content}

---

請以 AI_Anchor 的身份回覆。

規則：

1. 使用繁體中文
2. 30字內
3. 自然聊天
4. 不要說教
5. 不要客服語氣
6. 不要使用「作為AI」
7. 像生活在網上的網友
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        return response.text.strip()

    except Exception as e:

        print(f"Gemini 錯誤：{e}")

        return "又被叫出來了...社畜抱一個"
