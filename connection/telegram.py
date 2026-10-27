import logging
import os
from contextlib import contextmanager
from typing import Callable, Optional

import telebot

logger = logging.getLogger("connection.telegram")


class TelegramProgressHandler(logging.Handler):

    def __init__(self, bot, chat_id: int, level: int = logging.INFO):
        super().__init__(level=level)
        self.bot = bot
        self.chat_id = chat_id
        self._muted = False

    def emit(self, record: logging.LogRecord) -> None:
        if self._muted or record.name.startswith("connection"):
            return
        self._muted = True
        try:
            self.bot.send_message(self.chat_id, f"• {record.getMessage()}")
        except Exception:
            logger.warning("Failed to forward log line to chat %s", self.chat_id)
        finally:
            self._muted = False


class TelegramConnection:

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not self.token:
            raise ValueError("Telegram bot token is required. Set TELEGRAM_BOT_TOKEN env var or pass token.")

        self.bot = telebot.TeleBot(self.token)
        self.on_message: Optional[Callable[[str], str]] = None
        self._register_handlers()

    def _register_handlers(self) -> None:
        @self.bot.message_handler(commands=["start"])
        def handle_start(message):
            self.bot.reply_to(message, "Bot connected. Send me a message to begin.")

        @self.bot.message_handler(func=lambda m: bool(getattr(m, "text", None)))
        def handle_text(message):
            user_input = message.text.strip()
            logger.info("Incoming message from chat %s: %r", message.chat.id, user_input)
            with self._progress_stream(message.chat.id):
                reply = self._dispatch(user_input)
            self.bot.reply_to(message, reply)

    @contextmanager
    def _progress_stream(self, chat_id: int):
        handler = TelegramProgressHandler(self.bot, chat_id)
        root = logging.getLogger()
        root.addHandler(handler)
        try:
            yield handler
        finally:
            root.removeHandler(handler)

    def _dispatch(self, user_input: str) -> str:
        if self.on_message is None:
            return "Connection is ready. Wire a handler (core.run) into on_message to process tasks."
        return self.on_message(user_input)

    def connect(self, handler: Callable[[str], str]) -> None:
        self.on_message = handler
        logger.info("Message handler connected")

    def start(self) -> None:
        logger.info("Telegram bot polling started")
        self.bot.infinity_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    TelegramConnection().start()