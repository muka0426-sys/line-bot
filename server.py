import os
import json
import google.generativeai as genai
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- 設定區 (從環境變數抓鑰匙) ---
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_ai(user_msg):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"你是派單系統，只能輸出JSON。使用者輸入：{user_msg}。輸出格式：{{'action': 'create_order'}}"
    try:
        response = model.generate_content(prompt)
        return response.text.replace("```json", "").replace("```", "").strip()
    except:
        return '{"action": "error"}'

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    for event in json_data.get('events', []):
        if event['type'] == 'message' and event['message']['type'] == 'text':
            user_msg = event['message']['text']
            reply_token = event['replyToken']
            
            # 只有打「叫車」才發動 AI
            if "叫車" in user_msg:
                ai_reply = ask_ai(user_msg)
                line_bot_api.reply_message(reply_token, TextSendMessage(text=ai_reply))
            else:
                line_bot_api.reply_message(reply_token, TextSendMessage(text=f"你說: {user_msg}"))
    return 'OK'

@app.route("/")
def home():
    return "伺服器正常運作 ✅ (Gemini AI 版)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)