from sqlalchemy import Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Accounts(Base):
    __tablename__ = "Accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[bool] = mapped_column(Boolean)
    name: Mapped[str] = mapped_column(index=True)
    last_name: Mapped[str] = mapped_column(index=True)
    phone_number: Mapped[str] = mapped_column(index=True)

    # Связь с прокси через внешний ключ
    proxy_id: Mapped[int] = mapped_column(ForeignKey("Proxy.id"), index=True)

    # Связь с прокси
    proxy: Mapped["Proxy"] = relationship("Proxy", backref="accounts")

    # Связь с каналами
    channels: Mapped[list["Channels"]] = relationship("Channels", backref="account")


class Proxy(Base):
    __tablename__ = "Proxy"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(index=True, unique=True)
    login: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str] = mapped_column(index=True, unique=True)
    port: Mapped[int] = mapped_column(default=1080)

    # избыточная связь с аккаунтами
    # accounts: Mapped[list["Accounts"]] = relationship("Accounts", backref="proxy")


class Channels(Base):
    __tablename__ = "Channels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("Accounts.id"), index=True)
    comment: Mapped[str] = mapped_column(Text)

    # Статус канала (открытый или закрытый)
    status: Mapped[str] = mapped_column(Enum("open", "private", name="channel_status"), default="open")

    # Количество заявок на канал
    request_count: Mapped[int] = mapped_column(default=0)  # Количество поданных заявок
    accepted_request_count: Mapped[int] = mapped_column(default=0)  # Количество принятых заявок

    # Связь с аккаунтом
    account: Mapped["Accounts"] = relationship("Accounts", backref="channels")

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))


class Actions(Base):
    __tablename__ = "Actions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("Channels.id"), index=True)

    # Тип действия: "comment", "reaction", "view"
    action_type: Mapped[str] = mapped_column(Text)

    # Количество действий (например, количество комментариев, реакций или просмотров)
    count: Mapped[int] = mapped_column(default=0)

    # Время для выполнения действия в минутах (например, 60 минут)
    action_time: Mapped[int] = mapped_column(default=60)

    # Разброс времени в процентах (например, ±20%)
    random_percentage: Mapped[int] = mapped_column(default=20)

    # Связь с каналом
    channel: Mapped["Channels"] = relationship("Channels", backref="actions")

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))