from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from backend.app import models
from backend.app.database import get_db
from backend.app.oauth2 import get_current_user
from backend.app.schemas import vote_schemas

router = APIRouter(prefix="/votes", tags=["Votes (Likes/Dislikes)"])


# WIP
@router.post('')
async def create_vote(vote: vote_schemas.VoteCreate, current_user: models.User = Depends(get_current_user),
                      db: Session = Depends(get_db)):

    game = db.query(models.Game).filter(models.Game.guid == vote.game_guid).first()
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game {vote.game_guid} doesn't exist")

    vote_query = db.query(models.Vote).filter(models.Vote.user_guid == current_user.guid,
                                              models.Vote.game_guid == vote.game_guid)
    found_vote = vote_query.first()

    if found_vote is None:
        new_vote = models.Vote(user_guid=current_user.guid, **vote.dict())
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)

        return {"message": "Game liked" if new_vote.type == 1 else "Game disliked"}
    else:
        if vote.type == found_vote.type:
            db.delete(found_vote)
            db.commit()

            return {"message": "Vote has been deleted"}

        vote_query.update({"type": vote.type}, synchronize_session=False)
        db.commit()
        db.refresh(found_vote)

        return {"message": "Game liked" if found_vote.type == 1 else "Game disliked"}

