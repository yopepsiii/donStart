from authlib.oauth2 import OAuth2Error
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from .. import models, utils, oauth2
from ..database import get_db
from ..oauth2 import oauth_client, create_access_token
from ..schemas import auth_schemas, user_schemas

from ..utils import hash, generate_secure_password

router = APIRouter(tags=["Authentification"])


@router.post("/login", response_model=auth_schemas.Token)
async def login(
        user_credentials: user_schemas.UserLogin,
        db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()  # type: ignore
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = await oauth2.create_access_token(data={"user_guid": str(user.guid), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for("login_google_callback")
    return await oauth_client.google.authorize_redirect(request, redirect_uri)


@router.get("/login/google/callback")
async def login_google_callback(request: Request, db: Session = Depends(get_db)):
    userinfo = await get_userinfo(request)

    user = db.query(models.User).filter(models.User.email == userinfo['email']).first()  # type: ignore
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )

    access_token = await create_access_token(
        data={"user_guid": str(user.guid),
              "email": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/register/google")
async def register_google(request: Request):
    redirect_uri = request.url_for("register_google_callback")
    return await oauth_client.google.authorize_redirect(request, redirect_uri)


@router.get("/register/google/callback")
async def register_google_callback(request: Request, db: Session = Depends(get_db)):
    userinfo = await get_userinfo(request)

    existing_user = db.query(models.User).filter(models.User.email == userinfo["email"]).first()

    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    new_user_username = userinfo["name"] if not None else userinfo["email"][:userinfo["email"].find("@")]

    new_user = models.User(email=userinfo["email"], username=new_user_username,
                           profile_picture=userinfo["picture"], password=hash(generate_secure_password()))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    await FastAPICache.clear()

    access_token = await create_access_token(
        data={"user_guid": str(new_user.guid),
              "email": new_user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_userinfo(request: Request):
    try:
        token = await oauth_client.google.authorize_access_token(request)
    except OAuth2Error as e:
        raise e.error

    return token['userinfo']
