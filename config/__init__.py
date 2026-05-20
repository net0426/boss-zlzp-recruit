import os
import sys

# 获取项目根目录（config 的上一级目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将项目根目录添加到 sys.path（如果尚未添加）
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 确保项目根目录在 Python 路径的最前面，便于模块导入
