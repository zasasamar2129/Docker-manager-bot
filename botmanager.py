import os
import json
import pytz
import time
import psutil
import shutil 
import spotipy
import logging
import subprocess
from flask import Flask
from asyncio import sleep
from os import execvp, sys
from pyrogram import Client
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv
from aiohttp import ClientSession
from pyrogram import Client, filters
from os import environ,sys,mkdir,path
from pyrogram.raw.functions import Ping
import requests
from sys import executable
from pyrogram.types import InputMediaPhoto
from spotipy.oauth2 import SpotifyClientCredentials
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()
client_credentials_manager = SpotifyClientCredentials()

############################################## Log ###################################

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(message)s",
    handlers = [logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


class BotManagerClient(Client):
    async def start(self):
        global BOT_INFO
        await super().start()
        BOT_INFO = await self.get_me()
        LOGGER.info(f"Bot Started As {BOT_INFO.username}\n")
        
        # Send the startup message to the log group
        await send_startup_message()

# Initialize the bot
api_id = "29356703"
api_hash = "e701fd9416e0108d47b1041b27e74697"
bot_token = "7762068154:AAGwVtVsxm5hLRiwzdHxjE6ri-qXiRXL_yo"
LOG_GROUP_ID = -1001961244146  # Replace with your Telegram log group ID
OWNER_ID = 5337964165  # Replace with your Telegram user ID

############################################ File Paths #######################################################
SUDO_USERS_FILE = "sudo_users.json"
# Bot Log Retrieval Command
LOG_FILE = "bot_logs.log"
# Ensure the assets folder and image path are correctly defined
ASSETS_FOLDER = "assets"
STARTUP_IMAGE = os.path.join(ASSETS_FOLDER, "startup.jpg")

app = BotManagerClient("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


def load_sudo_users():
    if not os.path.exists(SUDO_USERS_FILE):
        return []
    with open(SUDO_USERS_FILE, "r") as f:
        return json.load(f)

def save_sudo_users(sudo_users):
    with open(SUDO_USERS_FILE, "w") as f:
        json.dump(sudo_users, f)

SUDO_USERS = load_sudo_users()

########################################### Docker command handlers ########################################################
def run_docker_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.stderr.decode('utf-8')


@app.on_message(filters.command("docker_start") & filters.user(SUDO_USERS + [OWNER_ID]))
async def docker_start(_, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡 Usage: /docker_start <container_name>")
        return

    container_name = message.command[1]
    output = run_docker_command(f"docker start {container_name}")
    formatted_output = f"**Docker Start Output:**\n```\n{output.strip()}\n```"
    await message.reply_text(formatted_output)


@app.on_message(filters.command("docker_stop") & filters.user(SUDO_USERS + [OWNER_ID]))
async def docker_stop(_, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡 Usage: /docker_stop <container_name>")
        return

    container_name = message.command[1]
    output = run_docker_command(f"docker stop {container_name}")
    formatted_output = f"**Docker Stop Output:**\n```\n{output.strip()}\n```"
    await message.reply_text(formatted_output)



@app.on_message(filters.command("docker_logs") & filters.user(SUDO_USERS + [OWNER_ID]))
async def docker_logs(_, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡 Usage: /docker_logs <container_name>")
        return

    container_name = message.command[1]
    output = run_docker_command(f"docker logs {container_name}")
    formatted_output = f"**Docker Logs Output:**\n```\n{output.strip()}\n```"
    await message.reply_text(formatted_output)


# /docker_ps command
@app.on_message(filters.command("docker_ps") & filters.user(SUDO_USERS + [OWNER_ID]))
async def docker_ps(_, message):
    await message.delete()
    output = run_docker_command("docker ps --format '{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}'")

    lines = output.splitlines()
    if not lines:  # No containers are running
        formatted_output = "**Docker PS Output:**\nNo containers are currently running."
    else:
        header = f"{'ID':<33}{'Name':<30}{'Image':<25}{'Status':<35}"
        rows = [
            f"{line.split('\t')[0]:<17}{line.split('\t')[1]:<25}{line.split('\t')[2]:<20}{line.split('\t')[3]:<20}"
            for line in lines
        ]
        formatted_output = f"**Docker PS Output:**\n```\n{header}\n{'-' * 73}\n" + "\n".join(rows) + "\n```"

    await message.reply_text(formatted_output)

# /docker_stats command
@app.on_message(filters.command("docker_stats") & filters.user(SUDO_USERS + [OWNER_ID]))
async def docker_stats(_, message):
    await message.delete()
    output = run_docker_command("docker stats --no-stream --format '{{.ID}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'")

    lines = output.splitlines()
    if not lines:  # No containers or no stats available
        formatted_output = "**Docker Stats Output:**\nNo stats are currently available."
    else:
        rows = []
        for line in lines:
            fields = line.split('\t')
            container_id = fields[0] if len(fields) > 0 else "N/A"
            name = fields[1] if len(fields) > 1 else "N/A"
            cpu = fields[2] if len(fields) > 2 else "N/A"
            mem = fields[3] if len(fields) > 3 else "N/A"
            net = fields[4] if len(fields) > 4 else "N/A"
            rows.append(
                f"ID: {container_id}\n\n"
                f"Name: {name}\n\n"
                f"CPU %: {cpu}\n\n"
                f"Memory Usage: {mem}\n\n"
                f"Net I/O: {net}\n\n"
                f"{'-' * 40}"
            )

        formatted_output = f"**Docker Stats Output:**\n```\n" + "\n".join(rows) + "\n```"

    await message.reply_text(formatted_output)


############################################### Bot Stats ###########################################################

@app.on_message(filters.command("cpu") & filters.user(SUDO_USERS))
async def cpu_usage(_, message):
    await message.delete()
    cpu_percent = psutil.cpu_percent(interval=1)
    await message.reply_text(f"**CPU Usage:** `{cpu_percent}%`")

@app.on_message(filters.command("ping"))
async def ping(client, message):
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    ms = (datetime.now() - start).microseconds / 1000
    await message.reply_text(f"**Pong!**\nResponse time: `{ms} ms`")

@app.on_message(filters.command("stats"))
async def stats(client, message):
    # Initial reply with a placeholder message
    fetching_message = await message.reply_text("Fetching stats...\n[                    ] 0%")
    
    # Simulate progress by updating the message incrementally
    for progress in range(0, 101, 10):
        bar = "█" * (progress // 10) + " " * (10 - (progress // 10))
        await fetching_message.edit_text(f"Fetching stats...\n[{bar}] {progress}%")
        await sleep(0.5)  # Adjust sleep time to control animation speed
    
    # Gather system information
    os_type = sys.platform
    linux_type = " ".join(os.uname()) if hasattr(os, 'uname') else "N/A"
    cpu_cores = psutil.cpu_count(logical=True)
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_free = 100 - cpu_usage
    core_usages = psutil.cpu_percent(interval=1, percpu=True)
    memory = psutil.virtual_memory()
    total_ram = memory.total / (1024 ** 2)
    ram_usage = memory.percent
    ram_available = memory.available / (1024 ** 2)
    used_ram = memory.used / (1024 ** 2)
    # Simulate database status (replace with actual database queries if available)
    db1_used_size = 116.23
    db1_free_size = 395.77
    db2_used_size = 10.47
    db2_free_size = 501.53
    # Simulate user and file counts (replace with actual queries if available)
    total_users = 1
    total_files = 0
    total_premium_users = 0
    total_premium_trials = 0
    # Measure response times
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    telegram_response_time = (datetime.now() - start).microseconds / 1000
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.search("test")  # Dummy search to measure response time
    spotify_response_time = (datetime.now() - start).microseconds / 1000
    stats_text = (
    "⚡️ **Server Status** ⚡️\n\n"
    
    "💻 **Server OS** 💻\n"
    f"🌐 **Operating System Type:** {os_type}\n"
    f"📜 **Linux Type:** {linux_type}\n\n"
    
    "🖥️ **CPU Status** 🖥️\n"
    f"🧮 **CPU Cores:** {cpu_cores}\n"
    f"📊 **CPU Usage:** {cpu_usage}%\n"
    f"💾 **CPU Free:** {cpu_free}%\n"
    + "\n".join([f"⚙️ **Core {i + 1}:** {usage}%" for i, usage in enumerate(core_usages)]) + "\n\n"
    
    "📡 **Response Status** 📡\n"
    f"⏱️ **Telegram API Response Time:** {round(telegram_response_time)} ms\n"
    f"🎵 **Spotify API Response Time:** {spotify_response_time:.2f} ms\n\n"
    
    "💾 **Memory Status** 💾\n"
    f"💽 **Total RAM:** {total_ram:.2f} MB\n"
    f"🔋 **RAM Usage:** {ram_usage}%\n"
    f"📥 **RAM Available:** {ram_available:.2f} MB\n"
    f"📤 **Used RAM:** {used_ram:.2f} MB\n\n"
    
    "📚 **Database Status** 📚\n"
    f"📂 **DB 1 Used Size:** {db1_used_size} MB\n"
    f"📂 **DB 1 Free Size:** {db1_free_size} MB\n"
    f"📂 **DB 2 Used Size:** {db2_used_size} MB\n"
    f"📂 **DB 2 Free Size:** {db2_free_size} MB\n\n"
    
    "👥 **Users Status** 👥\n"
    f"👤 **Total Users:** {total_users}\n"
    f"📁 **Total Files:** {total_files}\n"
    f"✨ **Total Premium Users and Premium Trial Users:** {total_premium_users}\n"
    f"🌟 **Users Who Enjoyed Premium Trials and Plans:** {total_premium_trials}\n"
)
    await fetching_message.delete()
    await message.reply_text(stats_text)

########################################## Command to display bot info ##############################################
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.delete()
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("🐳 Docker", callback_data="docker_commands")],
        [InlineKeyboardButton("🔑 Sudo", callback_data="sudo_commands")],
        [InlineKeyboardButton("📦 Repo", url="https://github.com/your-repo-link")],
        [InlineKeyboardButton("💖 Donate", url="https://www.buymeacoffee.com/zasasamar")],
        [InlineKeyboardButton("📢 Bot Channel", url="https://t.me/Zpotify1")
        ],
        [
            InlineKeyboardButton("❌", callback_data="close")
        ]
    ])
    await message.reply_text(
        "👋 Hello! I am your Bot Manager.\n"
        "✨ I can help you manage your bots and more.\n"
        "✨ Use the buttons below to navigate.",
        reply_markup=reply_markup
    )

# Command to display help
@app.on_message(filters.command("help"))
async def help(client, message):
    await message.delete()
    help_text = (
        "🛠 **Help Menu** 🛠\n\n"
        "✨ /docker_start <container_name> - Start a Docker container\n"
        "✨ /docker_stop <container_name> - Stop a Docker container\n"
        "✨ /docker_ps - List running Docker containers\n"
        "✨ /docker_logs <container_name> - Show logs for a Docker container\n"
        "✨ /docker_stats - Show stats for Docker containers\n"
        "✨ /add_sudo <user_id> - Add a sudo user (Owner only)\n"
        "✨ /remove_sudo <user_id> - Remove a sudo user (Owner only)\n"
        "✨ /sudo_users - List sudo users\n"
    )
    await message.reply_text(help_text)

################################### Command to +/- a sudo user (Owner only) ##################################################

@app.on_message(filters.command("add_sudo") & filters.user(OWNER_ID))
async def add_sudo(client, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡 Usage: /add_sudo <user_id>")
        return

    try:
        user_id = int(message.command[1])
        if user_id not in SUDO_USERS:
            SUDO_USERS.append(user_id)
            save_sudo_users(SUDO_USERS)
            await message.reply_text(f"✨User {user_id} added to sudo users.")
        else:
            await message.reply_text(f"💫User {user_id} is already a sudo user.")
    except ValueError:
        await message.reply_text("⛔Invalid user ID.")

# Command to remove a sudo user (Owner only)
@app.on_message(filters.command("remove_sudo") & filters.user(OWNER_ID))
async def remove_sudo(client, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡Usage: /remove_sudo <user_id>")
        return

    try:
        user_id = int(message.command[1])
        if user_id in SUDO_USERS:
            SUDO_USERS.remove(user_id)
            save_sudo_users(SUDO_USERS)
            await message.reply_text(f"🧹User {user_id} removed from sudo users.")
        else:
            await message.reply_text(f"⛔ User {user_id} is not a sudo user.")
    except ValueError:
        await message.reply_text("⛔ Invalid user ID.")

########################################## Command to list sudo users #############################################
@app.on_message(filters.command("sudo_users") & filters.user(SUDO_USERS + [OWNER_ID]))
async def list_sudo_users(client, message):
    await message.delete()
    if SUDO_USERS:
        await message.reply_text(f"🔑 Sudo users:\n" + "\n".join(map(str, SUDO_USERS)))
    else:
        await message.reply_text("( ＾◡＾)っ NO sudo users found.")


######################################################## HELP ######################################################
# Inline button handlers
@app.on_callback_query(filters.regex("help"))
async def on_help_callback(client, callback_query):
    help_text = (
        "🛠 **Help Menu** 🛠\n\n"
        "✨ /docker_start <container_name> - Start a Docker container\n"
        "✨ /docker_stop <container_name> - Stop a Docker container\n"
        "✨ /docker_ps - List running Docker containers\n"
        "✨ /docker_logs <container_name> - Show logs for a Docker container\n"
        "✨ /docker_stats - Show stats for Docker containers\n"
        "✨ /add_sudo <user_id> - Add a sudo user (Owner only)\n"
        "✨ /remove_sudo <user_id> - Remove a sudo user (Owner only)\n"
        "✨ /sudo_users - List sudo users\n"
    )
    await callback_query.message.edit_text(help_text)

@app.on_callback_query(filters.regex("docker_commands"))
async def on_docker_commands_callback(client, callback_query):
    docker_text = (
        "🐳 **Docker Commands** 🐳\n\n"
        "✨ /docker_start <container_name> - Start a Docker container\n"
        "✨ /docker_stop <container_name> - Stop a Docker container\n"
        "✨ /docker_ps - List running Docker containers\n"
        "✨ /docker_logs <container_name> - Show logs for a Docker container\n"
        "✨ /docker_stats - Show stats for Docker containers\n"
    )
    await callback_query.message.edit_text(docker_text)

@app.on_callback_query(filters.regex("sudo_commands"))
async def on_sudo_commands_callback(client, callback_query):
    sudo_text = (
        "🔑 **Sudo Commands** 🔑\n\n"
        "✨ /add_sudo <user_id> - Add a sudo user (Owner only)\n"
        "✨ /remove_sudo <user_id> - Remove a sudo user (Owner only)\n"
        "✨ /sudo_users - List sudo users\n"
    )
    await callback_query.message.edit_text(sudo_text)

@app.on_callback_query(filters.regex("close"))
async def on_close_callback(client, callback_query):
    await callback_query.message.delete()

#################################################### SHUTDOWN ################################################
@app.on_message(filters.command("shutdown") & filters.chat(OWNER_ID) & filters.private)
async def shutdown(_, message):
    await message.delete()

    keyboard = [
        [
            InlineKeyboardButton("🟢 Yes", callback_data="shutdown_yes"),
            InlineKeyboardButton("🔴 No", callback_data="shutdown_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("( •᷄ᴗ•́) Are you sure you want to shut down the bot?", reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"shutdown_(yes|no)"))
async def handle_shutdown_query(_, callback_query):
    if callback_query.data == "shutdown_yes":
        await callback_query.message.delete()
        await callback_query.answer("🔌Shutting down bot...", show_alert=True)

        # Shutdown the bot by stopping the event loop
        await os._exit(0)

    

    elif callback_query.data == "shutdown_no":
        await callback_query.answer("Bot shutdown has been cancelled.", show_alert=True)
        await callback_query.message.delete()

######################################################## RESTART #################################################
@app.on_message(filters.command("restart") & filters.chat(OWNER_ID) & filters.private)
async def restart(_, message):
    await message.delete()

    keyboard = [
        [
            InlineKeyboardButton("🟢 Yes", callback_data="restart_yes"),
            InlineKeyboardButton("🔴 No", callback_data="restart_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.delete()
    await message.reply_text("( •᷄ᴗ•́) Are you sure you want to restart the bot?", reply_markup=reply_markup)

@app.on_callback_query(filters.regex(r"restart_(yes|no)"))
async def handle_restart_query(_, callback_query):
    if callback_query.data == "restart_yes":
        await callback_query.message.delete()
        await callback_query.answer("Restarting bot...", show_alert=True)
        
        execvp(sys.executable, [sys.executable,  "zaco.py"])
    elif callback_query.data == "restart_no":
        await callback_query.answer("Bot restart has been cancelled.", show_alert=True)
        await callback_query.message.delete()

###################################################BOT LOG#####################################################


@app.on_message(filters.command("logs") & filters.user(SUDO_USERS + [OWNER_ID]))
async def get_logs(_, message):
    await message.delete()
    try:
        if os.path.exists(LOG_FILE):
            await app.send_document(
                LOG_GROUP_ID,
                LOG_FILE,
                caption="📜 **Bot Logs** 📜\nHere are the latest logs."
            )
        else:
            await message.reply_text("⛔ Log file not found.")
    except Exception as e:
        await message.reply_text(f"⛔ Failed to retrieve logs: {e}")


########################################################LOG#####################################################
# Logging Setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Bot started.")

# Example: Log an event
@app.on_message(filters.command("example") & filters.user(SUDO_USERS + [OWNER_ID]))
async def example_command(_, message):
    await message.reply_text("This is an example command.")
    logging.info(f"Example command used by {message.from_user.id}")


# Function to send a startup message with an image to the log group
async def send_startup_message():
    if os.path.exists(STARTUP_IMAGE):
        await app.send_photo(
            chat_id=LOG_GROUP_ID,
            photo=STARTUP_IMAGE,
            caption="📣 **Bot Manager Started!**\nThe bot is now online and operational. 🚀",
        )
    else:
        await app.send_message(
            chat_id=LOG_GROUP_ID,
            text="📣 **Bot Manager Started!**\nThe bot is now online and operational. 🚀\n\n⚠️ Startup image not found in assets folder.",
        )

# Override the `start` method to include the startup message feature
async def start(self):
    global BOT_INFO
    await super().start()
    BOT_INFO = await self.get_me()
    LOGGER.info(f"Bot Started As {BOT_INFO.username}\n")
    
    # Send the startup message to the log group
    await send_startup_message()

# Assign the updated start method to the app instance
# Start the bot
app.run()
