# Bot for moderating chats in Telegram
For moderating educational chats in the Czech Republic on Telegram. The bot is currently in the development stage.🚧

## Content
- [Links to get familiar with the bot](#links-to-get-familiar-with-the-bot)
- [Features](#features)
- [Setup and Run](#setup-and-run)
  - [Development](#development)
  - [Production](#production)
- [Commands for moderating](#commands-for-moderating)


## Links to get familiar with the bot
- Bot: @konnekt_moder_bot
- One of the chats with the bot: @cvut_chat


## Features

* ✅ - implemented
* ❌ - will be implemented
* 🚧 - in progress

| Feature | Description | Status |
|---------|-------------|--------|
| Moderating | Base commands for moderating the chat (mute, ban, etc.) | ✅ |
| Welcome message | Sending a welcome message to new chat members | ✅ |
| Saving messages history | Saving messages history to the database | ✅ |
| Captcha | Checking if the user is a bot | ❌ |
| Report | Sending a report to the admins | ❌ |
| ML model | Detecting spam messages | ❌ |

## Architecture

The project now follows a layered Domain-Driven approach:

- `app/domain` contains domain models.
- `app/infrastructure` provides infrastructure code like database repositories.
- `app/application` holds application services.
- `app/presentation` includes the Telegram interface with handlers and middlewares.

Run the bot with:

```bash
python -m app.presentation.telegram
```


## Setup and Run
1) Set up the environment:
```bash
cp .env.example .env
```
2) Fill in the `.env` file with your bot token.

### Development
3) Run the bot in development mode:
```bash
docker-compose -f docker-compose.dev.yaml up --build
```

### Production
3) Run the bot in production mode:
```bash
docker-compose up --build
```


## Commands for moderating

* ✅ - implemented
* ❌ - will be implemented
* 🚧 - in progress
* 👮 - admins
* 🧑‍🎓 - user 

| Command | Description | Status | For whom |
|---------|-------------|--------|----------|
| `/mute *int*` | Mutes a user in the chat for the specified time in minutes. Default: 5 minutes. | ✅ | 👮 |
| `/unmute` | Unmutes a user in the chat. | ✅ | 👮 |
| `/ban` | Bans a user from the chat and adds to the blacklist. | ✅ | 👮 |
| `/unban` | Unbans a user from the blacklist. | ✅ | 👮 |
| `black` | Adds a user to the blacklist for all chats. | ✅ | 👮 |
| `welcome` | Enables a welcome message for new chat members. | ✅ | 👮 |
| `welcome <text>` | Changes the welcome message. | ✅ | 👮 |
| `welcome -t <int>` | Changes the time for auto-deleting the welcome message. | 🚧 | 👮 |
| `welcome -b` | Enables a simple button for checking if the user is a bot in the welcome message. | ❌ | 👮 |
| `welcome -c` | Enables a captcha button for checking if the user is a bot in the welcome message. | ❌ | 👮 |
| `welcome -s` | Shows the current settings for the welcome message. | ❌ | 👮 |
| `/chats` | Sends a list of educational chats from the `ChatLinks` table in the `/db/moder_bot.db` database. | ✅ | 🧑‍🎓 |
| `report` | Sends a report to the admins | ❌ | 🧑‍🎓 |
