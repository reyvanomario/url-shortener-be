from fastapi import FastAPI
from .core import database
from contextlib import asynccontextmanager
from .core.redis import redis_client
from .api.routes import url_routes, stats_routes, user_routes, auth_routes, redirect_routes
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings


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


app = FastAPI(lifespan=lifespan,
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    settings.DOMAIN, 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(url_routes.router, prefix="/api")
app.include_router(stats_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")
app.include_router(redirect_routes.router)

@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} API",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None
    }



