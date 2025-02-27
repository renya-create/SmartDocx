from flask import Flask, request, Response
from utils.openai_helper import generate_text
import os
from extraction import extracted_text #extraction.pyから抽出された文章をインポート

app = Flask(__name__)

@app.route("/")
def home():
    return "Word自動入力APIサーバーが稼働中です"

@app.route("/generate-text", methods=["POST"])
def api_generate_text():
    try:
        data = request.get_json()
        input_text = extracted_text #ここでextraction.pyで抽出した文章をインプットしたい
        instruction = data.get("instruction", "inputの文章に続く1文として、最も可能性が高いものを出力してください。")
        
        # OpenAIを呼び出して文章生成
        generated_text = generate_text(input_text, instruction)
        
        # テキストだけを返す
        return Response(generated_text, mimetype="text/plain; charset=utf-8")
    
    except Exception as e:
        return Response(f"エラー: {str(e)}", mimetype="text/plain; charset=utf-8"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))


