from .. import schemas
from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..exceptions.url_exception import UrlNotFoundError, DuplicateShortUrlError
from ..exceptions.user_exception import UserNotFoundError
from ..core.redis import redis_client


def shorten_url(request: schemas.UrlCreate, db: Session):
    user = db.get(models.User, request.user_id)

    if user is None:
        raise UserNotFoundError()
    

    if request.short_url:
        existing = db.scalar(
            select(models.Url).where(
                models.Url.short_url == request.short_url
            )
        )
        if existing:
            raise DuplicateShortUrlError

    new_url = models.Url(full_url=request.full_url, short_url=request.short_url, user_id=request.user_id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url


def get_all_urls(db: Session):
    statement = select(models.Url)

    urls = db.scalars(statement).all()

    return urls


async def get_url(short_url: str, db: Session):
    cached = await redis_client.get_cached_url(short_url)
    if cached:
        print("return cache " + cached)
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


async def update_url(id: int, request: schemas.UrlUpdate, db: Session):
    url_db = db.get(models.Url, id)

    if url_db is None:
        raise UrlNotFoundError()
    
    old_short_url = url_db.short_url

    update_data = request.model_dump(exclude_unset=True)

    # Validasi short url baru tidak boleh sama
    if 'short_url' in update_data:
        existing = db.scalar(
            select(models.Url).where(
                models.Url.short_url == update_data['short_url'],
                models.Url.id != id 
            )
        )
        if existing:
            raise DuplicateShortUrlError()

    for field, value in update_data.items():
        # (url, key yg diupdate, value)
        setattr(url_db, field, value)

    db.commit()
    db.refresh(url_db)

    await redis_client.invalidate_url(old_short_url)
    if 'short_url' in update_data:
        await redis_client.invalidate_url(url_db.short_url)

    return url_db


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

