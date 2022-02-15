# notifico-bot

This project is just an experiment. No further updates are planned (Grafana does this and better).

## Description

Notifico is a platform for creating a Bot-based logging system.

It is possible to send a message to the bots using the REST Api, or execute periodic tests and get notified when something goes wrong.

At the moment Notifico only supports ping tests.

## How to use

1. Create an account and confirm the email address
2. In the dashboard create an app
3. Add a channel: connect to the Telegram Bot or add a Discord webhook
4a. Add a periodic test
4b. Send a GET request to `/api/messages` to forward a message to all bots: the required field names are `text` and `token`

## How to execute

1. Copy `template.env` into `.env` and insert the required values (see below for the guide)
2. Point the Telegram Bot Webhook to Notifico: visit `https://api.telegram.org/bot<telegram_bot_token>/setWebhook?url=<notifico_url>/api/webhook/telegram/<notifico_webhook_token>`
3. Run `docker-compose -f docker-compose-prod.yml up -d --build`

### Environment variables

- `SECRET_KEY`: random value, used by Django
- `MYSQL_PASSWORD`: password for MySQL user. DO NOT CHANGE AFTER FIRST BOOT (or delete database data)
- `GTAG`: Gtag from Google Analytics (optional)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token from Bot Father
- `TELEGRAM_WEBHOOK_TOKEN`: A random value used to secure the telegram webhook url

## Project structure

TBD

## Known bugs

- Sometimes ping fails and the bot sends a failure message. A retry should be set.
