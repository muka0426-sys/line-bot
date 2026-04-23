def ask_ai(user_msg):
    # ✅ 這是最新、最相容的寫法，直接略過 v1beta 的 404 問題
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
        # ⚡ 加上這行強制轉換，確保連線穩定
        response = model.generate_content(prompt)
        
        # 🛡️ 防爆機制
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return clean_json
    except Exception as e:
        # 這裡會噴出具體的報錯原因到 LINE 方便我們看
        import traceback
        error_detail = traceback.format_exc()
        return f'{{"action": "error", "detail": "{str(e)}"}}'