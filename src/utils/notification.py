import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from .config import Config
from .logger import Logger


class NotificationService:
    def __init__(self, config: 'Config', logger: Logger):
        self.config = config
        self.logger = logger
        
    def send_notification(self, subject: str, content: str) -> bool:
        """发送通知邮件"""
        notify_email = self.config.get("notify_email")
        if not notify_email:
            self.logger.info("未配置通知邮箱，跳过通知发送")
            return False
            
        email_password = self.config.get("email_password")
        if not email_password:
            self.logger.warning("未配置邮箱密码，无法发送通知")
            return False
            
        smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
        smtp_ssl_port = int(self.config.get("smtp_port", 465)) 
        smtp_tls_port = 587 

        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = notify_email
        msg['To'] = notify_email
        msg['Subject'] = subject
        
        body = MIMEText(content, 'plain', 'utf-8')
        msg.attach(body)
        
        email_sent_successfully = False

        # 尝试使用 SSL 连接发送邮件
        try:
            self.logger.debug(f"尝试使用 SSL 连接到 {smtp_server}:{smtp_ssl_port}")
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_ssl_port, context=context) as server:
                server.login(notify_email, email_password)
                server.send_message(msg)

                email_sent_successfully = True 
                self.logger.info(f"通知邮件通过 SSL 发送成功: {subject}")
        except Exception as ssl_error:
            if not email_sent_successfully:
                self.logger.debug(f"SSL 连接或发送失败，将尝试使用 TLS: {str(ssl_error)}")
            else:
                self.logger.warning(f"SSL 连接在邮件发送后出现错误 (可能在关闭连接时): {str(ssl_error)}. 由于邮件已发送，不再尝试 TLS。")

        # 如果 SSL 尝试没有成功发送邮件，则尝试 TLS
        if not email_sent_successfully:
            try:
                self.logger.debug(f"尝试使用 TLS 连接到 {smtp_server}:{smtp_tls_port}")
                with smtplib.SMTP(smtp_server, smtp_tls_port) as server: 
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(notify_email, email_password)
                    server.send_message(msg)

                    email_sent_successfully = True 
                    self.logger.info(f"通知邮件通过 TLS 发送成功: {subject}")

            except Exception as tls_error:
                if not email_sent_successfully:
                    self.logger.error(f"尝试使用 TLS 连接或发送失败: {str(tls_error)}")
                else:
                    self.logger.warning(f"TLS 连接在邮件发送后出现错误 (可能在关闭连接时): {str(tls_error)}.")

        return email_sent_successfully