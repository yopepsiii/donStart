from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .routers import users, games, admin, auth, roles, votes

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(middleware_class=SessionMiddleware, secret_key=settings.google_client_secret)

origins = ['http://localhost:8000',
           'http://frontend:4700']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Какие HTTP-методы разрешены для обработки
    allow_headers=["*"],  # Какие headers разрешены для обработки
)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(roles.router)
app.include_router(votes.router)


@app.get('/')
async def index():
    return {'message': 'welcome to DonStart\'s API'}
