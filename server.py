from flask import Flask, request

app = Flask(__name__)

# LINE webhook
@app.route("/callback", methods=["POST"])
def callback():
    print("🔥 收到 LINE 的訊息了！")
    return "OK"

# 測試首頁
@app.route("/")
def home():
    return "伺服器正常運作 ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)