from typing import Tuple

import requests

from ..utils.logger import Logger


class CookieValidator:
    def __init__(self, session: requests.Session, logger: Logger):
        self.session = session
        self.logger = logger
        self.check_urls = {
            "user_info": "https://music.163.com/api/nuser/account/get",
            "task_data": "https://interface.music.163.com/api/music/partner/daily/task/get"
        }

    def validate(self) -> Tuple[bool, str]:
        """验证Cookie是否有效"""
        try:
            if not self._check_cookie_exists():
                return False, "Cookie未正确设置"

            if not self._check_user_info():
                return False, "Cookie已失效或账号信息不完整"

            if not self._check_task_access():
                return False, "当前账号可能没有音乐合伙人权限"
            
            return True, "Cookie有效"
            
        except Exception as e:
            return False, f"Cookie验证失败: {str(e)}"
            
    def _check_cookie_exists(self) -> bool:
        """检查必要的Cookie是否存在"""
        return bool(
            self.session.cookies.get("MUSIC_U") and 
            self.session.cookies.get("__csrf")
        )
        
    def _check_user_info(self) -> bool:
        """检查用户信息是否有效"""
        response = self.session.get(self.check_urls["user_info"]).json()
        return bool(response.get("code") == 200 and response.get("profile"))
        
    def _check_task_access(self) -> bool:
        """检查是否有任务访问权限"""
        response = self.session.get(self.check_urls["task_data"]).json()
        return response.get("code") == 200 