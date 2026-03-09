class CsvDbProcessorError(Exception):
    """csv_db_processor パッケージ全体で使われるカスタム例外の基底クラス"""
    pass

class CsvFileError(CsvDbProcessorError):
    """CSVファイル関連のエラーを示す例外"""
    pass

class DbConnectionError(CsvDbProcessorError):
    """データベース接続関連のエラーを示す例外"""
    pass

class DbOperationError(CsvDbProcessorError):
    """データベース操作関連のエラーを示す例外"""
    pass

class DbBrowserLaunchError(CsvDbProcessorError):
    """DB Browser for SQLite 起動関連のエラーを示す例外"""
    pass

class ConfigurationError(CsvDbProcessorError):
    """設定関連のエラーを示す例外"""
    pass