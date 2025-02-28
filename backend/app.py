from flask import Flask, request, Response
from utils.openai_helper import generate_text
import os
from utils.extraction import extracted_text #extraction.pyから抽出された文章をインポート

app = Flask(__name__)

@app.route("/")
def home():
    return "Word自動入力APIサーバーが稼働中!!!"

@app.route("/generate-text", methods=["POST"])
def api_generate_text():
    try:
        print("APIリクエストを受信しました")
        data = request.get_json()
        print(f"受信されたデータ: {data}")
        
        # POSTリクエストから直接input_textを取得
        input_text = data.get("input", "")
        print(f"入力テキスト: {input_text}")
        
        # 入力テキストがない場合のバックアップとしてextracted_textを試す
        if not input_text:
            try:
                from utils.extraction import extracted_text
                input_text = extracted_text
                print(f"抽出された文章: {input_text}")
            except Exception as e:
                print(f"extracted_textからの取得に失敗: {str(e)}")
        
        # それでも入力テキストがない場合はエラーを返す
        if not input_text:
            return Response("エラー: 入力テキストがありません", mimetype="text/plain; charset=utf-8"), 400
        
        instruction = data.get("instruction", "inputの文章に続く1文として、最も可能性が高いものを出力してください。")
        
        # OpenAIを呼び出して文章生成
        generated_text = generate_text(input_text, instruction)
        print(f"生成された文章: {generated_text}")
        
        # テキストだけを返す
        return Response(generated_text, mimetype="text/plain; charset=utf-8")
        
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return Response(f"エラー: {str(e)}", mimetype="text/plain; charset=utf-8"), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))


