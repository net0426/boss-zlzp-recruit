import os
from dotenv import load_dotenv
from config import PROJECT_ROOT

# 加载环境变量（使用项目根目录下的 .env 文件）
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path)

# 基础配置
BASE_CONFIG = {
    'jobName': os.getenv('TARGET_JOB_NAME'),
    'Region': os.getenv('TARGET_REGION'),
}

# BOSS直聘配置
BOSS_CONFIG = {
    'url': 'https://www.zhipin.com/guangzhou/?ka=header-home',
    'work': os.getenv('WORK_EXPERIENCE'),
    'deg': os.getenv('DEGREE_REQUIREMENT'),
    'max_job': int(os.getenv('BOSS_MAX_JOB')),
}

# 智联招聘配置
ZLZP_CONFIG = {
    'url': 'https://www.zhaopin.com/',
    'work': os.getenv('WORK_EXPERIENCE'),
    'deg': os.getenv('DEGREE_REQUIREMENT'),
    'max_job': int(os.getenv('ZLZP_MAX_JOB')),
}

# AI相关配置
AI_CONFIG = {
    'UserQuery': [
        os.path.join(PROJECT_ROOT, 'prompt', 'prompt.txt'),
        os.path.join(PROJECT_ROOT, 'prompt', 'promp.txt')
    ],
    'ApiPath': os.getenv('AI_API_URL', 'http://127.0.0.1:8080/v1/chat/completions'),
    'SERVER_PATH': os.getenv('LLAMA_SERVER_PATH'),
    'MODEL_PATH': os.getenv('LLAMA_MODEL_PATH'),
    'PORT': 8080,
    'CTX_SIZE': 6800,
    'BATCH_SIZE': 256,
}

# 邮件配置
EMAIL_CONFIG = {
    'SMTP_SERVER': os.getenv('SMTP_SERVER'),
    'SMTP_PORT': os.getenv('SMTP_PORT'),
    'USE_SSL': os.getenv('USE_SSL', 'true').lower() in ('true', '1', 'yes'),
    'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
    'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD'),
    'RECEIVER_EMAIL': os.getenv('RECEIVER_EMAIL'),
}
