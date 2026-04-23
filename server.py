import os
import json
import google.generativeai as genai
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 關鍵的第一步：建立 Flask 引擎
app = Flask(__name__)

# --- 設定區 (從環境變數抓鑰匙) ---
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def ask_ai(user_msg):
    # 使用 1.5-flash，這是目前最穩定的免費路徑
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
你是叫車派單系統，只能輸出JSON，不要任何解釋。

使用者輸入：
{user_msg}

請輸出格式：
{{
  "action": "create_order"
}}
"""
    try:
        response = model.generate_content(prompt)
        # 🛡️ 脫掉 Markdown 外衣防爆機制
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return clean_json
    except Exception as e:
        return f'{{"action": "error", "reason": "{str(e)}"}}'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    return 'OK'

@handler.add(MessageEvent, filter_content_type='text')
def handle_message(event):
    user_msg = event.message.text
    reply_token = event.reply_token
    
    if "叫車" in user_msg:
        ai_reply = ask_ai(user_msg)
        line_bot_api.reply_message(reply_token, TextSendMessage(text=ai_reply))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=f"你說: {user_msg}"))

@app.route("/")
def home():
    return "伺服器正常運作 ✅ (阿光修正版)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))