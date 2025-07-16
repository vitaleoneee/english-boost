# English Boost

English Boost is a Django web application designed to help users learn English. The project offers an interactive and user-friendly platform with a spaced repetition system (SRS), a personal dictionary, and an achievement system.

## Features

- 📚 Personal dictionary — add words to study and listen to pronunciation.
- 🔁 Spaced repetition (SRS) — words appear in the test at the right time so you don’t forget them.
- 🏆 Achievement system — get rewards for progress and regular practice.
- 🔐 Authentication system — convenient and simple registration and login system.
- 🛠️ Admin panel with Unfold — a modern admin panel.

## Technologies

* Django 5.2
* PostgreSQL
* Redis
* django-allauth
* django-unfold

## Installation

1. Clone the repository or copy the project folder to your local machine.
    ```bash
    git clone https://github.com/vitaleoneee/english-boost.git

2. Navigate to the project folder:
   ```bash
   cd english-boost
3. Create and activate a virtual environment:
    ```bash
   python -m venv .venv
   source .venv/bin/activate      # for Linux/macOS
    .venv\Scripts\activate         # for Windows
4. Install dependencies:
   ```bash
   pip install -r requirements.txt

5. Install Redis
- Windows:
    Download the installer from [here](https://github.com/tporadowski/redis/releases)
- Ubuntu/Debian:
    ```bash
    sudo apt update
    sudo apt install redis-server
    sudo service redis-server start
- macOS (Homebrew):
    ```bash
    brew install redis
    brew services start redis

6. Open the folder and Start Redis
    ```bash
   redis-server

7. Create a .env file based on the example:
   ```bash
   cp .env.example .env
   
8. Specify variables in .env 
    ```bash
    DEBUG=True
    SECRET_KEY=your-secret-key
    DB_NAME=your-db-name
    DB_USER=your-user
    DB_PASSWORD=your-password
    DB_HOST=localhost
    DB_PORT=5432
    EMAIL_HOST_USER=your-email@gmail.com
    EMAIL_HOST_PASSWORD=your-email-password
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB=0
   
9. Set up the database (*Make sure PostgreSQL is running and the database is created.*)
    ```bash
    python manage.py migrate
10. Create a superuser
    ```bash
    python manage.py createsuperuser
11. Start the server
    ```bash
    python manage.py runserver

## 📸 Screenshots

### 🔍 Main page
![First photo - main page](screenshots/main-page1.png)
![Second photo - main page](screenshots/main-page2.png)

### 🧠 Srs system
![SRS system](screenshots/srs-system.png)

### 🏆 Achievements
![Achievements](screenshots/achievements.png)

### ⚙️ Admin Panel
![Admin Panel](screenshots/admin-panel.png)