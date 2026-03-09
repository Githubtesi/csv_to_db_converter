import sys
from datetime import datetime
from src.presentation.cli.cli import run_db_processor_cli

# --- 設定：使用期限 (年, 月, 日) ---
EXPIRATION_DATE = datetime(2029, 12, 31)


def check_expiration():
    """現在の時刻が期限を過ぎていないかチェックする"""
    if datetime.now() > EXPIRATION_DATE:
        print("--------------------------------------------------")
        print(f"エラー: このプログラムの使用期限（{EXPIRATION_DATE.date()}）を過ぎています。")
        print("最新版をダウンロードするか、管理者に連絡してください。")
        print("--------------------------------------------------")
        # ユーザーがメッセージを確認できるように一時停止（任意）
        input("Enterキーを押すと終了します...")
        sys.exit(1)


if __name__ == "__main__":
    # 期限チェックを実行
    # check_expiration()

    # OKならメイン処理を開始
    run_db_processor_cli()