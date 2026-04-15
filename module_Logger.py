import os
import sys
import traceback
import threading

from logging import getLogger, Formatter, FileHandler, StreamHandler, DEBUG, ERROR, INFO

def loggingGetLogger(charactor_code):

    # logger定義
    logger = getLogger(__name__)

    # loggerのログレベルをDEBUGに設定（ここではとりあえず全レベルを出力対象とする）
    logger.setLevel(DEBUG)

    # ログ出力フォーマットを設定
    formatter = Formatter("%(asctime)s\t%(levelname)s\t%(funcName)s\t%(filename)s\tLine:%(lineno)d\t%(message)s")

    # スクリプトがあるディレクトリ（PyInstaller EXEにも対応）
    if getattr(sys, 'frozen', False):
        # PyInstaller実行時
        currentPath = os.path.dirname(sys.executable)
    else:
        # pyスクリプト実行時
        currentPath = os.path.dirname(os.path.abspath(__file__))

    # logフォルダのパスを作成
    logDir = os.path.join(currentPath, "log")
    os.makedirs(logDir, exist_ok=True)

    # 出力先ファイル フルパス
    from datetime import datetime
    logFileName = "error" + datetime.now().strftime("%Y%m%d") + "_" + charactor_code + ".log"
    logFilePath = os.path.join(logDir, logFileName)

    # ////////////////////////////////////////
    # ファイル出力するためのFileHandlerを設定
    # ////////////////////////////////////////
    file_handler = FileHandler(logFilePath, encoding=charactor_code)
    file_handler.setLevel(ERROR)
    file_handler.setFormatter(formatter)
    
    # ////////////////////////////////////////
    # コンソールに出力するためのStreamHandlerを設定
    # ////////////////////////////////////////
    # stream_handler = StreamHandler()
    # stream_handler.setFormatter(formatter)
    # stream_handler.setLevel(INFO)
    
    # loggerにハンドラーを追加（hasHandlersを使用しないとログが積み重なってしまうため。）
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        # logger.addHandler(stream_handler)

    # 例外を自動でログ出力する関数を追加
    def error_exception(exc: Exception):
        # スタックトレースを文字列化
        tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        # 発生箇所を1行目だけ簡単に取得
        try:
            last_tb = exc.__traceback__
            while last_tb.tb_next:
                last_tb = last_tb.tb_next
            filename = os.path.basename(last_tb.tb_frame.f_code.co_filename)
            lineno = last_tb.tb_lineno
            funcname = last_tb.tb_frame.f_code.co_name
            location = f"{filename}::{funcname}() Line:{lineno}"
        except Exception:
            location = "発生箇所不明"
        msg = f"\n[{location}]:\n{tb_str}"
        logger.error(msg)
        return msg

    # error_exception関数を logger にバインド
    logger.error_exception = error_exception

    # --------------------------------
    # 未捕捉例外
    # --------------------------------
    def handle_exception(exc_type, exc_value, exc_traceback):

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        exc = exc_value
        logger.error_exception(exc)

    sys.excepthook = handle_exception

    # --------------------------------
    # スレッド例外
    # --------------------------------
    def thread_exception(args):
        logger.error_exception(args.exc_value)

    if hasattr(threading, "excepthook"):
        threading.excepthook = thread_exception

    return logger

# logger.debug("debug")
# logger.info("info")
# logger.warning("warning")
# logger.error("error")
# logger.critical("critical")

