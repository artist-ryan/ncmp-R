import base64
import json
import os
from typing import Dict, Optional

import nacl.encoding
import nacl.public
import requests

from ..utils.logger import Logger


class GitHubService:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.api_base = "https://api.github.com"
        self.token = os.environ.get("GH_TOKEN")
        self.repo_owner = os.environ.get("GH_REPO").split("/")[0]
        self.repo_name = os.environ.get("GH_REPO", "").split("/")[-1]
        
        if not self.token:
            raise ValueError("GitHub Token未设置，无法更新Secrets")
        
        if not self.repo_owner or not self.repo_name:
            raise ValueError("GitHub仓库信息不完整")
            
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def get_public_key(self) -> Optional[Dict]:
        """获取仓库的公钥，用于加密secrets"""
        try:
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/actions/secrets/public-key"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                self.logger.error(f"获取公钥失败: {response.status_code} - {response.text}")
                return None
                
            return response.json()
        except Exception as e:
            self.logger.error(f"获取公钥时出错: {str(e)}")
            return None
    
    def encrypt_secret(self, public_key: str, public_key_id: str, secret_value: str) -> Dict:
        """使用仓库的公钥加密secret值"""
        try:
            # 解码公钥
            public_key_bytes = base64.b64decode(public_key)
            
            # 创建加密盒
            box = nacl.public.SealedBox(nacl.public.PublicKey(public_key_bytes))
            
            # 加密值
            encrypted = box.encrypt(secret_value.encode("utf-8"))
            encrypted_value = base64.b64encode(encrypted).decode("utf-8")
            
            return {
                "encrypted_value": encrypted_value,
                "key_id": public_key_id
            }
        except Exception as e:
            self.logger.error(f"加密secret时出错: {str(e)}")
            raise
    
    def update_secret(self, secret_name: str, secret_value: str) -> bool:
        """更新GitHub仓库中的secret"""
        try:
            # 获取公钥
            key_data = self.get_public_key()
            if not key_data:
                return False
                
            # 加密secret值
            encrypted_data = self.encrypt_secret(
                key_data["key"],
                key_data["key_id"],
                secret_value
            )
            
            # 更新secret
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/actions/secrets/{secret_name}"
            payload = {
                "encrypted_value": encrypted_data["encrypted_value"],
                "key_id": encrypted_data["key_id"]
            }
            
            response = requests.put(url, headers=self.headers, json=payload)
            
            if response.status_code not in (201, 204):
                self.logger.error(f"更新secret '{secret_name}'失败: {response.status_code} - {response.text}")
                return False
                
            self.logger.info(f"成功更新secret: {secret_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新secret '{secret_name}'时出错: {str(e)}")
            return False
    
    def update_cookies(self, cookies: Dict[str, str]) -> bool:
        """更新Cookie相关的secrets"""
        try:
            results = []
            for key, value in cookies.items():
                result = self.update_secret(key, value)
                results.append(result)
                
            return all(results)
        except Exception as e:
            self.logger.error(f"更新Cookies时出错: {str(e)}")
            return False
