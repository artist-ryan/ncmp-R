import requests
import re
from typing import Dict, Tuple, Optional
from ..utils.logger import Logger


class AuthService:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.login_api = "https://ncma-web.vercel.app/login/cellphone"
        
    def login(self, phone: str, password: str = None, md5_password: str = None) -> Tuple[bool, Optional[Dict[str, str]]]:
        """
        通过手机号和密码登录获取 Cookie
        
        Args:
            phone: 手机号
            password: 明文密码（与md5_password二选一）
            md5_password: MD5加密后的密码（与password二选一）
            
        Returns:
            (成功状态, Cookie字典)
        """
        try:
            self.logger.info(f"尝试登录账号: {phone[:3]}****{phone[-4:]}")
            
            # 构建参数，优先使用md5_password
            params = {"phone": phone}
            
            if md5_password:
                params["md5_password"] = md5_password
                self.logger.debug("使用MD5加密密码登录")
            elif password:
                params["password"] = password
                self.logger.debug("使用明文密码登录")
            else:
                self.logger.error("未提供密码，无法登录")
                return False, None
            
            # 发送登录请求
            response = requests.get(self.login_api, params=params)
            
            # 检查响应状态
            if response.status_code != 200:
                self.logger.error(f"登录请求失败，状态码: {response.status_code}")
                return False, None
            
            # 解析响应数据
            response_data = response.json()
            if response_data.get("code") != 200:
                self.logger.error(f"登录失败: {response_data.get('message', '未知错误')}")
                return False, None
            
            # 从响应中获取Cookie
            music_u = None
            csrf = None
            
            # 首先尝试从cookies对象获取
            cookies = response.cookies
            music_u = cookies.get("MUSIC_U")
            csrf = cookies.get("__csrf")
            
            # 如果上面方法没有获取到，尝试解析响应中的cookie字段
            if (not music_u or not csrf) and "cookie" in response_data:
                cookie_str = response_data["cookie"]
                
                # 提取MUSIC_U
                music_u_match = re.search(r'MUSIC_U=([^;]+)', cookie_str)
                if music_u_match:
                    music_u = music_u_match.group(1)
                
                # 提取__csrf
                csrf_match = re.search(r'__csrf=([^;]+)', cookie_str)
                if csrf_match:
                    csrf = csrf_match.group(1)
            
            # 最后一种方法，尝试从Set-Cookie头部获取
            if not music_u or not csrf:
                cookie_header = response.headers.get("Set-Cookie", "")
                if not music_u:
                    music_u_match = re.search(r'MUSIC_U=([^;]+)', cookie_header)
                    if music_u_match:
                        music_u = music_u_match.group(1)
                if not csrf:
                    csrf_match = re.search(r'__csrf=([^;]+)', cookie_header)
                    if csrf_match:
                        csrf = csrf_match.group(1)
            
            if not music_u:
                self.logger.error("未能从响应中提取MUSIC_U")
                return False, None
                
            if not csrf:
                self.logger.error("未能从响应中提取__csrf")
                return False, None
                
            cookie_dict = {
                "Cookie_MUSIC_U": music_u,
                "Cookie___csrf": csrf
            }
            
            self.logger.info("登录成功并获取Cookie")
            self.logger.debug(f"成功获取MUSIC_U: {music_u[:10]}... 和 __csrf: {csrf}")
            
            return True, cookie_dict
            
        except Exception as e:
            self.logger.error(f"登录过程发生异常: {str(e)}")
            return False, None
