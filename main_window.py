import os
import re
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
                             QStackedWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QComboBox,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
                             QTextBrowser, QProgressBar, QSpinBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QThread, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from workers import SearchWorker, ParseWorker, PlaylistAlbumWorker, DownloadWorker
from qr_login_dialog import QRLoginDialog
from cookie_manager import CookieManager
import resources_rc
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网易云音乐工具箱")
        self.setGeometry(100, 100, 900, 800)
        self.setMinimumSize(800, 600)
        self.cookie_manager = CookieManager()
        self.worker_thread = None
        self.worker = None
        self._init_ui()
        self._init_menu()
        self.check_login_status()
    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        controls_group = QGroupBox("功能选择与操作")
        controls_layout = QGridLayout(controls_group)
        controls_layout.setSpacing(10)
        main_layout.addWidget(controls_group)
        controls_layout.addWidget(QLabel("选择功能:"), 0, 0, Qt.AlignTop)
        radio_button_container = QWidget()
        radio_layout = QHBoxLayout(radio_button_container)
        radio_layout.setContentsMargins(0, 0, 0, 0)
        radio_layout.setSpacing(20)
        self.mode_group = QButtonGroup(self)
        self.radio_search = QRadioButton("歌曲搜索")
        self.radio_parse = QRadioButton("单曲解析")
        self.radio_list = QRadioButton("歌单/专辑解析")
        self.radio_download = QRadioButton("音乐下载")
        self.radio_search.setChecked(True)
        radio_layout.addWidget(self.radio_search)
        radio_layout.addWidget(self.radio_parse)
        radio_layout.addWidget(self.radio_list)
        radio_layout.addWidget(self.radio_download)
        radio_layout.addStretch(1)
        self.mode_group.addButton(self.radio_search, 0)
        self.mode_group.addButton(self.radio_parse, 1)
        self.mode_group.addButton(self.radio_list, 2)
        self.mode_group.addButton(self.radio_download, 3)
        controls_layout.addWidget(radio_button_container, 0, 1)
        controls_layout.setColumnStretch(1, 1)
        self.stacked_widget = QStackedWidget()
        controls_layout.addWidget(self.stacked_widget, 1, 0, 1, 2)
        self.stacked_widget.addWidget(self._create_search_page())
        self.stacked_widget.addWidget(self._create_parse_page())
        self.stacked_widget.addWidget(self._create_list_page())
        self.stacked_widget.addWidget(self._create_download_page())
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["歌名", "歌手", "专辑", "ID"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.setMinimumHeight(200)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        main_layout.addWidget(self.results_table)
        self.detail_widget = QWidget()
        detail_layout = QHBoxLayout(self.detail_widget)
        self.cover_label = QLabel("封面")
        self.cover_label.setFixedSize(150, 150)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("border: 1px solid #4A4E60; border-radius: 5px;")
        info_v_layout = QVBoxLayout()
        info_v_layout.setSpacing(5)
        self.info_browser = QTextBrowser()
        self.info_browser.setOpenExternalLinks(True)
        self.lyric_browser = QTextBrowser()
        info_v_layout.addWidget(QLabel("歌曲信息:"))
        info_v_layout.addWidget(self.info_browser, 1)
        info_v_layout.addWidget(QLabel("歌词:"))
        info_v_layout.addWidget(self.lyric_browser, 1)
        detail_layout.addWidget(self.cover_label)
        detail_layout.addLayout(info_v_layout)
        main_layout.addWidget(self.detail_widget)
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.login_status_label = QLabel("未登录")
        self.status_bar.addWidget(self.login_status_label)
        self.mode_group.idClicked.connect(self.stacked_widget.setCurrentIndex)
        self.results_table.doubleClicked.connect(self.on_table_double_clicked)
    def _init_menu(self):
        menu_bar = self.menuBar()
        account_menu = menu_bar.addMenu("登录")
        login_action = account_menu.addAction("二维码登录")
        login_action.triggered.connect(self.open_qr_login)
        logout_action = account_menu.addAction("退出登录")
        logout_action.triggered.connect(self.logout)
        help_menu = menu_bar.addMenu("帮助")
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)
    def _create_search_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(0, 5, 0, 5)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词...")
        self.search_limit = QSpinBox()
        self.search_limit.setRange(1, 100)
        self.search_limit.setValue(20)
        self.search_btn = QPushButton("搜索")
        layout.addWidget(QLabel("关键词:"), 0, 0)
        layout.addWidget(self.search_input, 0, 1)
        layout.addWidget(QLabel("数量:"), 0, 2)
        layout.addWidget(self.search_limit, 0, 3)
        layout.addWidget(self.search_btn, 0, 4)
        layout.setColumnStretch(1, 1)
        self.search_btn.clicked.connect(self.start_search)
        return page
    def _create_parse_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(0, 5, 0, 5)
        self.parse_input = QLineEdit()
        self.parse_input.setPlaceholderText("输入歌曲ID或URL...")
        self.parse_quality_combo = self._create_quality_combo()
        self.parse_btn = QPushButton("解析")
        layout.addWidget(QLabel("ID/URL:"), 0, 0)
        layout.addWidget(self.parse_input, 0, 1)
        layout.addWidget(QLabel("音质:"), 0, 2)
        layout.addWidget(self.parse_quality_combo, 0, 3)
        layout.addWidget(self.parse_btn, 0, 4)
        layout.setColumnStretch(1, 1)
        self.parse_btn.clicked.connect(self.start_parse)
        return page
    def _create_list_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(0, 5, 0, 5)
        self.list_input = QLineEdit()
        self.list_input.setPlaceholderText("输入歌单或专辑ID/URL...")
        self.list_type_combo = QComboBox()
        self.list_type_combo.addItems(["歌单", "专辑"])
        self.list_btn = QPushButton("解析列表")
        layout.addWidget(QLabel("类型:"), 0, 0)
        layout.addWidget(self.list_type_combo, 0, 1)
        layout.addWidget(QLabel("ID/URL:"), 0, 2)
        layout.addWidget(self.list_input, 0, 3)
        layout.addWidget(self.list_btn, 0, 4)
        layout.setColumnStretch(3, 1)
        self.list_btn.clicked.connect(self.start_list_parse)
        return page
    def _create_download_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(0, 5, 0, 5)
        self.download_input = QLineEdit()
        self.download_input.setPlaceholderText("输入歌曲ID或URL...")
        self.download_quality_combo = self._create_quality_combo(default='lossless')
        self.download_btn = QPushButton("下载")
        self.open_folder_btn = QPushButton("打开目录")
        layout.addWidget(QLabel("ID/URL:"), 0, 0)
        layout.addWidget(self.download_input, 0, 1)
        layout.addWidget(QLabel("音质:"), 0, 2)
        layout.addWidget(self.download_quality_combo, 0, 3)
        layout.addWidget(self.download_btn, 0, 4)
        layout.addWidget(self.open_folder_btn, 0, 5)
        layout.setColumnStretch(1, 1)
        self.download_btn.clicked.connect(self.start_download)
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        return page
    def _create_quality_combo(self, default='standard'):
        combo = QComboBox()
        qualities = {
            'standard': '标准音质', 'exhigh': '极高音质', 'lossless': '无损音质',
            'hires': 'Hi-Res音质', 'sky': '沉浸环绕声', 'jyeffect': '高清环绕声', 'jymaster': '超清母带'
        }
        for value, name in qualities.items():
            combo.addItem(name, value)
        if default in qualities:
            index = combo.findData(default)
            if index != -1:
                combo.setCurrentIndex(index)
        return combo
    def _extract_id(self, text):
        text = text.strip()
        match = re.search(r'id=(\d+)', text)
        if match:
            return match.group(1)
        if text.isdigit():
            return text
        return ""
    def _is_task_running(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.show_error("请等待当前任务完成。")
            return True
        return False
    def _setup_worker(self, worker_class, *args):
        self.worker_thread = QThread()
        self.worker = worker_class(*args)
        self.worker.moveToThread(self.worker_thread)
        self.worker.error.connect(self.on_worker_error)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self._clear_worker_refs)
        return self.worker, self.worker_thread
    def _clear_worker_refs(self):
        self.worker = None
        self.worker_thread = None
    def start_search(self):
        if self._is_task_running():
            return
        keywords = self.search_input.text().strip()
        if not keywords:
            self.show_error("请输入搜索关键词。")
            return
        limit = self.search_limit.value()
        self.search_btn.setEnabled(False)
        self.status_bar.showMessage(f"正在搜索: {keywords}...")

        worker, thread = self._setup_worker(SearchWorker, keywords, limit)
        worker.finished.connect(self.on_search_finished)
        thread.start()
    def on_search_finished(self, results):
        self.results_table.setRowCount(0)
        if not results:
            self.status_bar.showMessage("未找到结果。", 5000)
        else:
            self.results_table.setRowCount(len(results))
            for row, song in enumerate(results):
                self.results_table.setItem(row, 0, QTableWidgetItem(song['name']))
                self.results_table.setItem(row, 1, QTableWidgetItem(song['artists']))
                self.results_table.setItem(row, 2, QTableWidgetItem(song['album']))
                self.results_table.setItem(row, 3, QTableWidgetItem(str(song['id'])))
            self.status_bar.showMessage(f"搜索完成，找到 {len(results)} 首歌曲。", 5000)
        self.search_btn.setEnabled(True)
    def start_parse(self):
        if self._is_task_running():
            return
        song_id_text = self.parse_input.text().strip()
        song_id = self._extract_id(song_id_text)
        if not song_id:
            self.show_error("请输入有效的歌曲ID或URL。")
            return
        quality = self.parse_quality_combo.currentData()
        self.parse_btn.setEnabled(False)
        self.status_bar.showMessage(f"正在解析歌曲: {song_id}...")
        worker, thread = self._setup_worker(ParseWorker, song_id, quality)
        worker.finished.connect(self.on_parse_finished)
        worker.cover_ready.connect(self.update_cover)
        thread.start()
    def on_parse_finished(self, song_info):
        if song_info:
            html_info = f"""
            <style>
                b {{ color: #25F4EE; }}
                a {{ color: #FE2C55; text-decoration: none; }}
            </style>
            <b>歌名:</b> {song_info['name']}<br>
            <b>歌手:</b> {song_info['ar_name']}<br>
            <b>专辑:</b> {song_info['al_name']}<br>
            <b>音质:</b> {song_info['level']}<br>
            <b>大小:</b> {song_info['size']}<br>
            <b>URL:</b> <a href="{song_info['url']}">右键复制链接或点击下载</a>
            """
            self.info_browser.setHtml(html_info)
            self.lyric_browser.setText(song_info.get('lyric', '无歌词信息。'))
            self.status_bar.showMessage(f"歌曲 '{song_info['name']}' 解析成功。", 5000)
        else:
            self.status_bar.showMessage("解析失败，未获取到歌曲信息。", 5000)
        self.parse_btn.setEnabled(True)
    def start_list_parse(self):
        if self._is_task_running():
            return
        list_id_text = self.list_input.text().strip()
        list_id = self._extract_id(list_id_text)
        list_type = "playlist" if self.list_type_combo.currentIndex() == 0 else "album"
        if not list_id:
            self.show_error("请输入有效的歌单或专辑ID/URL。")
            return
        self.list_btn.setEnabled(False)
        self.status_bar.showMessage(f"正在解析{self.list_type_combo.currentText()}: {list_id}...")
        worker, thread = self._setup_worker(PlaylistAlbumWorker, list_id, list_type)
        worker.finished.connect(self.on_list_parse_finished)
        thread.start()
    def on_list_parse_finished(self, data):
        tracks_key = 'tracks' if data and 'tracks' in data else 'songs'
        if data and data.get(tracks_key):
            self.results_table.setRowCount(0)
            songs = data[tracks_key]
            self.results_table.setRowCount(len(songs))
            for row, song in enumerate(songs):
                self.results_table.setItem(row, 0, QTableWidgetItem(song['name']))
                self.results_table.setItem(row, 1, QTableWidgetItem(song['artists']))
                self.results_table.setItem(row, 2, QTableWidgetItem(song['album']))
                self.results_table.setItem(row, 3, QTableWidgetItem(str(song['id'])))
            self.status_bar.showMessage(f"解析完成，共 {len(songs)} 首歌曲。", 5000)
        else:
            self.status_bar.showMessage("解析列表失败或列表为空。", 5000)
        self.list_btn.setEnabled(True)
    def start_download(self):
        if self._is_task_running():
            return
        music_id_text = self.download_input.text().strip()
        music_id = self._extract_id(music_id_text)
        if not music_id:
            self.show_error("请输入有效的歌曲ID或URL。")
            return
        quality = self.download_quality_combo.currentData()
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"准备下载: {music_id}...")
        worker, thread = self._setup_worker(DownloadWorker, music_id, quality)
        worker.finished.connect(self.on_download_finished)
        worker.progress.connect(self.on_download_progress)
        worker.download_started.connect(lambda name: self.status_bar.showMessage(f"正在下载: {name}"))
        thread.start()
    def on_download_progress(self, value):
        self.progress_bar.setValue(value)
    def on_download_finished(self, result):
        if result and result.get('success'):
            self.status_bar.showMessage(f"下载完成: {os.path.basename(result['file_path'])}", 10000)
            QMessageBox.information(self, "下载完成", f"文件已保存至:\n{result['file_path']}")
        elif result:
            self.show_error(f"下载失败: {result['error_message']}")
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
    def on_worker_error(self, error_msg):
        self.show_error(error_msg)
        for btn in [self.search_btn, self.parse_btn, self.list_btn, self.download_btn]:
            btn.setEnabled(True)
        self.status_bar.showMessage("操作失败", 5000)
        self.progress_bar.setVisible(False)
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
    def on_table_double_clicked(self, index):
        if self._is_task_running():
            return
        row = index.row()
        song_id_item = self.results_table.item(row, 3)
        if song_id_item:
            song_id = song_id_item.text()
            parse_page_index = self.mode_group.id(self.radio_parse)
            self.radio_parse.setChecked(True)
            self.stacked_widget.setCurrentIndex(parse_page_index)
            self.parse_input.setText(song_id)
            self.start_parse()
    def update_cover(self, image_data):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.cover_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    def open_download_folder(self):
        path = os.path.abspath("downloads")
        if not os.path.exists(path):
            os.makedirs(path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    def open_qr_login(self):
        dialog = QRLoginDialog(self)
        if dialog.exec_() == QRLoginDialog.Accepted:
            self.check_login_status()
            QMessageBox.information(self, "成功", "登录成功！Cookie已保存。")
        else:
            self.status_bar.showMessage("登录取消或失败", 5000)
    def check_login_status(self):
        if self.cookie_manager.is_cookie_valid():
            self.login_status_label.setText("状态: 已登录")
            self.login_status_label.setObjectName("status_label_ok")
        else:
            self.login_status_label.setText("状态: 未登录")
            self.login_status_label.setObjectName("status_label_error")
        self.login_status_label.style().unpolish(self.login_status_label)
        self.login_status_label.style().polish(self.login_status_label)
    def logout(self):
        if self.cookie_manager.clear_cookie():
            self.check_login_status()
            QMessageBox.information(self, "成功", "已退出登录。")
        else:
            self.show_error("退出登录失败。")
    def show_about(self):
        QMessageBox.about(self, "关于", "网易云音乐工具箱 v1.0\n\n一个基于PyQt5的桌面工具，用于解析和下载网易云音乐。")
    def show_error(self, message):
        QMessageBox.critical(self, "错误", message)
    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            if not self.worker_thread.wait(3000):
                print("警告: 后台线程在3秒内未能停止，将强制终止。")
                self.worker_thread.terminate()
                self.worker_thread.wait()
        event.accept()