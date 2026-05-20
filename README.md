# 🎯 招聘岗位智能筛选系统

> 自动化招聘平台岗位筛选与投递工具，支持 BOSS直聘和智联招聘，集成 AI 智能筛选功能

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-purple.svg)](README.md)

</div>

## 📸 界面预览

<div align="center">

### 主程序界面
![主程序界面](https://raw.githubusercontent.com/net0426/screenshots/main/%E7%A8%8B%E5%BA%8F%E6%88%AA%E5%9B%BE.png)

### 打招呼功能
![打招呼功能](https://raw.githubusercontent.com/net0426/screenshots/main/%E6%89%93%E6%8B%9B%E5%91%BC.png)

### AI 智能判断
![AI 智能判断](https://raw.githubusercontent.com/net0426/screenshots/main/AI%E5%88%A4%E6%96%AD.png)

</div>

## 📋 目录

- [功能特点](#功能特点)
- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [AI 配置](#ai-配置)

## ✨ 功能特点

### 🏢 双平台支持
- **BOSS直聘** - 自动筛选并投递岗位
- **智联招聘** - 自动筛选并投递岗位

### 🤖 AI 智能筛选
- 本地 AI 模型支持（LLaMA/Qwen 系列）
- 自定义筛选提示词
- 岗位信息智能分析

### 🖥️ 可视化界面
- PySide6 开发的图形界面
- 二维码登录支持
- 实时状态展示

### 🔒 安全登录
- 支持无头模式（CLI）
- 支持可视化模式（GUI）
- 登录状态管理

### 📊 灵活配置
- 自定义岗位名称
- 自定义地区筛选
- 自定义经验/学历要求
- 自定义投递数量

## 📁 项目结构

```
招聘联系测试/
├── business/                # 业务逻辑层
│   ├── __init__.py
│   └── recruit_business.py  # 核心业务调度
├── config/                  # 配置管理
│   ├── __init__.py          # 路径管理
│   └── config.py            # 配置加载
├── pages/                   # 页面对象层
│   ├── __init__.py
│   ├── base_page.py         # 页面基类
│   ├── boss_page.py         # BOSS页面操作
│   ├── zlzp_page.py         # 智联页面操作
│   ├── login_manager.py     # 登录管理
│   ├── get_web.py           # Web驱动管理
│   ├── start_copaw.py       # AI服务管理
│   └── AI_page.py           # AI工具类
├── utils/                   # 工具模块
│   ├── __init__.py
│   └── log_utils.py         # 日志工具
├── prompt/                  # AI提示词
│   ├── prompt.txt           # 岗位筛选提示词
│   └── promp.txt            # 打招呼提示词
├── logs/                    # 日志目录
├── main.py                  # CLI入口
├── recruitment_greeting_sender.py  # GUI入口
├── .env                     # 配置文件
├── requirements.txt         # 依赖列表
└── README.md                # 本文件
```

## 🛠️ 技术栈

| 分类 | 技术 |
|------|------|
| 编程语言 | Python 3.10+ |
| UI 框架 | PySide6 (Qt6) |
| 浏览器自动化 | DrissionPage |
| 配置管理 | python-dotenv |
| 中文处理 | pypinyin |
| HTTP 请求 | requests |
| 本地 AI | llama.cpp |

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目
cd 招聘联系测试

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置项目

复制示例配置文件并修改：

```bash
cp .env.example .env
```

编辑 [`.env`](d:\pyside6\bos\招聘联系测试\.env) 文件：

```env
# AI服务配置
AI_API_URL=http://127.0.0.1:8080/v1/chat/completions
LLAMA_SERVER_PATH=D:\AI-python\llama.cpp\bin\Release\llama-server.exe
LLAMA_MODEL_PATH=D:\AI-python\llama.cpp\models\Qwen2.5-7B-Instruct-1M-Q4_K_M-GGUF\Qwen2.5-7B-Instruct-1M-Q4_K_M.gguf

# 招聘平台配置
TARGET_JOB_NAME=软件测试
TARGET_REGION=广州
BOSS_MAX_JOB=1
ZLZP_MAX_JOB=1
WORK_EXPERIENCE=
DEGREE_REQUIREMENT=
```

### 3. 准备 AI 提示词

在 [`prompt/`](d:\pyside6\bos\招聘联系测试\prompt) 目录下准备两个文件：
- [`prompt.txt`](d:\pyside6\bos\招聘联系测试\prompt\prompt.txt) - 岗位筛选提示词
- [`promp.txt`](d:\pyside6\bos\招聘联系测试\prompt\promp.txt) - 打招呼提示词

## ⚙️ 配置说明

### .env 配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `TARGET_JOB_NAME` | 目标岗位名称 | `软件测试` |
| `TARGET_REGION` | 目标地区 | `广州` |
| `BOSS_MAX_JOB` | BOSS直聘最大投递数 | `10` |
| `ZLZP_MAX_JOB` | 智联招聘最大投递数 | `10` |
| `WORK_EXPERIENCE` | 工作经验要求 | `3-5年` |
| `DEGREE_REQUIREMENT` | 学历要求 | `本科` |
| `AI_API_URL` | AI API 地址 | `http://127.0.0.1:8080/v1/chat/completions` |
| `LLAMA_SERVER_PATH` | llama-server 路径 | `D:\AI-python\llama.cpp\...\llama-server.exe` |
| `LLAMA_MODEL_PATH` | 模型文件路径 | `D:\AI-python\...\Qwen2.5-7B-Instruct-1M-Q4_K_M.gguf` |

## 📖 使用方法

### 方式一：GUI 可视化模式（推荐）

```bash
python recruitment_greeting_sender.py
```

**功能特点：**
- 图形化配置界面
- 二维码扫码登录
- 实时状态监控
- 直观的操作体验

### 方式二：CLI 命令行模式

```bash
# 使用默认配置运行
python main.py

# 指定平台
python main.py --platform boss      # 仅 BOSS直聘
python main.py --platform zlzp      # 仅智联招聘
python main.py --platform all       # 两个平台（默认）

# 覆盖配置
python main.py --job "Python开发" --region "北京"
```

**CLI 参数：**

| 参数 | 说明 |
|------|------|
| `--platform` | 指定平台：boss/zlzp/all |
| `--job` | 覆盖岗位名称 |
| `--region` | 覆盖地区配置 |

## 🤖 AI 配置

### 本地 AI 服务启动

项目支持使用 llama.cpp 运行本地 AI 模型：

```bash
# 方式一：程序自动启动
# 在 GUI 模式下点击启动，会自动启动 AI 服务

# 方式二：手动启动 llama-server
# 使用项目配置的路径启动
llama-server -m <模型路径> -c 6800 -n 256 --port 8080
```

### 自定义提示词

编辑 [`prompt/prompt.txt`](d:\pyside6\bos\招聘联系测试\prompt\prompt.txt) - 岗位筛选提示词

```
你是一个招聘岗位筛选助手，根据以下信息判断岗位是否符合要求...
```

编辑 [`prompt/promp.txt`](d:\pyside6\bos\招聘联系测试\prompt\promp.txt) - 打招呼提示词

```
你好，我对这个岗位很感兴趣...
```

## 📝 项目架构说明

### 分层架构

```
┌─────────────────────────────────────────┐
│         UI 层 (GUI / CLI)               │
│  recruitment_greeting_sender.py | main.py│
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│       业务层 (Business)                  │
│      business/recruit_business.py       │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│       页面层 (Pages)                     │
│    base_page.py | boss_page.py | ...    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│       配置层 (Config)                    │
│      config/config.py                   │
└─────────────────────────────────────────┘
```

### 核心模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 业务调度 | [`business/recruit_business.py`](d:\pyside6\bos\招聘联系测试\business\recruit_business.py) | 协调各平台执行 |
| BOSS页面 | [`pages/boss_page.py`](d:\pyside6\bos\招聘联系测试\pages\boss_page.py) | BOSS直聘操作 |
| 智联页面 | [`pages/zlzp_page.py`](d:\pyside6\bos\招聘联系测试\pages\zlzp_page.py) | 智联招聘操作 |
| 登录管理 | [`pages/login_manager.py`](d:\pyside6\bos\招聘联系测试\pages\login_manager.py) | 登录和浏览器管理 |
| 基础页面 | [`pages/base_page.py`](d:\pyside6\bos\招聘联系测试\pages\base_page.py) | 页面基类和 AI 调用 |
| 配置管理 | [`config/config.py`](d:\pyside6\bos\招聘联系测试\config\config.py) | 统一配置加载 |

## 🔑 关键特性

### 1. 可移植路径管理

项目使用统一的路径管理机制，可将项目移动到任何位置都能正常运行。核心实现：[`config/__init__.py`](d:\pyside6\bos\招聘联系测试\config\__init__.py)

### 2. 双模式浏览器

- **有头模式（GUI）**：可视化操作，方便调试
- **无头模式（CLI）**：后台运行，性能更好

### 3. 智能登录检测

自动检测登录状态，未登录时跳过当前平台的处理。

### 4. AI 集成

支持本地 AI 模型进行岗位智能筛选，可自定义筛选标准。

## 📊 日志说明

所有运行日志保存在 [`logs/`](d:\pyside6\bos\招聘联系测试\logs) 目录：
- 文件命名：`recruit_YYYYMMDD.log`
- 包含时间戳、操作记录、错误信息

## 🧪 测试

```bash
# 测试导入是否正常
python test_imports.py

# 测试配置加载
python -c "from config.config import BASE_CONFIG; print(BASE_CONFIG)"
```

## ⚠️ 注意事项

1. **登录安全**：请保管好账号信息，项目不存储登录凭证
2. **使用频率**：合理设置投递间隔，避免对平台造成压力
3. **模型资源**：本地 AI 需要足够的内存和算力
4. **法律合规**：遵守各招聘平台的使用条款

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

<div align="center">
Made with ❤️ for Job Seekers
</div>
