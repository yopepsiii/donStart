import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from sqlalchemy.orm import Session
from starlette import status

from backend.app import models
from backend.app.database import get_db
from backend.app.oauth2 import get_current_user
from backend.app.schemas import favourite_schemas

router = APIRouter(prefix="/favourites", tags=["Favourites"])


@router.post("")
async def add_remove_to_favourite(favourite_data: favourite_schemas.Favourite, db: Session = Depends(get_db),
                                current_user: models.User = Depends(get_current_user)):
    game = db.query(models.Game).filter(models.Game.guid == favourite_data.game_guid).first()
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Game {favourite_data.game_guid} does not exist")
    user = db.query(models.User).filter(models.User.guid == current_user.guid).first()
    if game in user.favourite_games:
        user.favourite_games.remove(game)
        db.commit()

        await FastAPICache.clear()
        return {"message": "Game successfully removed from favourites"}
    user.favourite_games.append(game)
    db.commit()

    await FastAPICache.clear()
    return {"message": "Game successfully added to favourites."}
