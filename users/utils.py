import requests
from django.conf import settings
from .models import OTP
import secrets
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def generate_otp():
    return secrets.randbelow(900000) + 100000  # more secure than randint


def send_telegram_otp(chat_id, otp):
    token = settings.TELEGRAM_BOT_TOKEN
    message = f"Your OTP is: {otp}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=data, timeout=5)

        #  Log non-200 responses
        if response.status_code != 200:
            logger.error(
                "Telegram API HTTP error | status=%s | response=%s",
                response.status_code,
                response.text,
            )
            return False, "Failed to send OTP. Please try again."

        result = response.json()

        #  Log API-level failure
        if not result.get("ok"):
            logger.error(
                "Telegram API returned error | response=%s",
                result
            )
            return False, "Failed to send OTP. Please try again."

        return True, None

    except requests.exceptions.RequestException as e:
        #  Log network exception
        logger.exception(
            "Telegram request failed | chat_id=%s | error=%s",
            chat_id,
            str(e),
        )
        return False, "Network issue. Please try again."


def create_and_send_otp(user):
    """this function create otp_obj and return error if there is any"""
    otp_code = generate_otp()
    otp = OTP(user=user)
    otp.set_code(otp_code)
    otp.save()
    success, error = send_telegram_otp(user.telegram_chat_id, otp_code)

    if success:
        return 
    return error

def generate_token(user):
    token = secrets.token_urlsafe(8)  # short & Telegram-safe
    cache.set(token, user.id, timeout=300)  # expires in 5 minutes
    return token
