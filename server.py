from flask import Flask, request
import requests
import os
from openai import OpenAI

# 初始化
app = Flask(__name__)
client = OpenAI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# ===== LINE Webhook =====
@app.route("/callback", methods=["POST"])
def callback():
    data = request.json

    for event in data["events"]:
        if event["type"] == "message":
            reply_token = event["replyToken"]
            user_msg = event["message"]["text"]

            ai_reply = ask_ai(user_msg)
            reply_message(reply_token, ai_reply)

    return "OK"

# ===== 回覆訊息 =====
def reply_message(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
    }

    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        json=body
    )

# ===== AI（之後會鎖JSON）=====
def ask_ai(user_msg):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "你是叫車系統，只能回傳JSON，不要任何解釋"
            },
            {
                "role": "user",
                "content": user_msg
            }
        ]
    )

    return response.choices[0].message.content

# ===== 測試用 =====
@app.route("/")
def home():
    return "Bot running!"

# ===== 啟動 =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
