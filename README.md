# Telegram OTP Verification

A Django-based authentication system that allows users to log in using phone-number-based OTP verification through Telegram instead of SMS.

## Features

* Phone number-based user registration and login
* OTP delivery using Telegram Bot API
* Telegram account linking using secure token-based verification
* Hashed OTP storage for improved security
* OTP expiration and resend functionality
* Webhook-based Telegram integration
* POST-only OTP resend workflow
* Secure webhook validation using Telegram secret token

## Tech Stack

* Python
* Django
* Telegram Bot API
* HTML, CSS, Javascript

## How It Works

1. User registers or logs in using a phone number.
2. If Telegram is not linked, the user is redirected to a verification page.
3. A secure Telegram deep link is generated using a temporary cache token.
4. User opens the Telegram bot link and starts the bot.
5. Telegram webhook receives the request and links the user’s Telegram chat ID.
6. OTP is generated, hashed, saved, and sent to the user on Telegram.
7. User enters the OTP in the Django app.
8. If the OTP is valid and not expired, the user is logged in successfully.

## Security Highlights

* OTP is stored in hashed form using Django password hashing utilities.
* OTP verification uses secure password-checking logic.
* Telegram webhook is protected using a secret token.
* Account linking token expires automatically using Django cache.
* OTP resend is allowed only through POST requests.
* OTP expires after a fixed time limit.

```

## Environment Variables

Create a `.env` file or configure these values in your Django settings:

```text
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret
```

## Setup Instructions

1. Clone the repository:

```bash
git clone <repository-url>
cd telegram_otp_verification
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

## Telegram Webhook Setup

Set your Telegram webhook using:

```bash
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_WEBHOOK_URL>&secret_token=<YOUR_SECRET_TOKEN>
```

For local testing, you can use tools like ngrok to expose your local Django server.

## Future Improvements

* Add rate limiting for OTP resend
* Add OTP attempt limit
* Improve UI design
* Add automated tests
* Add Docker support
