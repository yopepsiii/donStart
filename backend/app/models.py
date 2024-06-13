import datetime
from typing import List

from sqlalchemy import ForeignKey, func, Table
from sqlalchemy.orm import relationship, declarative_base, mapped_column, Mapped
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()

class User(Base):
    __tablename__: str = "Users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    image: Mapped[str] = mapped_column(server_default='')
    role: Mapped[str] = mapped_column(server_default='Пользователь')

    created_games: Mapped[List["Game"]] = relationship("Game", back_populates="creator")

    liked_games: Mapped[List["Game"]] = relationship(
        "Game",
        back_populates="users_that_liked"
    )


class Game(Base):
    __tablename__: str = "Games"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    picture: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey("Users.id", onupdate="CASCADE", ondelete="CASCADE"))
    creator: Mapped["User"] = relationship("User", back_populates="created_games")

    users_that_liked: Mapped[List["User"]] = relationship(
        "User",
        back_populates="liked_games"
    )


class Admin(Base):
    __tablename__: str = "Admins"
    id: Mapped[int] = mapped_column(ForeignKey("Users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User")
