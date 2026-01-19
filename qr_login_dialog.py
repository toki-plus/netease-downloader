from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread
from workers import QRLoginWorker
from cookie_manager import CookieManager
class QRLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("二维码登录")
        self.setFixedSize(300, 350)
        self.cookie_manager = CookieManager()
        layout = QVBoxLayout(self)
        self.qr_label = QLabel("正在生成二维码...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(280, 280)
        self.qr_label.setStyleSheet("border: 1px solid #ccc;")
        self.status_label = QLabel("请使用网易云音乐App扫描")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qr_label)
        layout.addWidget(self.status_label)
        self.start_login_flow()
    def start_login_flow(self):
        self.thread = QThread()
        self.worker = QRLoginWorker()
        self.worker.moveToThread(self.thread)
        self.worker.qr_ready.connect(self.display_qr_code)
        self.worker.status_update.connect(self.update_status)
        self.worker.login_success.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        self.thread.started.connect(self.worker.run)
        self.finished.connect(self.stop_worker)
        self.thread.start()
    def display_qr_code(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.qr_label.setPixmap(pixmap.scaled(280, 280, Qt.KeepAspectRatio))
    def update_status(self, message):
        self.status_label.setText(message)
    def on_login_success(self, cookie_str):
        try:
            current_cookies = self.cookie_manager.parse_cookies()
            new_cookies = self.cookie_manager.parse_cookie_string(cookie_str)
            current_cookies.update(new_cookies)
            full_cookie_str = self.cookie_manager.format_cookie_string(current_cookies)
            if self.cookie_manager.write_cookie(full_cookie_str):
                self.accept()
            else:
                self.on_login_error("登录成功，但保存Cookie失败。")
        except Exception as e:
            self.on_login_error(f"保存Cookie时出错: {e}")
    def on_login_error(self, message):
        QMessageBox.critical(self, "登录错误", message)
        self.reject()
    def stop_worker(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
    def closeEvent(self, event):
        self.stop_worker()
        super().closeEvent(event)