from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from ..exceptions.url_exception import UrlNotFoundError

async def get_url_stats(short_url: str, db: Session):
    url = db.query(models.Url).filter(models.Url.short_url == short_url).first()
    
    if not url:
        raise UrlNotFoundError(f"URL with short code '{short_url}' not found")
    
    clicks = db.query(models.Click).filter(models.Click.short_url == short_url).all()
    
    device_stats = {
        "desktop": 0,
        "mobile": 0,
        "tablet": 0,
        "bot": 0,
        "other": 0
    }
    
    browser_stats = {}
    
    os_stats = {}
    
    daily_clicks = []
    today = datetime.now().date()
    
    for i in range(7):
        day = today - timedelta(days=i)
        count = db.query(models.Click).filter(
            and_(
                models.Click.short_url == short_url,
                func.date(models.Click.clicked_at) == day
            )
        ).count()
        daily_clicks.append({
            "date": day.isoformat(),
            "clicks": count
        })

    for click in clicks:
        if click.device_type in device_stats:
            device_stats[click.device_type] += 1
        else:
            device_stats["other"] += 1
        
        browser = click.browser or "Unknown"
        browser_stats[browser] = browser_stats.get(browser, 0) + 1
        
        os = click.os or "Unknown"
        os_stats[os] = os_stats.get(os, 0) + 1
    
    return {
        "id": url.id,
        "short_url": url.short_url,
        "full_url": url.full_url,
        "created_at": url.created_at,
        "total_clicks": url.click,
        "device_stats": device_stats,
        "browser_stats": browser_stats,
        "os_stats": os_stats,
        "daily_clicks": daily_clicks,
        "recent_clicks": [
            {
                "ip": click.ip_address,
                "country": click.country,
                "device": click.device_type,
                "browser": click.browser,
                "os": click.os,
                "timestamp": click.clicked_at
            }
            for click in clicks[-10:]  # 10 clicks terakhir
        ]
    }