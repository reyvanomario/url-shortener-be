from fastapi import FastAPI
from .core import database
from contextlib import asynccontextmanager
from .core.redis import redis_client
from .api.routes import url_routes, stats_routes, user_routes, auth_routes
from fastapi.middleware.cors import CORSMiddleware


def create_db_and_tables():
    database.init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    create_db_and_tables()
    await redis_client.connect()
    yield
    print("App stopped")
    await redis_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(url_routes.router)
app.include_router(stats_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)

