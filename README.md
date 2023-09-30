# Telegram Tracker Bot

![Telegram Tracker Bot Logo](your_logo_image_url_here)

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#key-features)
3. [Technologies Used](#technologies-used)
4. [Getting Started](#getting-started)
5. [Usage](#usage)
6. [Database](#database)
7. [Reports](#reports)
8. [Installation](#installation)
9. [Docker Deployment](#docker-deployment)
10. [Contributing](#contributing)
11. [License](#license)

---

## Introduction

Welcome to the Telegram Tracker Bot project! This bot, built using the Aiogram library and a stack of powerful technologies, empowers you to efficiently manage your activities, categories, and track your time right from within your Telegram group.

### Key Features

- **User Registration**: Automatically adds users to the PostgreSQL and Redis databases upon joining a specific Telegram group.

- **Private Chat Interaction**: Users can initiate a private chat with the bot using the `/start` command. The bot responds with a user-friendly menu containing five inline buttons: Categories, Actions, Reports, Trackers, and Exit.

- **Categories Management**: Users can create, delete, update, and display up to 10 categories. Accessible via the "Categories" button.

- **Activities Management**: Similar to categories, users can manage up to 10 activities under each category. Accessible via the "Actions" button.

- **Time Tracking**: The "Trackers" button allows users to start, view duration, stop, or delete trackers for specific activities within chosen categories. Time tracking data is stored in the database.

- **Weekly Reports**: Users can generate and download weekly reports containing all their tracked activities. Also At the end of the week, the bot automatically generates a report based on the users' trackers saved for the week. Reports are exported as Excel spreadsheets.
  
- **Language Selection**: Users can change the language of the application. The application currently supports two languages (English and Russian), and you can easily add more languages as needed, thanks to the Fluentogram library.

These features make the Telegram Tracker Bot a powerful tool for managing and tracking activities within your Telegram group.


Certainly! Here's the updated "Technologies Used" section with links to their respective GitHub pages or home pages if available:

## Technologies Used

- [Aiogram](https://github.com/aiogram/aiogram): A powerful Python framework for building Telegram bots.
- [Asyncpg](https://github.com/MagicStack/asyncpg): An asyncio-based PostgreSQL driver.
- [SQLAlchemy](https://www.sqlalchemy.org/): A SQL toolkit and Object-Relational Mapping (ORM) library.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/): A database migration tool.
- [Openpyxl](https://openpyxl.readthedocs.io/en/stable/): A library for reading and writing Excel files.
- [Pandas](https://pandas.pydata.org/): A data manipulation library.
- [Python-dotenv](https://github.com/theskumar/python-dotenv): For managing environment variables.
- [Pydantic-settings](https://github.com/pydantic/pydantic-settings): Configuration settings management.
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio): A testing framework for asyncio code.
- [pytest-cov](https://github.com/pytest-dev/pytest-cov): A coverage plugin for pytest.
- [APScheduler](https://apscheduler.readthedocs.io/en/stable/): A Python job scheduling library.
- [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/): A template engine.
- [Fluentogram](https://github.com/orsinium/fluentogram): A library for localizing Telegram bot messages.
- [Redis](https://redis.io/): An open-source, in-memory data structure store.
- [PostgreSQL](https://www.postgresql.org/): A powerful, open-source relational database management system.
- [Prometheus](https://prometheus.io/): An open-source monitoring and alerting toolkit.
- [Grafana](https://grafana.com/): An open-source analytics and monitoring platform.
- [PostgreSQL Exporter](https://github.com/prometheus-community/postgres_exporter): A PostgreSQL metric exporter for Prometheus.
- [Redis Exporter](https://github.com/oliver006/redis_exporter): A Prometheus exporter for Redis metrics.
- [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/): An alert handling system for Prometheus.
- [Portainer](https://www.portainer.io/): An open-source container management tool.

These technologies collectively power the Telegram Tracker Bot, enabling its robust functionality.

## Getting Started

Follow these steps to set up and run the Telegram Tracker Bot on your local machine:

1. Clone this repository to your local machine.

2. Install the required dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file and configure your environment variables.

4. Run the bot using:
   ```bash
   python __main__.py
   ```

## Usage

Once the bot is running, users in the Telegram group can interact with it by sending commands and using the inline buttons provided in private chat. Refer to the [Features](#features) section for details on how to use each feature.

## Database

The bot uses PostgreSQL and Redis for data storage. You can find database schemas and migration scripts in the `database` directory.

## Reports

To generate weekly reports, users can click the "Reports" button in the private chat menu. The reports are exported as Excel spreadsheets, containing all tracked activities.

## Installation
1. Go to @BotFather, create a new bot, write down its token, add it to your existing group and make bot an admin. You also need to give it "Delete messages" permission.
2. Clone this repo and cd into it;
3. Copy env_dist to .env (with dot). Warning: files starting with dot may be hidden in Linux, so don't worry if you stop seeing this file, it's still here!
4. Replace default values with your own;

## Docker Deployment

This project can also be deployed using Docker Compose, which includes various containers such as Redis, PostgreSQL, Prometheus, Grafana, PostgreSQL Exporter, Redis Exporter, Alertmanager, Portainer, and a custom image for the Telegram bot (tgbot).

## Contributing

Contributions to this project are welcome! Please see the [Contributing Guidelines](CONTRIBUTING.md) for more details on how to get involved.

## License

This project is licensed under the [MIT License](LICENSE).

---

Thank you for using the Telegram Tracker Bot. I hope this tool enhances your productivity and helps you manage your time effectively. If you encounter any issues or have suggestions for improvements, please don't hesitate to reach out to me. Happy tracking!
