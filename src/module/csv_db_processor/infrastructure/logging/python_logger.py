import logging
from src.module.csv_db_processor.domain.interfaces import ILogger
from src.module.csv_db_processor.infrastructure.config import ERROR_LOG_FILE_NAME


class PythonLogger(ILogger):
    """
    Pythonの標準loggingモジュールを使用したILoggerインターフェースの実装。
    エラーログはファイルにも出力されます。
    """
    def __init__(self, name: str = "csv_db_processor_logger") -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO) # デフォルトはINFOレベル

        # ハンドラがすでに設定されている場合は重複を避ける
        if not self._logger.handlers:
            # コンソールハンドラ
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)

            # ファイルハンドラ (エラーログ用)
            file_handler = logging.FileHandler(ERROR_LOG_FILE_NAME, encoding="utf-8")
            file_handler.setLevel(logging.ERROR) # ERRORレベル以上をファイルに出力
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)

    def critical(self, message: str, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self._logger.warning(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs)