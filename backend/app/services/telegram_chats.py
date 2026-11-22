"""Telegram chat registry.

Records chats that interact with the bot so web-dashboard approvals have a safe
delivery target even when TELEGRAM_DEFAULT_CHAT_ID is not configured.
"""

from sqlalchemy.orm import Session

from ..models import TelegramChat, utcnow


def remember_chat(db: Session, chat) -> TelegramChat:
    chat_id = str(chat.id)
    record = db.get(TelegramChat, chat_id)
    if record is None:
        record = TelegramChat(
            chat_id=chat_id,
            username=getattr(chat, "username", None),
            first_name=getattr(chat, "first_name", None),
        )
        db.add(record)
    else:
        record.username = getattr(chat, "username", None) or record.username
        record.first_name = getattr(chat, "first_name", None) or record.first_name
        record.last_seen = utcnow()
    db.commit()
    db.refresh(record)
    return record


def latest_known_chat_id(db: Session):
    """Return the target chat only when there is exactly one known chat.

    With multiple chats we refuse to guess; configure TELEGRAM_DEFAULT_CHAT_ID
    instead so approvals cannot be delivered to the wrong person.
    """
    chats = (
        db.query(TelegramChat)
        .order_by(TelegramChat.last_seen.desc())
        .limit(2)
        .all()
    )
    if len(chats) == 1:
        return chats[0].chat_id
    return None


def known_chat_count(db: Session) -> int:
    return db.query(TelegramChat).count()
