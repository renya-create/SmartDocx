import time
import platform
import subprocess
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
#各種ライブラリをインポート

# OS判定
IS_MAC = platform.system() == "Darwin"

# グローバル変数として抽出された文章を格納
extracted_text = ""

def get_word_text(file_path):
    """Wordファイルのテキストを取得"""
    try:
        if IS_MAC:
            # Mac: textutilを使用
            txt_file_path = "/tmp/word_text.txt"  # 一時的なテキストファイルのパス

            # docxファイルをテキストファイルに変換
            subprocess.run(["textutil", "-convert", "txt", file_path, "-output", txt_file_path], check=True)

            # テキストファイルを読み込み
            with open(txt_file_path, "r") as f:
                text = f.read()

            # 一時ファイルを削除
            os.remove(txt_file_path)

            return text.strip()
        else:
            # Windows: win32comを使用
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            doc = word.Open(file_path)
            text = doc.Content.Text
            doc.Close()
            return text
    except Exception as e:
        print(f"エラー: {e}")
        return None

class WordFileHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_text = get_word_text(file_path) if os.path.exists(file_path) else ""

    def on_modified(self, event):
        global extracted_text
        if event.src_path == self.file_path:
            current_text = get_word_text(self.file_path)
            if current_text and current_text != self.last_text:
                print("\n[Wordファイルが変更されました] \n" + current_text)
                self.last_text = current_text
                # extracted_text = current_text  # グローバル変数に抽出された文章を格納
                # POSTリクエストを送信
                url = "https://teame-hebbh9hhgsdwgwgm.canadacentral-01.azurewebsites.net/generate-text"
                headers = {"Content-Type": "application/json"}
                data = {
                    "input": current_text,
                    "instruction": "inputの文章に続く1文として、最も可能性が高いものを出力してください。"
                }
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    print(response.text)
                    AIanswer = response.text
                else:
                    print(f"POSTリクエストが失敗しました。ステータスコード: {response.status_code}")

    def on_modified(self, event):
        global extracted_text
        if event.src_path == self.file_path:
            current_text = get_word_text(self.file_path)
            if current_text and current_text != self.last_text:
                if current_text.endswith("。") or current_text.endswith("."):
                    print("\n[Wordファイルが変更されました] \n" + current_text)
                    self.last_text = current_text
                    # extracted_text = current_text  # グローバル変数に抽出された文章を格納
                    # POSTリクエストを送信
                    url = "https://teame-hebbh9hhgsdwgwgm.canadacentral-01.azurewebsites.net/generate-text"
                    headers = {"Content-Type": "application/json"}
                    data = {
                        "input": current_text,
                        "instruction": "inputの文章に続く1文として、最も可能性が高いものを出力してください。"
                    }
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 200:
                        print(response.text)
                        AIanswer = response.text
                    else:
                        print(f"POSTリクエストが失敗しました。ステータスコード: {response.status_code}")


if __name__ == "__main__":
    file_path = "/private/var/folders/rl/m7x_ycvx3yj7kwbyphz0sc680000gn/T/Word add-in 507457bb-29a9-4052-ae5b-4ce23e0bb4b8.docx" # ファイルパスを手動で入力

    if file_path:
        print(f"監視対象のWordファイル: {file_path}")
        event_handler = WordFileHandler(file_path)
        observer = Observer()
        observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        print("ファイルパスが入力されませんでした。")

