from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..exceptions.url_exception import UrlNotFoundError
from datetime import datetime, timedelta
from ..core.redis import redis_client


async def get_url_stats(short_url: str, db: Session):
    statement = select(models.Url).where(models.Url.short_url == short_url)

    url = db.scalar(statement)

    if url is None:
        raise UrlNotFoundError()
    
    total_clicks = db.query(models.Click).filter(models.Click.short_url == short_url).count()

    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_clicks = db.query(
        func.date(models.Click.clicked_at).label('date'),
        func.count().label('count')
    ).filter(
        models.Click.short_url == short_url,
        models.Click.clicked_at >= seven_days_ago
    ).group_by(func.date(models.Click.clicked_at)).all()
    
    # Top countries
    top_countries = db.query(
        models.Click.country,
        func.count().label('count')
    ).filter(
        models.Click.short_url == short_url,
        models.Click.country != ''
    ).group_by(models.Click.country).order_by(func.count().desc()).limit(5).all()
    
    # Top referers
    top_referers = db.query(
       models. Click.referer,
        func.count().label('count')
    ).filter(
        models.Click.short_url == short_url,
        models.Click.referer != ''
    ).group_by(models.Click.referer).order_by(func.count().desc()).limit(5).all()
    
    # Real-time clicks dari Redis
    realtime_clicks = await redis_client.get(f"clicks:{short_url}")
    
    return {
        "short_url": short_url,
        "full_url": url.full_url,
        "total_clicks": total_clicks,
        "realtime_clicks_today": int(realtime_clicks or 0),
        "daily_breakdown": [
            {"date": str(row.date), "clicks": row.count}
            for row in daily_clicks
        ],
        "top_countries": [
            {"country": row.country, "clicks": row.count}
            for row in top_countries
        ],
        "top_referers": [
            {"referer": row.referer, "clicks": row.count}
            for row in top_referers
        ]
    }