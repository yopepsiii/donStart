from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from backend.app import models
from backend.app.database import get_db
from backend.app.oauth2 import get_current_user
from backend.app.schemas import vote_schemas

router = APIRouter(prefix="/votes", tags=["Votes (Likes/Dislikes)"])

# WIP
@router.post('', status_code=status.HTTP_201_CREATED)
async def create_vote(vote_data: vote_schemas.VoteCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    pass