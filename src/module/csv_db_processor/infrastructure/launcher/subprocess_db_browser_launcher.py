import subprocess
from src.module.csv_db_processor.domain.interfaces import IDbBrowserLauncher
from src.module.csv_db_processor.infrastructure.config import IS_READ_ONLY
from src.module.shared.exceptions import DbBrowserLaunchError


class SubprocessDbBrowserLauncher(IDbBrowserLauncher):
    """
    subprocessモジュールを使用してDB Browser for SQLiteアプリケーションを起動するランチャー。
    IDbBrowserLauncherインターフェースを実装します。
    """
    def launch(self, application_path: str, db_file_path: str, is_raed_only:bool=IS_READ_ONLY) -> None:
        """
        指定されたDBファイルでDB Browser for SQLiteアプリケーションを起動します。
        起動に失敗した場合は DbBrowserLaunchError を発生させます。
        """
        try:
            # Popenはノンブロッキングでアプリケーションを通常起動
            # 読み取り専用
            if is_raed_only:
                subprocess.Popen([application_path, "--read-only", db_file_path])
            else:
                subprocess.Popen([application_path, db_file_path])
        except FileNotFoundError:
            raise DbBrowserLaunchError(
                f"DB Browser for SQLiteの実行ファイルが見つかりません: {application_path}"
            )
        except Exception as e:
            raise DbBrowserLaunchError(f"DB Browser for SQLiteの起動に失敗しました: {e}")