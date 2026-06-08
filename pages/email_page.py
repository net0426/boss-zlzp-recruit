import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.config import EMAIL_CONFIG


def send_email(subject, message, image_path=None):
    """
    发送邮件，可选是否包含图片内容

    参数:
        subject: 邮件主题
        message: 文本内容
        image_path: 图片文件路径（可选，为None则不发送图片）

    返回:
        发送成功返回True，否则返回False
    """
    # 检查必需的配置是否存在
    required_fields = ['SMTP_SERVER', 'SMTP_PORT', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECEIVER_EMAIL']
    for field in required_fields:
        if not EMAIL_CONFIG[field]:
            print(f"警告: 邮件配置项 {field} 未设置，无法发送邮件")
            return False

    # 检查图片文件是否存在（如果提供了图片路径）
    if image_path and not os.path.exists(image_path):
        print(f"警告: 图片文件不存在 - {image_path}，将发送纯文本邮件")
        image_path = None  # 标记为不发送图片

    server = None
    try:
        # 创建多部分邮件
        if image_path:
            msg = MIMEMultipart('related')  # 带图片用related类型
        else:
            msg = MIMEMultipart()  # 纯文本用普通类型

        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = EMAIL_CONFIG['RECEIVER_EMAIL']
        msg['Subject'] = subject

        if image_path:
            # 有图片时，使用HTML格式
            image_cid = "image_unique_id"
            html_content = f"""
            <html>
              <body>
                <p>{message}</p>
                <p>图片内容：</p>
                <img src="cid:{image_cid}" alt="邮件图片">
              </body>
            </html>
            """
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 添加图片
            with open(image_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<{image_cid}>')
                img.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                msg.attach(img)
        else:
            # 无图片时，使用纯文本格式
            msg.attach(MIMEText(message, 'plain', 'utf-8'))

        # 连接服务器并发送
        if EMAIL_CONFIG['USE_SSL']:
            server = smtplib.SMTP_SSL(EMAIL_CONFIG['SMTP_SERVER'], int(EMAIL_CONFIG['SMTP_PORT']), timeout=10)
        else:
            server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], int(EMAIL_CONFIG['SMTP_PORT']), timeout=10)
            server.starttls()

        server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
        server.sendmail(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['RECEIVER_EMAIL'], msg.as_string())
        print("邮件发送成功!")
        return True

    except Exception as e:
        print(f"发送失败: {str(e)}")
    finally:
        if server:
            try:
                server.quit()
            except:
                pass

    return False


# 使用示例
if __name__ == "__main__":
    send_email(
        subject="纯文本邮件",
        message="这是一封没有图片的纯文本邮件，不提供图片路径也能正常发送"
    )
