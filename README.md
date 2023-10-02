# tracker-tgbot  
  
![Telegram Tracker Bot Logo](your_logo_image_url_here)  

**Project Description:**
Welcome to the **tracker-tgbot**, a versatile Telegram bot designed to simplify task and time tracking. This bot seamlessly integrates with your Telegram groups and private chats, providing a powerful platform for managing your activities and generating insightful reports.

## Table of Contents  
  
1. [Introduction](#introduction)  
2. [Features](#key-features)  
3. [Usage](#how-it-works)  
4. [Getting Started](#getting-started)  
5. [Technologies Used](#technologies-used)  
6. [Project Roadmap](#Project Roadmap)  
7. [Contributing](#contributing)  
8. [License](#license)  
  
---  
  
## Introduction

### Overview
The **tracker-tgbot** offers an array of features that empower users to efficiently organize their tasks, track their time, and analyze their productivity. Whether you're working individually or within a group, this bot streamlines your workflow and enhances your control over activities.

## Key Features  

- **Categories and Actions:** Easily create, delete, update, and display categories and actions right from your Telegram chat.

- **Trackers:** Initiate, view duration, stop, or delete trackers for specific activities within chosen categories.

- **Reports:** Generate comprehensive weekly reports, exported as Excel spreadsheets with embedded graphs for data visualization.

- **Monitoring and Metrics**: This project incorporates monitoring tools to help you gain insights into the performance and health of various components. The primary monitoring stack includes Prometheus, Grafana, PostgreSQL Exporter, Redis Exporter, and Alertmanager. These tools offer several advantages, such as real-time metrics, alerting, and visualization, to ensure your application is running smoothly.

- **Docker Management**: This project includes Portainer, a powerful open-source Docker management tool that simplifies container management, deployment, and monitoring.

## How It Works

**Joining a Group:**
When you're added to a specific Telegram group, the bot automatically registers you in both a PostgreSQL and Redis database.

**Private Chat:**
In a private chat with the bot, simply use the `/start` command to initiate the interaction. The bot responds by presenting a menu with five inline buttons: Categories, Actions, Reports, Trackers, and Exit.

**Categories and Actions:**
- Categories: Manage up to 10 categories with options for creation, deletion, updating, and viewing.
- Actions: Create and manage activities, each associated with a category.

**Trackers:**
- Initiate: Start tracking time for a selected activity within a category.
- View Duration: Check the duration of ongoing activities.
- Stop: Stop tracking an activity, calculate its duration, and store the data.

**Reports:**
- Users can generate and download weekly reports containing all their tracked activities. Also At  the end of the week, the bot automatically generates a report based on the users' trackers saved for the week. Reports are exported as Excel spreadsheets.  
- Data Visualization: Analyze your tracked data through embedded graphs within the report.

**Language Selection**: 
- Users can change the language of the application simply use `/settings` command. The application currently supports two  languages (English and Russian). 

**Bot manual**
- If you need a full manual on how the bot works, you can always use the help command.

With **tracker-tgbot**, stay organized, boost productivity, and gain valuable insights into your daily activities—all within your Telegram chat. Start using it today!
  
## Getting Started  
  
Follow these steps to set up and run the **tracker-tgbot** on your local machine:  
  
### Prerequisites  
  
- Python 3.9+  
- Pip (Python package manager)  
- Docker (optional, for containerization)  
  
### Installation  

1. **Create a New Bot**: To create a new bot, use the link [BotFather](https://t.me/BotFather) and send the command `/newbot`. Follow the instructions provided by BotFather.

2. **Add the bot to your existing group and make it an administrator.**
  
3. **Clone the repository:**  
  
```bash  
https://github.com/Ence1ad/tracker-tgbot.git  
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

9. **Run the bot using:**  
  
```bash  
python tgbot/__main__.py
```  

10. **Start Docker Compose**: To get all the features, please [install docker engine](https://docs.docker.com/engine/install/) on your host and run the following command to launch docker compose file:

```bash
docker-compose -f docker-compose.yml up -d
```
  
## Technologies Used  
  
- [Aiogram](https://github.com/aiogram/aiogram): A powerful Python framework for building Telegram bots.  
- [Asyncpg](https://github.com/MagicStack/asyncpg): An asyncio-based PostgreSQL driver.  
- [SQLAlchemy](https://www.sqlalchemy.org/): A SQL toolkit and Object-Relational Mapping (ORM) library.  
- [Alembic](https://alembic.sqlalchemy.org/en/latest/): A database migration tool.  
- [Openpyxl](https://openpyxl.readthedocs.io/en/stable/): A library for reading and writing Excel files.  
- [Pandas](https://pandas.pydata.org/): A data manipulation library.  
- [Pydantic-settings](https://github.com/pydantic/pydantic-settings): Configuration settings management.  
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio): A testing framework for asyncio code.  
- [pytest-cov](https://github.com/pytest-dev/pytest-cov): A coverage plugin for pytest.  
- [APScheduler](https://apscheduler.readthedocs.io/en/stable/): A Python job scheduling library.  
- [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/): A template engine.  
- [Fluentogram](https://github.com/orsinium/fluentogram): A library for localizing Telegram bot messages.  
- [Redis](https://redis.io/): An open-source, in-memory data structure store.  
- [PostgreSQL](https://www.postgresql.org/): A powerful, open-source relational database management 
- [Docker](https://www.docker.com/): A platform for developing, shipping, and running applications in containers.
- [Docker Compose](https://docs.docker.com/compose/): A tool for defining and running multi-container Docker applications.system.  
- [Prometheus](https://prometheus.io/): An open-source monitoring and alerting toolkit.  
- [Grafana](https://grafana.com/): An open-source analytics and monitoring platform.  
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter): A PostgreSQL metric exporter for  
Prometheus.  
- [Redis Exporter](https://github.com/oliver006/redis_exporter): A Prometheus exporter for Redis metrics.  
- [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/): An alert handling system for Prometheus.  
- [Portainer](https://www.portainer.io/): An open-source container management tool.
  
These technologies collectively power the **tracker-tgbot**, enabling its robust functionality.  
## Project Roadmap

- **Feature 1: Report Generation Options**
  - Description: Add the capability for users to generate daily, monthly, and yearly reports.
  - Benefits: Users will have more flexibility in viewing and analyzing their data.

- **Feature 2: Data Visualization with Plotly**
  - Description: Implement data visualization features using the Plotly library to create charts, graphs, and bars based on users' tracked data.
  - Benefits: Users will be able to visualize their data in a more interactive and informative way.

- **Enhancement: Test Suite Improvement**
  - Description: Strengthen the test suite with more robust unit and functional tests to ensure the reliability of the application.
  - Benefits: Improved test coverage will lead to better code quality and fewer issues.

## Contributing  
  
Contributions to this project are welcome! Please see the [Contributing Guidelines](CONTRIBUTING.md) for more details on  how to get involved.  
  
## License  
  
This project is licensed under the [MIT License](LICENSE).  
  
---  
  
Thank you for using the **tracker-tgbot**. I hope this tool enhances your productivity and helps you manage your time  effectively. If you encounter any issues or have suggestions for improvements, please don't hesitate to reach out to me.  Happy tracking!