import sqlite3
from typing import List

from src.module.csv_db_processor.domain.entities import CSVConfig, DbFileUpdateStatus
from src.module.csv_db_processor.domain.interfaces import (
    ICsvRepository, IDbBrowserLauncher, IDbRepository, ILogger
)
from src.module.shared.exceptions import (
    CsvFileError, DbConnectionError, DbOperationError, DbBrowserLaunchError
)


class DbGenerationService:
    """
    データベースの生成、更新、ビュー作成という一連のビジネスロジックを調整するドメインサービス。
    ドメインの関心事である「CSVデータからDBを構築・管理する」プロセスをカプセル化します。
    具体的なデータアクセスや外部ツールの起動は、インターフェースを介してインフラストラクチャ層に委譲します。
    """

    def __init__(self,
                 csv_repo: ICsvRepository,
                 db_repo: IDbRepository,
                 db_browser_launcher: IDbBrowserLauncher,
                 logger: ILogger) -> None:
        self._csv_repo: ICsvRepository = csv_repo
        self._db_repo: IDbRepository = db_repo
        self._db_browser_launcher: IDbBrowserLauncher = db_browser_launcher
        self._logger: ILogger = logger

    def process_database_update(self,
                                server_csv_dir_path: str,
                                db_file_path: str,
                                smile_csv_configs: List[CSVConfig],
                                my_csv_configs: List[CSVConfig],
                                db_browser_app_path: str,
                                create_simple_product_master_view_query: str,
                                create_environmental_research_view_query: str) -> None:
        """
        DBの更新プロセス全体を実行します。
        DBファイルの更新要否を判断し、必要であればCSVデータの読み込み、
        テーブルおよびビューの作成・更新を行い、最終的にDB Browserを起動します。

        Args:
            server_csv_dir_path: CSVファイルが配置されているサーバー共有フォルダのパス。
            db_file_path: 生成・更新されるDBファイルの絶対パス。
            smile_csv_configs: SmileシステムからのCSV設定リスト。
            my_csv_configs: 自作CSVの設定リスト。
            db_browser_app_path: DB Browser for SQLiteアプリケーションの実行可能ファイルのパス。
            create_simple_product_master_view_query: simple_product_masterビューを作成するSQLクエリ。
            create_environmental_research_view_query: '環境調査'ビューを作成するSQLクエリ。

        Raises:
            CsvFileError: CSVファイルの読み込みや更新日時取得に失敗した場合。
            DbConnectionError: DBへの接続に失敗した場合。
            DbOperationError: DB操作（テーブル/ビュー作成）に失敗した場合。
            DbBrowserLaunchError: DB Browserの起動に失敗した場合。
        """
        self._logger.info("データベース更新処理を開始します。")

        try:
            # 1. CSVファイルの最新更新日時を取得
            latest_smile_csv_time = self._csv_repo.get_latest_modification_time(
                smile_csv_configs, server_csv_dir_path
            )
            latest_my_csv_time = self._csv_repo.get_latest_modification_time(
                my_csv_configs, server_csv_dir_path
            )
            latest_csv_time = max(latest_smile_csv_time, latest_my_csv_time)
            self._logger.info(f"最新のCSV更新日時: {latest_csv_time}")

            # 2. DBファイルの更新要否をチェック
            db_modified_time = self._db_repo.get_db_modification_time(db_file_path)
            update_status = DbFileUpdateStatus.create(db_modified_time, latest_csv_time)
            self._logger.info(update_status.reason)

            if not update_status.needs_update:
                self._logger.info("DBファイルが最新のため、更新をスキップしDB Browserを起動します。")
                self._db_browser_launcher.launch(db_browser_app_path, db_file_path)
                return

            self._logger.info(update_status.reason) # DBが古いor存在しない場合の理由を再度ログ出力

            # 3. DBに接続
            self._logger.info(f"DBファイル '{db_file_path}' に接続します。")
            conn = self._db_repo.connect(db_file_path)
            try:
                # 4. CSVを読み込み、テーブルを作成
                self._logger.info("CSVデータからテーブルを作成/更新します。")
                self._load_and_create_tables(conn, server_csv_dir_path, smile_csv_configs)
                self._load_and_create_tables(conn, server_csv_dir_path, my_csv_configs)

                # 5. ビューを作成
                self._logger.info("ビューを作成します。")
                self._create_views(
                    conn,
                    create_simple_product_master_view_query,
                    create_environmental_research_view_query
                )
            finally:
                # 6. DB接続を閉じる
                self._logger.info("DB接続を閉じます。")
                self._db_repo.close(conn)

            # 7. DB BrowserでDBファイルを開く
            self._logger.info(f"DB Browser for SQLite で '{db_file_path}' を開きます。")
            self._db_browser_launcher.launch(db_browser_app_path, db_file_path)

            self._logger.info("データベース更新処理が正常に完了しました。")

        except (CsvFileError, DbConnectionError, DbOperationError, DbBrowserLaunchError) as e:
            self._logger.error(f"データベース更新処理中にエラーが発生しました: {e}")
            raise # 例外を再発生させ、上位で捕捉させる

    def _load_and_create_tables(self,
                                conn: sqlite3.Connection,
                                base_path: str,
                                csv_configs: List[CSVConfig]) -> None:
        """
        CSVファイルを読み込み、データベーステーブルを作成/更新します。
        """
        for config in csv_configs:
            file_path = self._csv_repo.get_csv_file_path(base_path, config.file_name)
            self._logger.info(f"CSVファイル '{config.file_name}' を読み込み、テーブル '{config.table_name}' を作成します。")
            df = self._csv_repo.read_csv_to_dataframe(file_path, config.encoding)
            self._db_repo.create_table_from_dataframe(conn, df, config.table_name)
            self._logger.info(f"テーブル '{config.table_name}' の作成が完了しました。")

    def _create_views(self,
                      conn: sqlite3.Connection,
                      simple_product_master_query: str,
                      environmental_research_query: str) -> None:
        """
        指定されたSQLクエリに基づいてデータベースビューを作成します。
        """
        self._logger.info("ビュー 'simple_product_master' を作成します。")
        self._db_repo.execute_query(conn, simple_product_master_query)
        self._logger.info("ビュー 'simple_product_master' が正常に作成されました。")

        self._logger.info("ビュー '環境調査' を作成します。")
        self._db_repo.execute_query(conn, environmental_research_query)
        self._logger.info("ビュー '環境調査' が正常に作成されました。")