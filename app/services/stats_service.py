from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from ..exceptions.url_exception import UrlNotFoundError
from ..exceptions.stats_exception import ForbiddenAccessException
from collections import defaultdict


async def get_url_stats(short_url: str, db: Session, current_user):
    url = db.query(models.Url).filter(models.Url.short_url == short_url).first()
    
    if not url:
        raise UrlNotFoundError(f"URL with short url '{short_url}' not found")
    
    if url.user_id != current_user.id:
        raise ForbiddenAccessException()
    
    all_clicks = db.query(models.Click).filter(
        models.Click.short_url == short_url
    ).order_by(models.Click.clicked_at.desc()).all()

    total_clicks = len(all_clicks)

    recent_clicks = []
    for click in all_clicks[:10]:
        recent_clicks.append({
            "ip": click.ip_address,
            "country": click.country,
            "device": click.device_type,
            "browser": click.browser,
            "os": click.os,
            "timestamp": click.clicked_at.isoformat() if click.clicked_at else None
        })

    clicks_by_date = defaultdict(int)
    earliest_date = datetime.now().date()

    for click in all_clicks:
        if click.clicked_at:
            date = click.clicked_at.date()
            clicks_by_date[date] += 1
            if date < earliest_date:
                earliest_date = date
    
    daily_clicks = []
    current_date = earliest_date
    today = datetime.now().date()
    
    while current_date <= today:
        daily_clicks.append({
            "date": current_date.isoformat(),
            "clicks": clicks_by_date.get(current_date, 0)
        })
        current_date += timedelta(days=1)
    
    
    device_stats = {
        "desktop": 0,
        "mobile": 0,
        "tablet": 0,
        "bot": 0,
        "other": 0
    }
    
    browser_stats = {}
    os_stats = {}
    
    for click in all_clicks:
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
        "total_clicks": total_clicks,
        "device_stats": device_stats,
        "browser_stats": browser_stats,
        "os_stats": os_stats,
        "daily_clicks": daily_clicks,
        "recent_clicks": recent_clicks
    }