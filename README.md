# 🤖 Telegram Bot Manager

Welcome to **Telegram Bot Manager**! This Telegram bot helps you manage Docker containers and provides various system stats. It also includes features for managing sudo users and more.

## 🌟 Features

- **Docker Management**: Start, stop, list, and view logs and stats of Docker containers.
- **System Stats**: Check CPU usage, response time, and detailed system stats.
- **Sudo User Management**: Add, remove, and list sudo users.
- **Inline Buttons**: Easy navigation with inline buttons for various commands and links.

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Telegram Bot API credentials
- Docker installed on your server

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo-link.git
    cd your-repo-link
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your environment variables:
    ```bash
    export API_ID="YOUR_API_ID"
    export API_HASH="YOUR_API_HASH"
    export BOT_TOKEN="YOUR_BOT_TOKEN"
    export OWNER_ID="YOUR_OWNER_ID"
    ```

4. Run the bot:
    ```bash
    python bot.py
    ```

## 📜 Commands

### General Commands

- `/start` - Display bot info and navigation buttons.
- `/help` - Show help menu with available commands.
- `/ping` - Check the bot's response time.
- `/stats` - Fetch and display detailed system stats.
- `/cpu` - Display current CPU usage.

### Docker Commands

- `/docker_start <container_name>` - Start a Docker container.
- `/docker_stop <container_name>` - Stop a Docker container.
- `/docker_ps` - List running Docker containers.
- `/docker_logs <container_name>` - Show logs for a Docker container.
- `/docker_stats` - Show stats for Docker containers.

### Sudo User Commands (Owner Only)

- `/add_sudo <user_id>` - Add a sudo user.
- `/remove_sudo <user_id>` - Remove a sudo user.
- `/sudo_users` - List all sudo users.

## 🔧 Inline Buttons

- **Help**: Display the help menu.
- **Docker**: List all Docker commands.
- **Sudo**: List all sudo commands.
- **Repo**: Link to the GitHub repository.
- **Donate**: Link to the donation page.
- **Bot Channel**: Link to the bot's Telegram channel.
- **Close**: Close the current message.

## 📦 Repository Links

- **GitHub Repo**: [Telegram Bot Manager](https://github.com/zasasamar2129/Server-Bot-Manager)
- **Donate**: [Buy Me a Coffee](https://www.buymeacoffee.com/zasasamar)
- **Bot Channel**: [Telegram Channel](https://t.me/Zpotify1)

## 🛠️ Built With

- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API Client Library
- [Docker](https://www.docker.com/) - Containerization Platform
- [Psutil](https://github.com/giampaolo/psutil) - System and Process Utilities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) for the awesome library.
- [Docker](https://www.docker.com/) for container management.
- [Psutil](https://github.com/giampaolo/psutil) for system stats utilities.

---

Feel free to contribute to this project by opening issues or submitting pull requests. Your feedback and contributions are highly appreciated!

