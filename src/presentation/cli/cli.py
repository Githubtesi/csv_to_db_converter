import sys
from src.module.csv_db_processor.application.commands import DatabaseUpdateCommand
from src.module.csv_db_processor.application.services import DatabaseUpdater
from src.module.csv_db_processor.infrastructure.config import (
    SERVER_CSV_DIR_PATH, DB_FILE_NAME, SERVER_TARGET_DB_PATH,
    SMILE_CSV_CONFIGS, MY_CSV_CONFIGS, LOCAL_APPLICATION_PATH,
    CREATE_SIMPLE_PRODUCT_MASTER_VIEW_QUERY, CREATE_ENVIRONMENTAL_RESEARCH_VIEW_QUERY
)
from src.module.csv_db_processor.infrastructure.launcher.subprocess_db_browser_launcher import SubprocessDbBrowserLauncher
from src.module.csv_db_processor.infrastructure.logging.python_logger import PythonLogger
from src.module.csv_db_processor.infrastructure.repositories.csv_pandas_repository import CsvPandasRepository
from src.module.csv_db_processor.infrastructure.repositories.sqlite_db_repository import SqliteDbRepository
from src.module.csv_db_processor.domain.services import DbGenerationService
from src.module.shared.exceptions import CsvDbProcessorError, ConfigurationError


def run_db_processor_cli() -> None: # 関数名をより実態に合わせ、CLI実行であることを明示
    """
    CSVからDBを生成し、DB Browserで開くCLIアプリケーションのエントリポイント。
    依存関係を解決し、DatabaseUpdaterアプリケーションサービスを実行します。
    """
    # 1. ロガーの初期化
    logger = PythonLogger(name="cli_logger") # ロガー名を変更
    logger.info("CLIアプリケーションが開始されました。")

    try:
        # 2. 設定値の検証（簡易的なもの）
        # config.pyで既に定義されているため、ここではより上位のチェック
        if not SERVER_CSV_DIR_PATH or not LOCAL_APPLICATION_PATH or not DB_FILE_NAME:
            raise ConfigurationError("必須の設定値が不足しています。config.pyを確認してください。")

        # 3. インフラストラクチャ層の実装インスタンス化
        csv_repo = CsvPandasRepository()
        db_repo = SqliteDbRepository()
        db_browser_launcher = SubprocessDbBrowserLauncher()

        # 4. ドメインサービスにインフラ層の依存を注入
        db_generation_service = DbGenerationService(
            csv_repo=csv_repo,
            db_repo=db_repo,
            db_browser_launcher=db_browser_launcher,
            logger=logger
        )

        # 5. アプリケーションサービスにドメインサービスとロガーを注入
        database_updater = DatabaseUpdater(
            db_generation_service=db_generation_service,
            logger=logger
        )

        # 6. コマンドオブジェクトの作成
        command = DatabaseUpdateCommand(
            server_csv_dir_path=SERVER_CSV_DIR_PATH,
            db_file_path=SERVER_TARGET_DB_PATH,
            smile_csv_configs=SMILE_CSV_CONFIGS,
            my_csv_configs=MY_CSV_CONFIGS,
            db_browser_app_path=LOCAL_APPLICATION_PATH,
            create_simple_product_master_view_query=CREATE_SIMPLE_PRODUCT_MASTER_VIEW_QUERY,
            create_environmental_research_view_query=CREATE_ENVIRONMENTAL_RESEARCH_VIEW_QUERY
        )

        # 7. アプリケーションサービスの実行
        database_updater.execute(command)

    except CsvDbProcessorError as e:
        # カスタム例外はすでにロガーで記録されているはずなので、ここでは簡潔に表示
        logger.critical(f"CLIアプリケーション実行中に致命的なエラーが発生しました: {e}")
        sys.exit(1) # エラー終了
    except Exception as e:
        logger.critical(f"予期せぬエラーが発生しました: {e}", exc_info=True) # スタックトレースも出力
        sys.exit(1) # エラー終了

    logger.info("CLIアプリケーションが正常に終了しました。")