# business package initialization
# 自动配置项目路径
from config import PROJECT_ROOT
import sys

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
