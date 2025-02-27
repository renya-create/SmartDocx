import time
import platform
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
                extracted_text = current_text  # グローバル変数に抽出された文章を格納

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
    # if file_path:
    #     print(f"監視対象のWordファイル: {file_path}")
    #     event_handler = WordFileHandler(file_path)
    #     observer = Observer()
    #     observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
    #     observer.start()
    #     try:
    #         while True:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         observer.stop()
    #     observer.join()
    # else:
    #     print("ファイルが選択されませんでした。")
