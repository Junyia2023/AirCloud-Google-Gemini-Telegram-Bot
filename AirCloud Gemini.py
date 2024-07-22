import json
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters, ConversationHandler
from telegram import __version__ as tg_version
import logging
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def main():
    ascii_art = """
           _____                    _____                    _____                    _____                    _____           _______                   _____                    _____          
          /\    \                  /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \                  /\    \         
         /::\    \                /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\                /::\    \        
        /::::\    \               \:::\    \              /::::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /               /::::\    \       
       /::::::\    \               \:::\    \            /::::::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/    /               /::::::\    \      
      /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/    /               /:::/\:::\    \     
     /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/  \:::\    \        /:::/    /      /:::/    \:::\    \       /:::/    /               /:::/  \:::\    \    
    /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/    /               /:::/    \:::\    \   
   /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    / \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/    /      _____    /:::/    / \:::\    \  
  /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\____\  /:::/    /   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/____/      /\    \  /:::/    /   \:::\ ___\ 
 /:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::|    |/:::/____/     \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|    /      /::\____\/:::/____/     \:::|    |
 \::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/   |::::\  /:::|____|\:::\    \      \::/    /\:::\    \        \:::\    \   /:::/    / |:::|____\     /:::/    /\:::\    \     /:::|____|
  \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____|:::::\/:::/    /  \:::\    \      \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\    \   /:::/    /  \:::\    \   /:::/    / 
           \::::::/    /    \::::::/    /                 |:::::::::/    /    \:::\    \               \:::\    \        \:::\    /:::/    /     \:::\    \ /:::/    /    \:::\    \ /:::/    /  
            \::::/    /      \::::/____/                  |::|\::::/    /      \:::\    \               \:::\    \        \:::\__/:::/    /       \:::\    /:::/    /      \:::\    /:::/    /   
            /:::/    /        \:::\    \                  |::| \::/____/        \:::\    \               \:::\    \        \::::::::/    /         \:::\__/:::/    /        \:::\  /:::/    /    
           /:::/    /          \:::\    \                 |::|  ~|               \:::\    \               \:::\    \        \::::::/    /           \::::::::/    /          \:::\/:::/    /     
          /:::/    /            \:::\    \                |::|   |                \:::\    \               \:::\    \        \::::/    /             \::::::/    /            \::::::/    /      
         /:::/    /              \:::\____\               \::|   |                 \:::\____\               \:::\____\        \::/____/               \::::/    /              \::::/    /       
         \::/    /                \::/    /                \:|   |                  \::/    /                \::/    /         ~~                      \::/____/                \::/____/        
          \/____/                  \/____/                  \|___|                   \/____/                  \/____/                                   ~~                       ~~              
 """
    print(ascii_art)

if __name__ == "__main__":
    main()                                                                                                                                                                                             

# 设置日志记录
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 检查版本
print(f"python-telegram-bot 版本: {tg_version}")

# 配置
GEMINI_API_KEY = '' #在此添加你的Gemini Key
TELEGRAM_BOT_TOKEN = '' #在此添加你的Telegram Bot Key

# 管理员和授权用户列表
SUPER_ADMIN_USER_IDS = [0]  # 替换为超级管理员的Telegram用户ID
ADMIN_USER_IDS = [0]  # 替换为管理员的Telegram用户ID
authorized_users = set()
user_agreements = {}
new_admins = set()
new_super_admins = set()
new_authorized_users = set()

