import os
import json
import psutil
import spotipy
import subprocess
from asyncio import sleep
from os import execvp, sys
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.raw.functions import Ping
from spotipy.oauth2 import SpotifyClientCredentials
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Initialize the bot
api_id = "YOUR_API_ID"
api_hash = "YOUR_API_HASH"
bot_token = "YOUR_BOT_TOKEN"
OWNER_ID = YOUR_OWNER_ID  # Replace with your Telegram user ID

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define sudo users
SUDO_USERS_FILE = "sudo_users.json"

def load_sudo_users():
    if not os.path.exists(SUDO_USERS_FILE):
        return []
    with open(SUDO_USERS_FILE, "r") as f:
        return json.load(f)

def save_sudo_users(sudo_users):
    with open(SUDO_USERS_FILE, "w") as f:
        json.dump(sudo_users, f)

SUDO_USERS = load_sudo_users()

# Bot Stats
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
    total_users = 61864
    total_files = 42590
    total_premium_users = 0
    total_premium_trials = 31916
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

# Command to start a Docker container
@app.on_message(filters.command("docker_start") & filters.user(SUDO_USERS))
async def docker_start(client, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡Usage: /docker_start <container_name>")
        return

    container_name = message.command[1]
    try:
        subprocess.run(["docker", "start", container_name], check=True)
        await message.reply_text(f"Container '{container_name}' started successfully.")
    except subprocess.CalledProcessError as e:
        await message.reply_text(f"⛔ Failed to start container '{container_name}'. Error: {e}")

# Command to stop a Docker container
@app.on_message(filters.command("docker_stop") & filters.user(SUDO_USERS))
async def docker_stop(client, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡Usage: /docker_stop <container_name>")
        return

    container_name = message.command[1]
    try:
        subprocess.run(["docker", "stop", container_name], check=True)
        await message.reply_text(f"Container '{container_name}' stopped successfully.")
    except subprocess.CalledProcessError as e:
        await message.reply_text(f"⛔ Failed to stop container '{container_name}'. Error: {e}")

# Command to list Docker containers
@app.on_message(filters.command("docker_ps") & filters.user(SUDO_USERS))
async def docker_ps(client, message):
    await message.delete()
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True, check=True)
        await message.reply_text(f"🚀 Running containers:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        await message.reply_text(f"⛔ Failed to list containers. Error: {e}")

# Command to show Docker container logs
@app.on_message(filters.command("docker_logs") & filters.user(SUDO_USERS))
async def docker_logs(client, message):
    await message.delete()
    if len(message.command) != 2:
        await message.reply_text("💡Usage: /docker_logs <container_name>")
        return

    container_name = message.command[1]
    try:
        result = subprocess.run(["docker", "logs", container_name], capture_output=True, text=True, check=True)
        await message.reply_text(f"📝 Logs for container '{container_name}':\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        await message.reply_text(f"💡Failed to get logs for container '{container_name}'. Error: {e}")

# Command to show Docker container stats
@app.on_message(filters.command("docker_stats") & filters.user(SUDO_USERS))
async def docker_stats(client, message):
    await message.delete()
    try:
        result = subprocess.run(["docker", "stats", "--no-stream"], capture_output=True, text=True, check=True)
        await message.reply_text(f"📊 Container stats:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        await message.reply_text(f"⛔ Failed to get container stats. Error: {e}")

# Command to display bot info
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.delete()
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("🐳 Docker", callback_data="docker_commands")],
        [InlineKeyboardButton("🔑 Sudo", callback_data="sudo_commands")],
        [InlineKeyboardButton("📦 Repo", url="https://github.com/your-repo-link")],
        [InlineKeyboardButton("💖 Donate", url="https://www.buymeacoffee.com/your-link")],
        [InlineKeyboardButton("📢 Bot Channel", url="https://t.me/your-channel-link")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
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

# Command to add a sudo user (Owner only)
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

# Command to list sudo users
@app.on_message(filters.command("sudo_users") & filters.user(SUDO_USERS + [OWNER_ID]))
async def list_sudo_users(client, message):
    await message.delete()
    if SUDO_USERS:
        await message.reply_text(f"🔑 Sudo users:\n" + "\n".join(map(str, SUDO_USERS)))
    else:
        await message.reply_text("( ＾◡＾)っ NO sudo users found.")

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

# Start the bot
app.run()
