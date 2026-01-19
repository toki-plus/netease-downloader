import sys
import traceback
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from style import STYLESHEET
from main_window import MainWindow

def global_exception_hook(exctype, value, tb):
    traceback_details = "".join(traceback.format_exception(exctype, value, tb))
    error_msg = (
        f"抱歉，程序遇到一个未处理的错误，即将退出。\n\n"
        f"错误类型: {exctype.__name__}\n"
        f"错误信息: {value}\n\n"
        f"详细信息已保存到 error.log 文件中。"
    )
    print(error_msg)
    print(traceback_details)
    try:
        with open("error.log", "a", encoding="utf-8") as f:
            f.write(f"--- {__import__('datetime').datetime.now()} ---\n")
            f.write(traceback_details)
            f.write("\n")
    except Exception as e:
        print(f"写入错误日志失败: {e}")
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setText("程序遇到严重错误")
    error_box.setInformativeText(f"{value}")
    error_box.setDetailedText(traceback_details)
    error_box.setStandardButtons(QMessageBox.Ok)
    error_box.exec_()
    sys.exit(1)
if __name__ == '__main__':
    sys.excepthook = global_exception_hook
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('assets/icon.png'))
    app.setApplicationName("Netease Music Toolbox")
    app.setStyle('Fusion')
    app.setStyleSheet(STYLESHEET)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())