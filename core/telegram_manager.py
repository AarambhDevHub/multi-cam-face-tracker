import logging
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional
from pathlib import Path
import asyncio
import time

class TelegramManager:
    def __init__(self, token: str, chat_id: str, rate_limit: int):
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        self.last_sent = 0
        self.min_interval = rate_limit
        self.loop = asyncio.new_event_loop()

    async def _initialize_bot(self):
        """Initialize the Telegram bot asynchronously"""
        try:
            self.bot = Bot(token=self.token)
            await self.bot.get_me()  # Test connection
            logging.info("Telegram bot initialized successfully")
        except TelegramError as e:
            logging.error(f"Failed to initialize Telegram bot: {e}")
            self.bot = None

    def send_alert(self, message: str, image_path: Optional[Path] = None):
        """Send alert to Telegram (blocking wrapper)"""
        if not self.bot:
            try:
                self.loop.run_until_complete(self._initialize_bot())
            except Exception as e:
                logging.error(f"Telegram connection failed: {e}")
                return

        async def _send():
            now = time.time()
            if now - self.last_sent < self.min_interval:
                logging.warning(f"Telegram rate limit reached ({self.min_interval}s)")
                return
            try:
                if image_path and image_path.exists():
                    with open(image_path, 'rb') as photo:
                        await self.bot.send_photo(
                            chat_id=self.chat_id,
                            photo=photo,
                            caption=message
                        )
                else:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message
                    )
                self.last_sent = now
                logging.info("Telegram alert sent successfully")
            except TelegramError as e:
                logging.error(f"Failed to send Telegram alert: {e}")

        try:
            self.loop.run_until_complete(_send())
        except Exception as e:
            logging.error(f"Telegram alert failed: {str(e)}")
            # Fallback to saving alert locally
            with open("failed_alerts.log", "a") as f:
                f.write(f"{time.ctime()}: {message}\n")
            if image_path:
                backup_dir = Path("failed_alert_images")
                backup_dir.mkdir(exist_ok=True)
                new_path = backup_dir / f"alert_{int(time.time())}.jpg"
                try:
                    image_path.rename(new_path)
                except Exception as e:
                    logging.error(f"Failed to backup alert image: {e}")
    
    def shutdown(self):
        """Cleanup resources"""
        self._shutdown = True
        self.last_sent = 0
        if self.loop.is_running():
            self.loop.stop()
        
        # Close all pending tasks
        pending = asyncio.all_tasks(loop=self.loop)
        for task in pending:
            task.cancel()
        
        self.loop.close()