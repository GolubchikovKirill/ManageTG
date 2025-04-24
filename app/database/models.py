from sqlalchemy import Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
from datetime import datetime, timezone
from app.database.enum_db import ChannelStatus


class BaseAction(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    action_time: Mapped[int] = mapped_column(default=60, nullable=False)
    random_percentage: Mapped[int] = mapped_column(default=20, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )

class Accounts(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    is_authorized: Mapped[bool] = mapped_column(Boolean, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, index=True, default="Unknown")
    last_name: Mapped[str] = mapped_column(nullable=False, index=True, default="Unknown")
    phone_number: Mapped[str] = mapped_column(nullable=False, index=True)
    api_id: Mapped[int] = mapped_column(nullable=False)
    api_hash: Mapped[str] = mapped_column(nullable=False)

    proxy_id: Mapped[int] = mapped_column(ForeignKey("proxy.id"), nullable=True, index=True)
    proxy: Mapped["Proxy"] = relationship("Proxy", backref="accounts")


class Proxy(Base):
    __tablename__ = "proxy"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    type: Mapped[str] = mapped_column(default="socks5")
    login: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    password: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    port: Mapped[int] = mapped_column(default=1080, nullable=False)


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

    comment_actions: Mapped[list["CommentActions"]] = relationship("CommentActions", back_populates="channel")
    reaction_actions: Mapped[list["ReactionActions"]] = relationship("ReactionActions", back_populates="channel")
    view_actions: Mapped[list["ViewActions"]] = relationship("ViewActions", back_populates="channel")

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False
    )


class CommentActions(BaseAction):
    __tablename__ = "comment_actions"

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)
    positive_count: Mapped[int] = mapped_column(default=0, nullable=False)
    neutral_count: Mapped[int] = mapped_column(default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(default=0, nullable=False)
    question_count: Mapped[int] = mapped_column(default=0, nullable=False)
    custom_prompt: Mapped[str] = mapped_column(Text, nullable=True)

    channel: Mapped["Channels"] = relationship("Channels", back_populates="comment_actions")


class ReactionActions(BaseAction):
    __tablename__ = "reaction_actions"

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)
    emoji: Mapped[str] = mapped_column(default="❤️", nullable=False)
    count: Mapped[int] = mapped_column(default=10, nullable=False)

    channel: Mapped["Channels"] = relationship("Channels", back_populates="reaction_actions")


class ViewActions(BaseAction):
    __tablename__ = "view_actions"

    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False, index=True)
    count: Mapped[int] = mapped_column(default=10, nullable=False)
    post_link: Mapped[str] = mapped_column(Text, nullable=True)

    channel: Mapped["Channels"] = relationship("Channels", back_populates="view_actions")
