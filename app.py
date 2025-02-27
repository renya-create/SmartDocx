from flask import Flask, request, jsonify
from utils.openai_helper import generate_text
import os

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
        
        return jsonify({"text": generated_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))