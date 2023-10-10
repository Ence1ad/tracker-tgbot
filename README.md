
# tracker-tgbot  

---
[![](https://img.shields.io/github/license/Ence1ad/tracker-tgbot?style=flat-square)](https://github.com/Ence1ad/tracker-tgbot/LICENSE)
[![](https://img.shields.io/badge/Python-3.10&nbsp;|&nbsp;3.11-blue)](https://www.python.org/downloads/)
![](https://img.shields.io/badge/version-0.0.3%20-brightgreen?style=flat-square)
[![CI](https://github.com/Ence1ad/tracker-tgbot/actions/workflows/ci-tests.yml/badge.svg?branch=dev)](https://github.com/Ence1ad/tracker-tgbot/actions/workflows/ci-tests.yml)
[![codecov](https://codecov.io/gh/Ence1ad/tracker-tgbot/graph/badge.svg?)](https://codecov.io/gh/Ence1ad/tracker-tgbot)
![](https://img.shields.io/github/forks/Ence1ad/tracker-tgbot?style=flat-square)
![](https://img.shields.io/github/stars/Ence1ad/tracker-tgbot?style=flat-square)
[![telegram](https://img.shields.io/badge/Telegram-Join-blue)](https://t.me/)


**Project Description:**
Welcome to the **tracker-tgbot**, a versatile Telegram bot designed to simplify task and time tracking. This bot seamlessly integrates with your Telegram groups and private chats, providing a powerful platform for managing your activities and generating insightful reports.

## Table of Contents  
  
1. [Introduction](#introduction)  
2. [Features](#key-features)  
3. [Usage](#how-it-works)  
4. [Getting Started](#getting-started)  
5. [Technologies Used](#technologies-used)  
6. [Project Roadmap](#project-roadmap)  
7. [Contributing](#contributing)  
8. [License](#license)  
  
---  
  
## Introduction

### Overview

## Key Features

- **Monitoring and Metrics**: This project incorporates monitoring tools to help you gain insights into the performance and health of various components. The primary monitoring stack includes Prometheus, Grafana, PostgreSQL Exporter, Redis Exporter, and Alertmanager. These tools offer several advantages, such as real-time metrics, alerting, and visualization, to ensure your application is running smoothly.

- **Docker Management**: This project includes Portainer, a powerful open-source Docker management tool that simplifies container management, deployment, and monitoring.

## How It Works

**Joining a Group:**
When you're added to a specific Telegram group, the bot automatically registers you in both a PostgreSQL and Redis database.

**Private Chat:**
In a private chat with the bot, simply use the `/start` command to initiate the interaction. The bot responds by presenting a menu with five inline buttons: Categories, Actions, Reports, Trackers, and Exit.

**Language Selection**: 
- Users can change the language of the application simply use `/settings` command. The application currently supports two  languages (English and Russian). 

**Bot manual**
- If you need a full manual on how the bot works, you can always use the `/help` command.

With **tracker-tgbot**, stay organized, boost productivity, and gain valuable insights into your daily activities—all within your Telegram chat. Start using it today!
  
## Getting Started  
  
Follow these steps to set up and run the **tracker-tgbot** on your local machine:  
  
### Prerequisites  
  
- Python 3.9+  
- Pip (Python package manager)  
- Docker (For containerization)  
  
### Installation  

1. **Create a New Bot**: To create a new bot, use the link [BotFather](https://t.me/BotFather) and send the command `/newbot`. Follow the instructions provided by BotFather.

2. **Add the bot to your existing group and make it an administrator.**
  
3. **Clone the repository:**
    ```bash
    git clone https://github.com/Ence1ad/tracker-tgbot.git  
    ```

4. **Navigate to the project directory:**:  
  
    ```bash  
    cd tracker-tgbot
    ```  
  
5. **Create a virtual environment (optional but recommended)**:  
  
    ```bash  
    python -m venv venvsource venv/bin/activate # On Windows, use "venv\Scripts\activate"
    ```  
  
6. **Install project dependencies:**:  
  
    ```bash  
    pip install -r requirements.txt
    ```  
  
7. **Create an .env file based on the provided .env.example:**  
  
    ```bash  
    cp .env.example .env
    ```  
  
8. **Open the .env file in a text editor and fill in the required configuration values.** 
    ```env
    # Database Configuration
    POSTGRES_USER= # PostgreSQL database superuser.  
    POSTGRES_PASSWORD= # Password for the PostgreSQL database superuser.
    ...

    # Bot API Configuration  
    BOT_TOKEN= # Bot api token received from the bot-father  
    GROUP_ID= # Your group or supergroup chat id
    ```
9. **Install Docker Compose**: To get all the features, please [install docker engine](https://docs.docker.com/engine/install/) on your host.

10. **Alertmanager notification** To receive an alert notification from alertmanager, set up an email notification configs. 
Open the alertmanager.yml and enter your email credentials:
   ```yml
       email_configs:
        - to: '<login>gmail.com' # Enter the gmail login that will receive alert notifications
          from: '<login>@gmail.com' # Enter the gmail login that will send alert notifications
          smarthost: smtp.gmail.com:587
          auth_username: '<login>@gmail.com' # Enter the gmail login that will send alert notifications
          auth_identity: '<login>@gmail.com' # Enter the gmail login that will send alert notifications
          auth_password: 'google-app-password' # if you are using gmail create google app password -> https://support.google.com/accounts/answer/185833?hl=en
          send_resolved: true
   ```
11. Run the following command to launch docker compose file:
  ```bash
  docker-compose -f docker-compose.yml up -d
  ```
  
## Technologies Used  

## Project Roadmap

## Contributing  
  
Contributions to this project are welcome! Please see the [Contributing Guidelines](CONTRIBUTING.md) for more details on  how to get involved.  
  
## License  
  
This project is licensed under the [MIT License](LICENSE).  
  
---  
  
Thank you for using the **tracker-tgbot**. I hope this tool enhances your productivity and helps you manage your time  effectively. If you encounter any issues or have suggestions for improvements, please don't hesitate to reach out to me.  Happy tracking!