import time
import platform
import subprocess
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# OS判定
IS_MAC = platform.system() == "Darwin"

# グローバル変数として抽出された文章を格納
extracted_text = ""

# デバッグ情報を追加して問題を特定
def get_word_text(file_path):
    """Wordファイルのテキストを取得"""
    try:
        print(f"ファイルの存在確認: {os.path.exists(file_path)}")
        if IS_MAC:
            # Mac: textutilを使用
            txt_file_path = "/tmp/word_text.txt"  # 一時的なテキストファイルのパス
            
            # コマンドをデバッグ出力
            cmd = ["textutil", "-convert", "txt", file_path, "-output", txt_file_path]
            print(f"実行するコマンド: {' '.join(cmd)}")
            
            # docxファイルをテキストファイルに変換
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            print(f"コマンド実行結果: 終了コード={result.returncode}")
            print(f"標準出力: {result.stdout}")
            print(f"標準エラー: {result.stderr}")
            
            if result.returncode != 0:
                print("textutilコマンドが失敗しました")
                return None
                
            # テキストファイルを読み込み
            if os.path.exists(txt_file_path):
                with open(txt_file_path, "r") as f:
                    text = f.read()
                
                # 一時ファイルを削除
                os.remove(txt_file_path)
                
                return text.strip()
            else:
                print(f"変換後のファイルが見つかりません: {txt_file_path}")
                return None

    except Exception as e:
        print(f"エラー: {e}")
        return None

class WordFileHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path
        self.last_text = get_word_text(file_path) if os.path.exists(file_path) else ""

    def on_modified(self, event):
        global extracted_text
        print(f"変更イベント検出: {event.src_path}")  # デバッグ情報を追加
        
        # パスの正規化 - /privateプレフィックスの違いを吸収
        normalized_event_path = os.path.normpath(event.src_path)
        normalized_file_path = os.path.normpath(self.file_path)
        
        # ファイル名だけを比較する方法も追加
        event_filename = os.path.basename(event.src_path)
        watched_filename = os.path.basename(self.file_path)
        
        print(f"イベントパス: {normalized_event_path}")
        print(f"監視対象パス: {normalized_file_path}")
        print(f"イベントファイル名: {event_filename}")
        print(f"監視対象ファイル名: {watched_filename}")
        
        # ファイル名だけでも一致する場合は処理を続行
        if normalized_event_path == normalized_file_path or event_filename == watched_filename:
            print("\n[Wordファイルが変更されました]")
            
            # ファイル変更の検出からテキスト取得までの間に少し待機
            time.sleep(0.5)
            
            current_text = get_word_text(event.src_path)  # 実際に変更があったパスを使用
            print(f"取得されたテキスト: {current_text}")  # デバッグ情報を追加
            
            if current_text and current_text != self.last_text:
                print("\n[テキスト変更を検出] \n" + current_text)
                self.last_text = current_text
                # POSTリクエストを送信
                url = "https://teame-hebbh9hhgsdwgwgm.canadacentral-01.azurewebsites.net/generate-text"
                headers = {"Content-Type": "application/json"}
                data = {
                    "input": current_text,
                    "instruction": "inputの文章に続く1文として、最も可能性が高いものを出力してください。"
                }
                
                try:
                    response = requests.post(url, headers=headers, json=data)
                    print(f"APIレスポンスステータス: {response.status_code}")  # デバッグ情報を追加
                    
                    if response.status_code == 200:
                        print(f"API応答: {response.text}")
                        AIanswer = response.text
                    else:
                        print(f"POSTリクエストが失敗しました。ステータスコード: {response.status_code}")
                        print(f"レスポンス内容: {response.text}")
                except Exception as e:
                    print(f"API呼び出し中にエラーが発生しました: {e}")


if __name__ == "__main__":
    # 正しいパスを設定
    file_path = "/var/folders/ml/_h746s1j20lf_d2m5ql9z5_w0000gn/T/Word add-in 507457bb-29a9-4052-ae5b-4ce23e0bb4b8.docx"
    
    # 絶対パスに変換
    file_path = os.path.abspath(file_path)
    
    print(f"監視対象のWordファイル: {file_path}")
    print(f"ファイルの存在確認: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        event_handler = WordFileHandler(file_path)
        observer = Observer()
        # ディレクトリパスの取得時にも絶対パスを使う
        dir_path = os.path.dirname(file_path)
        print(f"監視対象ディレクトリ: {dir_path}")
        observer.schedule(event_handler, dir_path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        print(f"ファイルが存在しません: {file_path}")