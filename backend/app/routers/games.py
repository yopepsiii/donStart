import hashlib
import json
import time
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, session
from starlette import status

from .. import models
from ..config import settings
from ..database import get_db
from ..oauth2 import get_current_user
from ..schemas import game_schemas
from ..utils import validate_list, validate

router = APIRouter(prefix="/games", tags=["Games"])


# Получить все игры

@router.get("", response_model=List[game_schemas.GameOut])
@cache(expire=60*60, namespace="games")
async def get_games(db: Session = Depends(get_db)):
    games = db.query(models.Game).all()
    return validate_list(values=games, class_type=game_schemas.GameOut)


# Получить игру по GUID
@router.get("/{guid}", response_model=game_schemas.GameFullInfo)
@cache(expire=60*60, namespace="game_by_guid")
async def get_game(guid: uuid.UUID, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.guid == guid).first()
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game {guid} doesn't exist")
    return validate(value=game, class_type=game_schemas.GameFullInfo)


# Создать новую игру
@router.post("", response_model=game_schemas.GameOut, status_code=status.HTTP_201_CREATED)
async def create_game(game_data: game_schemas.GameCreate, db: session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    game = models.Game(creator_guid=current_user.guid, **game_data.dict())
    db.add(game)
    db.commit()
    db.refresh(game)

    await FastAPICache.clear()

    return game


# Удалить игру
@router.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(guid: uuid.UUID, db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    game_query = db.query(models.Game).filter(models.Game.guid == guid)
    game = game_query.first()

    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game {guid} doesn't exist")
    if game.creator_guid != current_user.guid and current_user.email != settings.owner_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't delete games from other users")

    await FastAPICache.clear()

    game_query.delete(synchronize_session=False)
    db.commit()


@router.patch("/{guid}", response_model=game_schemas.GameOut)
async def update_game(guid: uuid.UUID, updated_game_data: game_schemas.GameUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    game_query = db.query(models.Game).filter(models.Game.guid == guid)
    game = game_query.first()

    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game {guid} doesn't exist")
    if game.creator_guid != current_user.guid and current_user.email != settings.owner_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't update games from other users")

    to_update = updated_game_data.dict(exclude_unset=True)

    if to_update:
        game_query.update(to_update, synchronize_session=False)
        db.commit()
        db.refresh(game)

        await FastAPICache.clear()

    return game
