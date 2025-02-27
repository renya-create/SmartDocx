from flask import Flask, request, make_response
from utils.openai_helper import generate_text
import os
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Word自動入力APIサーバーが稼働中です"

@app.route("/generate-text", methods=["POST"])
def api_generate_text():
    try:
        data = request.get_json()
        input_text = data.get("input", "")
        instruction = data.get("instruction", "inputの文章に続く1文として、最も可能性が高いものを出力してください。")
        
        # OpenAIを呼び出して文章生成
        generated_text = generate_text(input_text, instruction)
        
        # 日本語エンコードに対応したレスポンス
        response = make_response(json.dumps({"text": generated_text}, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    
    except Exception as e:
        response = make_response(json.dumps({"error": str(e)}, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))