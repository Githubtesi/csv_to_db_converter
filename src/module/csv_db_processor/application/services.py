from src.module.csv_db_processor.application.commands import DatabaseUpdateCommand
from src.module.csv_db_processor.domain.interfaces import ILogger
from src.module.csv_db_processor.domain.services import DbGenerationService
from src.module.shared.exceptions import CsvDbProcessorError


class DatabaseUpdater:
    """
    データベース更新のユースケースを表現するアプリケーションサービス。
    Presentation層からのコマンドを受け取り、ドメインサービスを呼び出してビジネスロジックを実行します。
    エラー発生時には、ロギングを行い、Presentation層に適切な例外を伝播させます。
    """

    def __init__(self, db_generation_service: DbGenerationService, logger: ILogger) -> None:
        self._db_generation_service: DbGenerationService = db_generation_service
        self._logger: ILogger = logger

    def execute(self, command: DatabaseUpdateCommand) -> None:
        """
        DatabaseUpdateCommand に従ってデータベース更新処理を実行します。

        Args:
            command: データベース更新に必要な情報を含むコマンドオブジェクト。

        Raises:
            CsvDbProcessorError: データベース更新処理中に発生した全てのエラーの基底クラス。
        """
        self._logger.info("DatabaseUpdater: 実行コマンドを受け取りました。")
        try:
            self._db_generation_service.process_database_update(
                server_csv_dir_path=command.server_csv_dir_path,
                db_file_path=command.db_file_path,
                smile_csv_configs=command.smile_csv_configs,
                my_csv_configs=command.my_csv_configs,
                db_browser_app_path=command.db_browser_app_path,
                create_simple_product_master_view_query=command.create_simple_product_master_view_query,
                create_environmental_research_view_query=command.create_environmental_research_view_query
            )
            self._logger.info("DatabaseUpdater: データベース更新処理が正常に完了しました。")
        except CsvDbProcessorError as e:
            # ドメインサービスから伝播された具体的なエラーを再度ロギングし、上位に伝播
            self._logger.error(f"DatabaseUpdater: データベース更新処理中にエラーが発生しました: {e}")
            raise # Presentation層にエラーを伝えるために再発生