import requests
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from music_api import NeteaseAPI, APIException, QRLoginManager
from music_downloader import MusicDownloader, DownloadException
from cookie_manager import CookieManager
class Worker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.api = NeteaseAPI()
        self.cookie_manager = CookieManager()
    def get_cookies(self):
        return self.cookie_manager.parse_cookies()
class SearchWorker(Worker):
    def __init__(self, keywords, limit):
        super().__init__()
        self.keywords = keywords
        self.limit = limit
    @pyqtSlot()
    def run(self):
        try:
            results = self.api.search_music(self.keywords, self.get_cookies(), self.limit)
            self.finished.emit(results)
        except APIException as e:
            self.error.emit(f"搜索失败: {e}")
        except Exception as e:
            self.error.emit(f"发生未知错误: {e}")
class ParseWorker(Worker):
    cover_ready = pyqtSignal(bytes)
    def __init__(self, song_id, quality):
        super().__init__()
        self.song_id = song_id
        self.quality = quality
    @pyqtSlot()
    def run(self):
        try:
            cookies = self.get_cookies()
            song_info = self.api.get_song_detail(self.song_id)
            if not song_info or 'songs' not in song_info or not song_info['songs']:
                raise APIException("未找到歌曲信息")
            song_data = song_info['songs'][0]
            url_info = self.api.get_song_url(self.song_id, self.quality, cookies)
            lyric_info = self.api.get_lyric(self.song_id, cookies)
            pic_url = song_data.get('al', {}).get('picUrl', '')
            if pic_url:
                try:
                    response = requests.get(pic_url)
                    response.raise_for_status()
                    self.cover_ready.emit(response.content)
                except Exception:
                    pass
            response_data = {
                'id': self.song_id,
                'name': song_data.get('name', ''),
                'ar_name': ', '.join(artist['name'] for artist in song_data.get('ar', [])),
                'al_name': song_data.get('al', {}).get('name', ''),
                'pic': pic_url,
                'lyric': lyric_info.get('lrc', {}).get('lyric', ''),
                'tlyric': lyric_info.get('tlyric', {}).get('lyric', ''),
            }
            if url_info and url_info.get('data') and len(url_info['data']) > 0:
                url_data = url_info['data'][0]
                size_bytes = url_data.get('size', 0)
                size_formatted = f"{size_bytes / (1024*1024):.2f} MB" if size_bytes > 0 else "N/A"
                response_data.update({
                    'url': url_data.get('url', ''),
                    'size': size_formatted,
                    'level': url_data.get('level', self.quality)
                })
            else:
                response_data.update({'url': '', 'size': '获取失败', 'level': self.quality})
            self.finished.emit(response_data)
        except APIException as e:
            self.error.emit(f"解析失败: {e}")
        except Exception as e:
            self.error.emit(f"发生未知错误: {e}")
class PlaylistAlbumWorker(Worker):
    def __init__(self, list_id, list_type):
        super().__init__()
        self.list_id = list_id
        self.list_type = list_type
    @pyqtSlot()
    def run(self):
        try:
            cookies = self.get_cookies()
            if self.list_type == "playlist":
                result = self.api.get_playlist_detail(self.list_id, cookies)
            else:
                result = self.api.get_album_detail(self.list_id, cookies)
            self.finished.emit(result)
        except APIException as e:
            self.error.emit(f"解析 {self.list_type} 失败: {e}")
        except Exception as e:
            self.error.emit(f"发生未知错误: {e}")
class DownloadWorker(Worker):
    progress = pyqtSignal(int)
    download_started = pyqtSignal(str)
    def __init__(self, music_id, quality):
        super().__init__()
        self.music_id = music_id
        self.quality = quality
        self.downloader = MusicDownloader()
    def _download_with_progress(self, music_info):
        try:
            self.download_started.emit(f"{music_info.artists} - {music_info.name}")
            response = requests.get(music_info.download_url, stream=True, timeout=60)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0: total_size = music_info.file_size
            filename = f"{music_info.artists} - {music_info.name}"
            safe_filename = self.downloader._sanitize_filename(filename)
            file_ext = self.downloader._determine_file_extension(music_info.download_url, response.headers.get('Content-Type', ''))
            file_path = self.downloader.download_dir / f"{safe_filename}{file_ext}"
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress_percent = int((downloaded_size / total_size) * 100)
                            self.progress.emit(progress_percent)
            self.progress.emit(100)
            self.downloader._write_music_tags(file_path, music_info)
            return {'success': True, 'file_path': str(file_path)}
        except Exception as e:
            return {'success': False, 'error_message': str(e)}
    @pyqtSlot()
    def run(self):
        try:
            music_info = self.downloader.get_music_info(self.music_id, self.quality)
            result = self._download_with_progress(music_info)
            if result['success']:
                self.finished.emit(result)
            else:
                self.error.emit(result['error_message'])
        except DownloadException as e:
            self.error.emit(f"下载准备失败: {e}")
        except Exception as e:
            self.error.emit(f"发生未知错误: {e}")
class QRLoginWorker(QObject):
    qr_ready = pyqtSignal(bytes)
    status_update = pyqtSignal(str)
    login_success = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.qr_manager = QRLoginManager()
        self.unikey = None
        self._is_running = True
    @pyqtSlot()
    def run(self):
        try:
            import qrcode
            from io import BytesIO
            self.status_update.emit("正在生成二维码Key...")
            self.unikey = self.qr_manager.generate_qr_key()
            if not self.unikey:
                raise Exception("生成二维码Key失败")
            qr_url = f'https://music.163.com/login?codekey={self.unikey}'
            img = qrcode.make(qr_url)
            buffer = BytesIO()
            img.save(buffer, "PNG")
            self.qr_ready.emit(buffer.getvalue())
            while self._is_running:
                code, cookies = self.qr_manager.check_qr_login(self.unikey)
                if code == 800:
                    self.status_update.emit("二维码已过期，请关闭重试。")
                    break
                elif code == 801:
                    self.status_update.emit("等待扫码...")
                elif code == 802:
                    self.status_update.emit("扫码成功，请在手机上确认登录...")
                elif code == 803:
                    self.status_update.emit("登录成功！")
                    cookie_str = f"MUSIC_U={cookies['MUSIC_U']}"
                    self.login_success.emit(cookie_str)
                    break
                else:
                    self.status_update.emit(f"状态码: {code}")
                QThread.sleep(2)
        except ImportError:
            self.error.emit("请安装 qrcode 库 (pip install qrcode)")
        except Exception as e:
            self.error.emit(f"登录时出错: {e}")
    def stop(self):
        self._is_running = False
