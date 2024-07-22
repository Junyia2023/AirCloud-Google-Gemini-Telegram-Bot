# Telegram AI Chatbot

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 项目简介

这是一个基于Telegram的AI聊天机器人，使用Google Gemini API进行对话生成。该机器人支持管理员和超级管理员功能，允许授权用户与机器人进行互动。


## 功能

- 支持管理员和超级管理员功能
- 用户同意条款和条件后才能使用机器人
- 定时任务自动保存新授权用户和管理员
- 集成Google Gemini API进行对话生成

## 安装

### 先决条件

在开始之前，请确保你已经安装了以下软件：

- Python 3.8+
- pip (Python包管理器)

### 克隆仓库

```bash
git (https://github.com/Junyia2023/AirCloud-Google-Gemini-Telegram-Bot.git)
cd AirCloud-Google-Gemini-Telegram-Bot
```

### 安装运行库

- python-telegram-bot：用于与Telegram Bot API进行交互。
- requests：用于发送HTTP请求。
- apscheduler：用于调度定时任务。
- 你可以使用命令一键安装以上运行库
```bash
pip install python-telegram-bot requests apscheduler
```


## 配置

### 修改脚本中 Gemini Key 以及 Telegram Bot Key

```bash
GEMINI_API_KEY = '' #在此添加你的Gemini Key
TELEGRAM_BOT_TOKEN = '' #在此添加你的Telegram Bot Key
```
### 修改脚本中 超级管理员 ID 以及 管理员ID

```bash
SUPER_ADMIN_USER_IDS = [0]  # 替换为超级管理员的Telegram用户ID
ADMIN_USER_IDS = [0]  # 替换为管理员的Telegram用户ID
```

### 关于文件输出

在首次运行本脚本时，脚本将会在脚本所在文件目录创建多个文件夹 分别为
- admin_ids.txt #用于记录管理员UID
- super_admin_ids.txt #用于记录超级管理员UID
- authorized_users.txt #用于记录被授权用户UID
- user_agreements.json #用于记录用户条款同意情况
- Log.json #用于记录管理员操作日志

# 使用

```bash
python AirCloud Gemini.py
```

# 可用命令

- /start - 启动机器人并同意条款和条件
- /authorize - (仅限管理员) 授权用户使用机器人，通过回复他们的消息
- /appoint - (仅限超级管理员) 任命新管理员，通过回复他们的消息
- /dismiss - (仅限超级管理员) 解除管理员身份，通过回复他们的消息
- /so - 发送消息给AI模型并获得回复，适用于群组
- /help - 获取帮助并查看可用命令列表

# 许可证

- 该项目基于 MIT 许可证开源。详情请参阅 LICENSE 文件。