# 获取当前脚本所在的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 更新文件路径
SUPER_ADMIN_FILE = os.path.join(SCRIPT_DIR, 'super_admin_ids.txt')
ADMIN_FILE = os.path.join(SCRIPT_DIR, 'admin_ids.txt')
AUTHORIZED_USER_FILE = os.path.join(SCRIPT_DIR, 'authorized_users.txt')
USER_AGREEMENTS_FILE = os.path.join(SCRIPT_DIR, 'user_agreements.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'Log.json')

# 创建User文件夹和读取管理员ID以及用户UID的函数
def initialize_user_directory():
    global user_agreements
    # 读取或创建超级管理员ID文件
    if os.path.exists(SUPER_ADMIN_FILE):
        with open(SUPER_ADMIN_FILE, 'r') as f:
            for line in f:
                try:
                    super_admin_id = int(line.strip())
                    SUPER_ADMIN_USER_IDS.append(super_admin_id)
                    print(f"加载超级管理员ID: {super_admin_id}")
                except ValueError:
                    logger.warning(f"{SUPER_ADMIN_FILE} 中的无效超级管理员ID: {line}")
    else:
        with open(SUPER_ADMIN_FILE, 'w') as f:
            for super_admin_id in SUPER_ADMIN_USER_IDS:
                f.write(f"{super_admin_id}\n")
                print(f"写入超级管理员ID: {super_admin_id}")

    # 读取或创建管理员ID文件
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'r') as f:
            for line in f:
                try:
                    admin_id = int(line.strip())
                    ADMIN_USER_IDS.append(admin_id)
                    authorized_users.add(admin_id)
                    print(f"加载管理员ID: {admin_id}")
                except ValueError:
                    logger.warning(f"{ADMIN_FILE} 中的无效管理员ID: {line}")
    else:
        with open(ADMIN_FILE, 'w') as f:
            for admin_id in ADMIN_USER_IDS:
                f.write(f"{admin_id}\n")
                authorized_users.add(admin_id)
                print(f"写入管理员ID: {admin_id}")

    # 读取或创建授权用户UID文件
    if os.path.exists(AUTHORIZED_USER_FILE):
        with open(AUTHORIZED_USER_FILE, 'r') as f:
            for line in f:
                try:
                    user_id = int(line.strip())
                    authorized_users.add(user_id)
                    print(f"加载授权用户ID: {user_id}")
                except ValueError:
                    logger.warning(f"{AUTHORIZED_USER_FILE} 中的无效用户ID: {line}")
    else:
        with open(AUTHORIZED_USER_FILE, 'w') as f:
            pass  # 如果文件不存在，则创建一个空文件

    # 读取或创建用户协议同意文件
    if os.path.exists(USER_AGREEMENTS_FILE):
        with open(USER_AGREEMENTS_FILE, 'r') as f:
            user_agreements = json.load(f)
    else:
        user_agreements = {}
        with open(USER_AGREEMENTS_FILE, 'w') as f:
            json.dump(user_agreements, f)

    # 初始化日志文件
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)

# 保存用户协议同意情况
def save_user_agreements():
    with open(USER_AGREEMENTS_FILE, 'w') as f:
        json.dump(user_agreements, f)

