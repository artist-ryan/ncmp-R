import logging
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from src.utils.config import Config
from src.utils.logger import Logger
from src.utils.notification import NotificationService
from src.validators.cookie import CookieValidator


def test_config():
    """测试配置加载"""
    try:
        config = Config()
        print("✅ 配置加载成功")
        
        # 打印配置信息（隐藏敏感信息）
        print("\n当前配置信息:")
        print(f"  MUSIC_U: {config.get('Cookie_MUSIC_U')[:20]}...（已隐藏）")
        print(f"  __csrf: {config.get('Cookie___csrf')}")
        print(f"  通知邮箱: {config.get('notify_email')}")
        print(f"  SMTP服务器: {config.get('smtp_server')}:{config.get('smtp_port')}")
        print(f"  等待时间: {config.get('wait_time_min')}~{config.get('wait_time_max')}秒")
        
        # 测试必要的配置项
        assert config.get("Cookie_MUSIC_U"), "Cookie_MUSIC_U 未配置"
        assert config.get("Cookie___csrf"), "Cookie___csrf 未配置"
        print("\n✅ 必要配置项验证通过")
        
        return config
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        raise

def test_cookie(config):
    """测试Cookie有效性"""
    try:
        logger = Logger()
        session = requests.Session()
        session.cookies.set("MUSIC_U", config.get("Cookie_MUSIC_U"))
        session.cookies.set("__csrf", config.get("Cookie___csrf"))
        
        print("\n验证Cookie...")
        validator = CookieValidator(session, logger)
        is_valid, message = validator.validate()
        
        if is_valid:
            print("✅ Cookie验证通过")
            return session, logger
        else:
            print(f"❌ Cookie验证失败: {message}")
            raise ValueError(message)
    except Exception as e:
        print(f"❌ Cookie测试失败: {str(e)}")
        raise

def test_notification(config, logger):
    """测试通知服务"""
    notifier = NotificationService(config, logger)
    if not config.get("notify_email"):
        print("⚠️ 未配置通知服务（可选）")
        return notifier
        
    print("\n通知服务配置:")
    print(f"  邮箱: {config.get('notify_email')}")
    print(f"  SMTP服务器: {config.get('smtp_server')}:{config.get('smtp_port')}")
    print("\n正在测试邮件发送...")
    
    try:
        notifier.send_notification(
            "网易云音乐合伙人 - 测试邮件",
            "这是一封测试邮件，如果你收到这封邮件，说明通知服务配置正确。\n\n"
            "当前配置:\n"
            f"- SMTP服务器: {config.get('smtp_server')}:{config.get('smtp_port')}\n"
            f"- 发送邮箱: {config.get('notify_email')}"
        )
        print("✅ 通知服务测试成功，请检查邮箱")
        return notifier
    except Exception as e:
        print(f"❌ 通知服务测试失败: {str(e)}")
        return None

def main():
    """运行测试"""
    try:
        print("开始测试...")
        print("-" * 50)
        
        # 1. 测试配置
        config = test_config()
        print("-" * 50)
        
        # 2. 测试Cookie
        session, logger = test_cookie(config)
        print("-" * 50)
        
        # 3. 测试通知服务
        notifier = test_notification(config, logger)
        if notifier is None:
            print("⚠️ 通知服务配置失败")
        print("-" * 50)
        
        print("✅ 所有配置测试通过")
        print("您可以运行 python main.py 开始执行任务")
            
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 