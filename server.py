import os
import json
import google.generativeai as genai
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- 1. 自動抓取你的環境變數 ---
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- 2. AI 大腦運算區 ---
def ask_ai(user_msg):
    if not GEMINI_KEY:
        return '{"action": "error", "reason": "Render後台沒設定GEMINI_API_KEY"}'
    
    try:
        genai.configure(api_key=GEMINI_KEY)
       model = genai.GenerativeModel("gemini-pro")
        prompt = f"你是派單系統，只能輸出JSON。使用者輸入：{user_msg}。輸出格式：{{'action': 'create_order'}}"
        
        response = model.generate_content(prompt)
        
        # 脫掉 Markdown 外殼
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return clean_json
    except Exception as e:
        # 發生錯誤時，直接把原因寫出來，讓你手機看得到
        return f'{{"action": "error", "reason": "{str(e)}"}}'

# --- 3. 接收 LINE 訊息區 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Webhook 錯誤: {e}")
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    reply_token = event.reply_token
    
    # 只要訊息包含「叫車」，就啟動 AI
    if "叫車" in user_msg:
        ai_reply = ask_ai(user_msg)
        line_bot_api.reply_message(reply_token, TextSendMessage(text=ai_reply))
    else:
        # 普通對話測試
        line_bot_api.reply_message(reply_token, TextSendMessage(text=f"伺服器已連線！你說的是：{user_msg}"))

@app.route("/")
def home():
    return "✅ 伺服器運行中 (Gemini 診斷版)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)