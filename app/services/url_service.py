from typing import Optional
from .. import schemas
from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from ..exceptions.url_exception import UrlNotFoundError, DuplicateShortUrlError
from ..exceptions.user_exception import UserNotFoundError
from ..core.redis import redis_client


def shorten_url(request: schemas.UrlCreate, db: Session, user: Optional[schemas.UserBase] = None):
    if user:
        user_id = user.id
    else:
        user_id = None 
    
    if request.short_url:
        existing = db.scalar(
            select(models.Url).where(
                models.Url.short_url == request.short_url
            )
        )
        if existing:
            raise DuplicateShortUrlError

    new_url = models.Url(full_url=request.full_url, short_url=request.short_url, user_id=user_id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url


def get_all_urls(db: Session):
    statement = select(models.Url)

    urls = db.scalars(statement).all()

    return urls

def get_user_urls(user_id: int, db: Session):
    urls = db.query(models.Url).filter(models.Url.user_id == user_id).all()

    return urls


async def get_url(short_url: str, db: Session):
    cached = await redis_client.get_cached_url(short_url)

    if cached:
        db.execute(
            update(models.Url)
            .where(models.Url.short_url == short_url)
            .values(click=models.Url.click + 1)
        )
        db.commit()


        return cached
    
    statement = select(models.Url).where(models.Url.short_url == short_url)

    url = db.scalar(statement)

    if url is None:
        raise UrlNotFoundError()

    url.click += 1
    db.commit()


    await redis_client.cache_url(short_url, url.full_url)

    # langsung return full url
    return url.full_url



async def delete_url(id: int, db: Session):
    url = db.get(models.Url, id)

    if url is None:
        raise UrlNotFoundError()
    
    short_url = url.short_url
    
    db.delete(url)
    db.commit()
    
    await redis_client.delete(f"url:{short_url}")
    
    return {
        "message": "Deleted successfully",
        "deleted_url": short_url,
        "id": id
    }

