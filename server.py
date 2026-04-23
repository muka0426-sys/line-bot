from flask import Flask, request
import requests

app = Flask(__name__)

import os
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json

    for event in data["events"]:
        if event["type"] == "message":
            reply_token = event["replyToken"]
            user_msg = event["message"]["text"]

            reply_message(reply_token, f"你說: {user_msg}")

    return "OK"


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


@app.route("/")
def home():
    return "Bot running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
