"""Telegram bot integration — polling for local development.

The bot submits missions to the same orchestrator used by the web dashboard.
Outbound delivery only happens after an explicit human approval.
"""

import logging

from ..config import settings

logger = logging.getLogger("nexus.telegram")


class TelegramUnavailable(Exception):
    pass


class TelegramManager:
    def __init__(self):
        self.app = None
        self.running = False
        self.last_error = None

    @property
    def configured(self) -> bool:
        return settings.telegram_configured

    async def start(self):
        if not self.configured:
            logger.info("Telegram token not configured; bot disabled.")
            return
        try:
            from telegram.ext import (
                Application,
                CommandHandler,
                MessageHandler,
                filters,
            )

            app = (
                Application.builder()
                .token(settings.telegram_bot_token)
                .build()
            )
            app.add_handler(CommandHandler("start", self._cmd_start))
            app.add_handler(CommandHandler("help", self._cmd_help))
            app.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_text)
            )

            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            self.app = app
            self.running = True
            self.last_error = None
            logger.info("Telegram bot polling started.")
        except Exception as exc:  # noqa: BLE001 - never crash the API
            self.running = False
            self.last_error = str(exc)
            logger.exception("Failed to start Telegram bot")

    async def stop(self):
        if not self.app:
            return
        try:
            if self.app.updater and self.app.updater.running:
                await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
        except Exception:  # noqa: BLE001
            logger.exception("Error while stopping Telegram bot")
        finally:
            self.app = None
            self.running = False

    async def send_message(self, text: str, chat_id: int) -> str:
        if not self.running or not self.app:
            raise TelegramUnavailable("Telegram bot is not running")
        message = await self.app.bot.send_message(chat_id=chat_id, text=text)
        return str(message.message_id)

    def _allowed(self, chat_id) -> bool:
        return settings.telegram_chat_allowed(chat_id)

    def _remember_chat(self, chat):
        from ..database import SessionLocal
        from ..services.telegram_chats import remember_chat

        db = SessionLocal()
        try:
            remember_chat(db, chat)
        except Exception:  # noqa: BLE001 - never break message handling
            logger.exception("Failed to remember Telegram chat")
        finally:
            db.close()

    async def _cmd_start(self, update, context):
        chat_id = update.effective_chat.id
        if not self._allowed(chat_id):
            await update.message.reply_text(
                "⛔ This chat is not authorised to use NEXUS."
            )
            return
        self._remember_chat(update.effective_chat)
        await update.message.reply_text(
            "🛰️ NEXUS online.\n\n"
            "Send me an objective in plain language and I will research it, "
            "build a plan and draft a Telegram announcement for your approval.\n\n"
            "Try: Organize a technical workshop for 100 students within 10 days."
        )

    async def _cmd_help(self, update, context):
        chat_id = update.effective_chat.id
        if not self._allowed(chat_id):
            await update.message.reply_text(
                "⛔ This chat is not authorised to use NEXUS."
            )
            return
        self._remember_chat(update.effective_chat)
        await update.message.reply_text(
            "NEXUS commands\n\n"
            "/start – connect to NEXUS\n"
            "/help – show this help\n\n"
            "Any other message is treated as a mission objective. "
            "NEXUS will respond with the plan and the draft announcement, "
            "which must be approved in the web dashboard before it is sent."
        )

    async def _on_text(self, update, context):
        chat_id = update.effective_chat.id
        if not self._allowed(chat_id):
            await update.message.reply_text(
                "⛔ This chat is not authorised to use NEXUS."
            )
            return

        objective = (update.message.text or "").strip()
        if len(objective) < 3:
            await update.message.reply_text(
                "Please send a mission objective (at least 3 characters)."
            )
            return

        self._remember_chat(update.effective_chat)
        await update.message.reply_text(
            "🧠 Mission received. Research, planning and communication agents "
            "are working…"
        )

        from ..database import SessionLocal
        from ..services.mission_service import create_mission, run_mission

        db = SessionLocal()
        try:
            mission = create_mission(
                db,
                objective,
                source="telegram",
                source_chat_id=str(chat_id),
            )
            await run_mission(db, mission)
            db.refresh(mission)

            lines = [
                f"✅ Mission {mission.id[:8]} — {mission.status}",
                "",
                mission.summary or "Mission processed.",
            ]
            pending = next(
                (a for a in mission.approvals if a.status == "pending"), None
            )
            if pending:
                lines += [
                    "",
                    "📝 Draft announcement awaiting approval:",
                    "",
                    pending.content,
                    "",
                    "Approve or reject it in the NEXUS dashboard.",
                ]
            if mission.error:
                lines += ["", f"⚠️ {mission.error}"]

            text = "\n".join(lines)
            await update.message.reply_text(text[:4000])
        except Exception as exc:  # noqa: BLE001
            logger.exception("Telegram mission failed")
            await update.message.reply_text(f"⚠️ Mission failed: {exc}")
        finally:
            db.close()


telegram_manager = TelegramManager()
