from datetime import datetime
import uuid
from typing import List

from sqlalchemy import func, ForeignKey, types, text, select, String
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship, column_property

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    guid: Mapped[uuid.UUID] = mapped_column(types.Uuid, server_default=text("gen_random_uuid()"), primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    profile_picture: Mapped[str] = mapped_column(server_default="some picture")

    roles: Mapped[List["Role"]] = relationship(back_populates="user")
    created_games: Mapped[List["Game"]] = relationship(back_populates="creator")


class Role(Base):
    __tablename__ = 'Roles'

    id: Mapped[int] = mapped_column(primary_key=True)

    user_guid: Mapped[uuid.UUID] = mapped_column(ForeignKey('Users.guid', ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="roles", single_parent=True)

    name: Mapped[str] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(nullable=False)


class Vote(Base):
    __tablename__ = 'Votes'
    user_guid: Mapped[uuid.UUID] = mapped_column(ForeignKey("Users.guid", ondelete="CASCADE"), primary_key=True)
    game_guid: Mapped[uuid.UUID] = mapped_column(ForeignKey("Games.guid", ondelete="CASCADE"), primary_key=True)
    type: Mapped[int] = mapped_column(nullable=False)


class Game(Base):
    __tablename__ = 'Games'

    guid: Mapped[uuid.UUID] = mapped_column(types.Uuid, server_default=text("gen_random_uuid()"), primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    img: Mapped[str] = mapped_column(nullable=False)

    likes_count = column_property(
        select(func.count(Vote.game_guid)).where(
            (Vote.game_guid == guid) & (Vote.type == 1)
        ).correlate_except(Vote)
        .scalar_subquery()
    )
    dislikes_count: Mapped[int] = column_property(
        select(func.count(Vote.game_guid)).where(
            (Vote.game_guid == guid) & (Vote.type == 0)
        ).correlate_except(Vote)
        .scalar_subquery()
    )

    creator_guid: Mapped[uuid.UUID] = mapped_column(ForeignKey('Users.guid', ondelete="CASCADE"), nullable=False)
    creator: Mapped["User"] = relationship(back_populates="created_games", single_parent=True)