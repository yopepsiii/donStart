import hashlib
from typing import Optional, Callable

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from starlette.requests import Request
from starlette.responses import Response

from .config import settings
from .routers import users, games, admin, auth, roles, votes

from fastapi.middleware.cors import CORSMiddleware

import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool
from fastapi_cache import FastAPICache
from fastapi_cache.coder import PickleCoder
from fastapi_cache.backends.redis import RedisBackend

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


@app.on_event("startup")
async def startup():
    pool = ConnectionPool.from_url(url="redis://redis")
    r = aioredis.Redis(connection_pool=pool)
    FastAPICache.init(RedisBackend(r), prefix="donstart-cache", key_builder=api_key_builder)


def api_key_builder(
        func: Callable,
        namespace: Optional[str] = "",
        request: Optional[Request] = None,
        response: Optional[Response] = None,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
) -> str:
    # SOLUTION: https://github.com/long2ice/fastapi-cache/issues/26
    print("kwargs.items():", kwargs.items())
    arguments = {}
    for key, value in kwargs.items():
        if key != 'db':
            arguments[key] = value
    # print("request:", request, "request.base_url:", request.base_url, "request.url:", request.url)
    arguments['url'] = request.url
    # print("arguments:", arguments)

    prefix = f"{FastAPICache.get_prefix()}:{namespace}:"
    cache_key = (
            prefix
            + hashlib.md5(  # nosec:B303
        f"{func.__module__}:{func.__name__}:{args}:{arguments}".encode()
    ).hexdigest()
    )
    return cache_key
