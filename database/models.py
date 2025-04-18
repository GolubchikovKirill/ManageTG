from sqlalchemy import Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base
from datetime import datetime, timezone
import enum



class ChannelStatus(str, enum.Enum):
    open = "open"
    private = "private"


class ActionType(str, enum.Enum):
    comment = "comment"
    reaction = "reaction"
    view = "view"


class ToneType(str, enum.Enum):
    positive = "positive"
    negative = "negative"
    critical = "critical"
    question = "question"


# Таблица аккаунтов
class Accounts(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(nullable=False, index=True)
    api_id: Mapped[int] = mapped_column(nullable=False)
    api_hash: Mapped[str] = mapped_column(nullable=False)

    proxy_id: Mapped[int] = mapped_column(ForeignKey("proxy.id"), nullable=True, index=True)
    proxy: Mapped["Proxy"] = relationship("Proxy", backref="accounts")


# Таблица прокси
class Proxy(Base):
    __tablename__ = "proxy"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    type: Mapped[str] = mapped_column(default="socks5")
    login: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    password: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    port: Mapped[int] = mapped_column(default=1080, nullable=False)


# Таблица каналов
class Channels(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ChannelStatus] = mapped_column(
        Enum(ChannelStatus, name="channel_status"),
        default=ChannelStatus.open,
        nullable=False
    )
    request_count: Mapped[int] = mapped_column(default=0, nullable=False)
    accepted_request_count: Mapped[int] = mapped_column(default=0, nullable=False)

    actions: Mapped[list["Actions"]] = relationship("Actions", back_populates="channel")

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )


# Таблица действий
class Actions(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)

    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType), nullable=False)

    # Для комментариев
    positive_count: Mapped[int] = mapped_column(default=0, nullable=False)
    negative_count: Mapped[int] = mapped_column(default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(default=0, nullable=False)
    question_count: Mapped[int] = mapped_column(default=0, nullable=False)
    custom_prompt: Mapped[str] = mapped_column(Text, nullable=True)

    action_time: Mapped[int] = mapped_column(default=60, nullable=False)
    random_percentage: Mapped[int] = mapped_column(default=20, nullable=False)

    channel: Mapped["Channels"] = relationship("Channels", back_populates="actions")

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
                                                 onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
                                                 nullable=False)