import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional, Any
@dataclass
class CookieInfo:
    name: str
    value: str
    domain: str = ""
    path: str = "/"
    expires: Optional[int] = None
    secure: bool = False
    http_only: bool = False
class CookieException(Exception):
    pass
class CookieManager:
    def __init__(self, cookie_file: str = "cookie.txt"):
        self.cookie_file = Path(cookie_file)
        self.logger = logging.getLogger(__name__)
        self.important_cookies = {
            'MUSIC_U',
        }
        self._ensure_cookie_file_exists()
    def _ensure_cookie_file_exists(self) -> None:
        if not self.cookie_file.exists():
            self.cookie_file.touch()
            self.logger.info(f"创建Cookie文件: {self.cookie_file}")
    def read_cookie(self) -> str:
        try:
            if not self.cookie_file.exists():
                self.logger.warning(f"Cookie文件不存在: {self.cookie_file}")
                return ""
            content = self.cookie_file.read_text(encoding='utf-8').strip()
            if not content:
                self.logger.warning("Cookie文件为空")
                return ""
            self.logger.debug(f"成功读取Cookie文件，长度: {len(content)}")
            return content
        except UnicodeDecodeError as e:
            raise CookieException(f"Cookie文件编码错误: {e}")
        except PermissionError as e:
            raise CookieException(f"没有权限读取Cookie文件: {e}")
        except Exception as e:
            raise CookieException(f"读取Cookie文件失败: {e}")
    def write_cookie(self, cookie_content: str) -> bool:
        try:
            if not cookie_content or not cookie_content.strip():
                raise CookieException("Cookie内容不能为空")
            if not self.validate_cookie_format(cookie_content):
                raise CookieException("Cookie格式无效")
            self.cookie_file.write_text(cookie_content.strip(), encoding='utf-8')
            self.logger.info(f"成功写入Cookie到文件: {self.cookie_file}")
            return True
        except PermissionError as e:
            raise CookieException(f"没有权限写入Cookie文件: {e}")
        except Exception as e:
            raise CookieException(f"写入Cookie文件失败: {e}")
    def parse_cookies(self) -> Dict[str, str]:
        try:
            cookie_content = self.read_cookie()
            if not cookie_content:
                return {}
            return self.parse_cookie_string(cookie_content)
        except Exception as e:
            raise CookieException(f"解析Cookie失败: {e}")
    def parse_cookie_string(self, cookie_string: str) -> Dict[str, str]:
        if not cookie_string or not cookie_string.strip():
            return {}
        cookies = {}
        try:
            cookie_string = cookie_string.strip()
            cookie_pairs = []
            if ';' in cookie_string:
                cookie_pairs = cookie_string.split(';')
            elif '\n' in cookie_string:
                cookie_pairs = cookie_string.split('\n')
            else:
                cookie_pairs = [cookie_string]
            for pair in cookie_pairs:
                pair = pair.strip()
                if not pair or '=' not in pair:
                    continue
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    cookies[key] = value
            self.logger.debug(f"解析得到 {len(cookies)} 个Cookie项")
            return cookies
        except Exception as e:
            self.logger.error(f"解析Cookie字符串失败: {e}")
            return {}
    def validate_cookie_format(self, cookie_string: str) -> bool:
        if not cookie_string or not cookie_string.strip():
            return False
        try:
            cookies = self.parse_cookie_string(cookie_string)
            if not cookies:
                return False
            for name, value in cookies.items():
                if not name or not isinstance(name, str):
                    return False
                if not isinstance(value, str):
                    return False
                if any(char in name for char in [' ', '\t', '\n', '\r', ';', ',']):
                    return False
            return True
        except Exception:
            return False
    def is_cookie_valid(self) -> bool:
        try:
            cookies = self.parse_cookies()
            if not cookies:
                self.logger.debug("Cookie为空")
                return False
            music_u = cookies.get('MUSIC_U', '')
            if not music_u or len(music_u) < 10:
                self.logger.debug("MUSIC_U Cookie不存在或无效")
                return False
            self.logger.debug("Cookie验证通过 (MUSIC_U 有效)")
            return True
        except Exception as e:
            self.logger.error(f"Cookie验证失败: {e}")
            return False
    def get_cookie_info(self) -> Dict[str, Any]:
        try:
            cookies = self.parse_cookies()
            info = {
                'file_path': str(self.cookie_file),
                'file_exists': self.cookie_file.exists(),
                'file_size': self.cookie_file.stat().st_size if self.cookie_file.exists() else 0,
                'cookie_count': len(cookies),
                'is_valid': self.is_cookie_valid(),
                'important_cookies_present': list(self.important_cookies & set(cookies.keys())),
                'missing_important_cookies': list(self.important_cookies - set(cookies.keys())),
                'all_cookie_names': list(cookies.keys())
            }
            if self.cookie_file.exists():
                mtime = self.cookie_file.stat().st_mtime
                info['last_modified'] = datetime.fromtimestamp(mtime).isoformat()
            return info
        except Exception as e:
            return {
                'error': str(e),
                'file_path': str(self.cookie_file),
                'file_exists': False,
                'is_valid': False
            }
    def backup_cookie(self, backup_suffix: str = None) -> str:
        try:
            if not self.cookie_file.exists():
                raise CookieException("Cookie文件不存在，无法备份")
            if backup_suffix is None:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.cookie_file.with_suffix(f".{backup_suffix}.bak")
            content = self.cookie_file.read_text(encoding='utf-8')
            backup_path.write_text(content, encoding='utf-8')
            self.logger.info(f"Cookie备份成功: {backup_path}")
            return str(backup_path)
        except Exception as e:
            raise CookieException(f"备份Cookie文件失败: {e}")
    def restore_cookie(self, backup_path: str) -> bool:
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise CookieException(f"备份文件不存在: {backup_path}")
            backup_content = backup_file.read_text(encoding='utf-8')
            if not self.validate_cookie_format(backup_content):
                raise CookieException("备份文件中的Cookie格式无效")
            self.write_cookie(backup_content)
            self.logger.info(f"从备份恢复Cookie成功: {backup_path}")
            return True
        except Exception as e:
            raise CookieException(f"恢复Cookie失败: {e}")
    def clear_cookie(self) -> bool:
        try:
            if self.cookie_file.exists():
                self.cookie_file.write_text("", encoding='utf-8')
                self.logger.info("Cookie文件已清空")
            return True
        except Exception as e:
            self.logger.error(f"清空Cookie文件失败: {e}")
            return False
    def update_cookie(self, new_cookies: Dict[str, str]) -> bool:
        try:
            if not new_cookies:
                raise CookieException("新Cookie不能为空")
            existing_cookies = self.parse_cookies()
            existing_cookies.update(new_cookies)
            cookie_string = '; '.join(f"{k}={v}" for k, v in existing_cookies.items())
            return self.write_cookie(cookie_string)
        except Exception as e:
            self.logger.error(f"更新Cookie失败: {e}")
            return False
    def get_cookie_for_request(self) -> Dict[str, str]:
        try:
            cookies = self.parse_cookies()
            filtered_cookies = {k: v for k, v in cookies.items() if k and v}
            return filtered_cookies
        except Exception as e:
            self.logger.error(f"获取请求Cookie失败: {e}")
            return {}
    def format_cookie_string(self, cookies: Dict[str, str]) -> str:
        if not cookies:
            return ""
        return '; '.join(f"{k}={v}" for k, v in cookies.items() if k and v)
    def __str__(self) -> str:
        info = self.get_cookie_info()
        return f"CookieManager(file={info['file_path']}, valid={info['is_valid']}, count={info['cookie_count']})"
    def __repr__(self) -> str:
        return self.__str__()
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    manager = CookieManager()
    print("Cookie管理器模块")
    print("支持的功能:")
    print("- Cookie文件读写")
    print("- Cookie格式验证")
    print("- Cookie有效性检查")
    print("- Cookie备份和恢复")
    print("- Cookie信息查看")
    info = manager.get_cookie_info()
    print(f"\n当前Cookie状态: {manager}")
    print(f"详细信息: {info}")