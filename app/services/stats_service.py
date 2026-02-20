from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from ..exceptions.url_exception import UrlNotFoundError

async def get_url_stats(short_url: str, db: Session):
    url = db.query(models.Url).filter(models.Url.short_url == short_url).first()
    
    if not url:
        raise UrlNotFoundError(f"URL with short url '{short_url}' not found")
    
    clicks_query = db.query(models.Click).filter(
        models.Click.short_url == short_url
    ).order_by(models.Click.clicked_at.desc()).limit(10)

    recent_clicks = []
    for click in clicks_query:
        recent_clicks.append({
            "ip": click.ip_address,
            "country": click.country,
            "device": click.device_type,
            "browser": click.browser,
            "os": click.os,
            "timestamp": click.clicked_at.isoformat() if click.clicked_at else None
        })
    
    device_stats = {
        "desktop": 0,
        "mobile": 0,
        "tablet": 0,
        "bot": 0,
        "other": 0
    }
    
    browser_stats = {}
    os_stats = {}
    
    daily_breakdown = []
    today = datetime.now().date()
    
    for i in range(7):
        day = today - timedelta(days=i)
        count = db.query(models.Click).filter(
            and_(
                models.Click.short_url == short_url,
                func.date(models.Click.clicked_at) == day
            )
        ).count()
        daily_breakdown.append({
            "date": day.isoformat(),
            "clicks": count
        })

    total_clicks = db.query(models.Click).filter(
        models.Click.short_url == short_url
    ).count()
    
    return {
        "id": url.id,
        "short_url": url.short_url,
        "full_url": url.full_url,
        "total_clicks": total_clicks,
        "device_stats": device_stats,
        "browser_stats": browser_stats,
        "os_stats": os_stats,
        "daily_breakdown": daily_breakdown,
        "recent_clicks": recent_clicks
    }