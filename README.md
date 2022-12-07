# reminder-bot

Simple Telegram bot for reminding you about something

### Dependencies
- aiogram
- croniter

### Build and Run
```
$ git clone https://github.com/Woofka/reminder-bot.git
$ cd reminder-bot
$ docker build -t reminder-bot .
$ docker run --name reminder-bot --rm -d -v data:/app/data reminder-bot <API_TOKEN> <YOUR_TELEGRAM_ID>
```
