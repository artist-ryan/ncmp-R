import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from src.core.tasks.cookie_refresh import CookieRefreshTask
from src.utils.config import Config
from src.utils.logger import Logger
from src.utils.notification import NotificationService



def main():
    try:
        # 初始化基础组件
        config = Config()
        logger = Logger()
        notifier = NotificationService(config, logger)
        
        if not os.environ.get("NETEASE_PHONE") and config.get("netease_phone"):
            os.environ["NETEASE_PHONE"] = config.get("netease_phone")
            
        if not os.environ.get("NETEASE_PASSWORD") and config.get("netease_password"):
            os.environ["NETEASE_PASSWORD"] = config.get("netease_password")
            
        if not os.environ.get("NETEASE_MD5_PASSWORD") and config.get("netease_md5_password"):
            os.environ["NETEASE_MD5_PASSWORD"] = config.get("netease_md5_password")
            
        if not os.environ.get("GH_TOKEN") and config.get("gh_token"):
            os.environ["GH_TOKEN"] = config.get("gh_token")
            
        if not os.environ.get("GH_REPO") and config.get("gh_repo"):
            os.environ["GH_REPO"] = config.get("gh_repo")
        
        # 初始化并执行刷新任务
        task = CookieRefreshTask(logger, notifier)
        success = task.execute()
        
        # 处理执行结果
        if success:
            logger.info("✅ Cookie刷新成功")
        else:
            logger.error("❌ Cookie刷新失败")
            
    except Exception as e:
        error_message = f"Cookie刷新程序异常: {str(e)}"
        logger = Logger()
        logger.error(error_message)
        
        try:
            config = Config()
            notifier = NotificationService(config, logger)
            notifier.send_notification(
                "网易云音乐合伙人 - Cookie刷新异常",
                error_message
            )
        except Exception as notify_error:
            logger.error(f"发送异常通知时出错: {str(notify_error)}")


if __name__ == "__main__":
    main()