# 保存日志
def log_action(action, user_id, target_id):
    with open(LOG_FILE, 'r+') as f:
        logs = json.load(f)
        logs.append({
            'action': action,
            'user_id': user_id,
            'target_id': target_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        f.seek(0)
        json.dump(logs, f, indent=4)

# 假设的获取用户IP地址的函数
def get_user_ip(user_id):
    return "192.168.1.1"

# 调用Google Gemini API的函数
def call_gemini_api(prompt, user_id, user_name, user_ip):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    logger.info(f"请求URL: {url}")
    logger.info(f"请求头: {headers}")
    logger.info(f"请求体: {data}")
    logger.info(f"用户ID: {user_id}, 用户名: {user_name}, 用户IP: {user_ip}")

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        
        logger.info(f"API响应: {response_json}")
        
        if 'candidates' in response_json and 'content' in response_json['candidates'][0]:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "抱歉，我无法处理您的请求。"
    except requests.exceptions.RequestException as e:
        logger.error(f"调用Gemini API时出错: {e}")
        if e.response is not None:
            logger.error(f"响应内容: {e.response.content}")
        return "抱歉，处理您的请求时出错。"

# 定义用户同意条款的状态
AGREEMENT, AGREEMENT_RESPONSE = range(2)

# 处理/start命令的函数
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    user_ip = get_user_ip(user_id)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    logger.info(f"用户 {user_name} (ID: {user_id}, IP: {user_ip}) 在 {current_time} 启动了机器人。")
    
    if user_id not in authorized_users:
        await update.message.reply_text('抱歉，您未被授权使用此机器人。')
        return
    
    if str(user_id) not in user_agreements:
        user_agreements[str(user_id)] = False
        await update.message.reply_text(
            '请在使用此机器人前阅读并同意条款和条件。您同意吗？(是/否)'
        )
        return AGREEMENT
    
    if user_agreements[str(user_id)]:
        await update.message.reply_text('您好！我是您的AI聊天机器人。问我任何问题吧！')
    else:
        await update.message.reply_text('您需要同意条款和条件才能使用此机器人。')

# 处理用户同意条款的函数
async def handle_agreement(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_response = update.message.text.lower()
    
    if user_response == '是':
        user_agreements[str(user_id)] = True
        save_user_agreements()
        await update.message.reply_text('感谢您同意条款和条件。您现在可以使用机器人了。')
        return ConversationHandler.END
    elif user_response == '否':
        user_agreements[str(user_id)] = False
        save_user_agreements()
        await update.message.reply_text('您需要同意条款和条件才能使用此机器人。')
        return ConversationHandler.END
    else:
        await update.message.reply_text('请回复 是 或 否。')
        return AGREEMENT

# 处理消息的函数
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    user_ip = get_user_ip(user_id)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if user_id not in authorized_users:
        await update.message.reply_text('抱歉，您未被授权使用此机器人。')
        return
    
    if str(user_id) not in user_agreements or not user_agreements[str(user_id)]:
        await update.message.reply_text('您需要同意条款和条件才能使用此机器人。')
        return
    
    ai_response = call_gemini_api(user_message, user_id, user_name, user_ip)
    
    logger.info(f"用户 {user_name} (ID: {user_id}, IP: {user_ip}) 在 {current_time} 发送了一条消息: {user_message}")
    
    try:
        await update.message.reply_text(ai_response)
    except Forbidden:
        logger.warning(f"机器人被用户阻止: {update.message.chat_id}")

# 处理/authorize命令的函数
async def authorize(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text('您无权使用此命令。')
        return
    
    # 检查是否回复了一条消息
    if update.message.reply_to_message:
        user_to_authorize = update.message.reply_to_message.from_user.id
        authorized_users.add(user_to_authorize)
        new_authorized_users.add(user_to_authorize)
        
        await update.message.reply_text(f'用户 {user_to_authorize} 已被授权。')
        logger.info(f"用户 {user_to_authorize} 被管理员 {user_id} 授权。")
    else:
        await update.message.reply_text('请回复一条用户消息以授权他们。')

# 处理/so命令的函数
async def so_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    user_ip = get_user_ip(user_id)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if user_id not in authorized_users:
        await update.message.reply_text('抱歉，您未被授权使用此机器人。')
        return
    
    if str(user_id) not in user_agreements or not user_agreements[str(user_id)]:
        await update.message.reply_text('您需要同意条款和条件才能使用此机器人。')
        return
    
    if context.args:
        user_message = ' '.join(context.args)
        ai_response = call_gemini_api(user_message, user_id, user_name, user_ip)
        
        logger.info(f"用户 {user_name} (ID: {user_id}, IP: {user_ip}) 在 {current_time} 发送了一条消息: {user_message}")
        
        try:
            await update.message.reply_text(ai_response)
        except Forbidden:
            logger.warning(f"机器人被用户阻止: {update.message.chat_id}")
    else:
        await update.message.reply_text('请在 /so 命令后提供一条消息。')

# 处理/appoint命令的函数
async def appoint(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in SUPER_ADMIN_USER_IDS:
        await update.message.reply_text('您无权使用此命令。')
        return
    
    # 检查是否回复了一条消息
    if update.message.reply_to_message:
        user_to_appoint = update.message.reply_to_message.from_user.id
        if user_to_appoint not in ADMIN_USER_IDS:
            ADMIN_USER_IDS.append(user_to_appoint)
            authorized_users.add(user_to_appoint)
            new_admins.add(user_to_appoint)
            
            await update.message.reply_text(f'用户 {user_to_appoint} 已被任命为管理员。')
            log_action('appoint', user_id, user_to_appoint)
            logger.info(f"用户 {user_to_appoint} 被超级管理员 {user_id} 任命为管理员。")
        else:
            await update.message.reply_text(f'用户 {user_to_appoint} 已经是管理员。')
    else:
        await update.message.reply_text('请回复一条用户消息以任命他们为管理员。')

# 处理/dismiss命令的函数
async def dismiss(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in SUPER_ADMIN_USER_IDS:
        await update.message.reply_text('您无权使用此命令。')
        return
    
    # 检查是否回复了一条消息
    if update.message.reply_to_message:
        user_to_dismiss = update.message.reply_to_message.from_user.id
        if user_to_dismiss in ADMIN_USER_IDS:
            ADMIN_USER_IDS.remove(user_to_dismiss)
            authorized_users.discard(user_to_dismiss)
            
            await update.message.reply_text(f'用户 {user_to_dismiss} 已被解除管理员身份。')
            log_action('dismiss', user_id, user_to_dismiss)
            logger.info(f"用户 {user_to_dismiss} 被超级管理员 {user_id} 解除管理员身份。")
        else:
            await update.message.reply_text(f'用户 {user_to_dismiss} 不是管理员。')
    else:
        await update.message.reply_text('请回复一条用户消息以解除他们的管理员身份。')

# 处理/help命令的函数
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "以下是您可以使用的命令:\n"
        "/start - 启动机器人并同意条款和条件。\n"
        "/authorize - (仅限管理员) 授权用户使用机器人，通过回复他们的消息。\n"
        "/appoint - (仅限超级管理员) 任命新管理员，通过回复他们的消息。\n"
        "/dismiss - (仅限超级管理员) 解除管理员身份，通过回复他们的消息。\n"
        "/so - 发送消息给AI模型并获得回复。\n"
        "/help - 获取帮助并查看可用命令列表。"
    )
    await update.message.reply_text(help_text)

# 创建ConversationHandler
agreement_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        AGREEMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_agreement)]
    },
    fallbacks=[]
)

# 定时任务函数
def write_new_authorizations():
    global new_admins, new_super_admins, new_authorized_users
    if new_super_admins:
        with open(SUPER_ADMIN_FILE, 'a') as f:
            for super_admin_id in new_super_admins:
                f.write(f"{super_admin_id}\n")
                logger.info(f"新超级管理员ID {super_admin_id} 已写入文件。")
        new_super_admins.clear()
    
    if new_admins:
        with open(ADMIN_FILE, 'a') as f:
            for admin_id in new_admins:
                f.write(f"{admin_id}\n")
                logger.info(f"新管理员ID {admin_id} 已写入文件。")
        new_admins.clear()
    
    if new_authorized_users:
        with open(AUTHORIZED_USER_FILE, 'a') as f:
            for user_id in new_authorized_users:
                f.write(f"{user_id}\n")
                logger.info(f"新授权用户ID {user_id} 已写入文件。")
        new_authorized_users.clear()

def main():
    # 初始化用户目录和ID列表
    initialize_user_directory()
    
    # 打印调试信息
    print(f"超级管理员用户ID: {SUPER_ADMIN_USER_IDS}")
    print(f"管理员用户ID: {ADMIN_USER_IDS}")
    print(f"授权用户: {authorized_users}")
    
    # 创建Application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # 添加命令和消息处理器
    application.add_handler(agreement_handler)
    application.add_handler(CommandHandler('authorize', authorize))
    application.add_handler(CommandHandler('appoint', appoint))
    application.add_handler(CommandHandler('dismiss', dismiss))
    application.add_handler(CommandHandler('so', so_command))
    application.add_handler(CommandHandler('help', help_command))  # 添加这一行
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 设置定时任务
    scheduler = BackgroundScheduler()
    scheduler.add_job(write_new_authorizations, 'interval', minutes=3)
    scheduler.start()

    # 启动Bot
    application.run_polling()

if __name__ == '__main__':
    main()
