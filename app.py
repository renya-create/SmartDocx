from flask import Flask, request, jsonify
from utils.openai_helper import generate_text
import os
import json

app = Flask(__name__)

# JSONのエンコード設定を変更
app.config['JSON_AS_ASCII'] = False

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
        
        # 直接JSONをエンコードして返す
        response_data = {"text": generated_text}
        json_str = json.dumps(response_data, ensure_ascii=False)
        response = Response(
            response=json_str,
            status=200,
            mimetype="application/json"
        )
        return response
    
    except Exception as e:
        error_data = {"error": str(e)}
        json_str = json.dumps(error_data, ensure_ascii=False)
        response = Response(
            response=json_str,
            status=500,
            mimetype="application/json"
        )
        return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))