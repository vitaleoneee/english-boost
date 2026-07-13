import httpx
from django.conf import settings


class TelegramError(Exception):
    pass


class TelegramConfigurationError(TelegramError):
    pass


class TelegramTemporaryError(TelegramError):
    pass


class TelegramPermanentError(TelegramError):
    pass


def send_telegram_message(text):
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_SUPPORT_CHAT_ID:
        raise TelegramConfigurationError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_SUPPORT_CHAT_ID must be configured"
        )

    url = (
        f"{settings.TELEGRAM_API_BASE_URL}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:
        response = httpx.post(
            url,
            data={
                "chat_id": settings.TELEGRAM_SUPPORT_CHAT_ID,
                "text": text,
            },
            timeout=settings.TELEGRAM_REQUEST_TIMEOUT,
        )
    except (httpx.TimeoutException, httpx.NetworkError):
        raise TelegramTemporaryError(
            "Telegram API is temporarily unavailable"
        ) from None

    if response.status_code == 429 or response.status_code >= 500:
        raise TelegramTemporaryError(
            f"Telegram API returned temporary status {response.status_code}"
        )
    if response.status_code >= 400:
        raise TelegramPermanentError(
            f"Telegram API rejected the request with status {response.status_code}"
        )

    try:
        payload = response.json()
    except ValueError:
        raise TelegramTemporaryError("Telegram API returned invalid JSON") from None

    if payload.get("ok") is not True:
        error_code = payload.get("error_code")
        error_class = (
            TelegramTemporaryError
            if error_code == 429 or (isinstance(error_code, int) and error_code >= 500)
            else TelegramPermanentError
        )
        raise error_class(f"Telegram API returned error code {error_code}")
