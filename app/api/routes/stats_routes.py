from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from ...core.database import SessionDep
from ...core import oauth2
from ... import schemas
from ... import models
from typing import Annotated
from ...schemas.base_response import BaseResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/{short_url}/dashboard")
async def get_url_dashboard(
    short_url: str, 
    db: SessionDep, 
    current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)],
    days: int = 90
):
    url = db.query(models.Url).filter(models.Url.short_url == short_url).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    clicks_query = db.query(models.Click).filter(
        models.Click.short_url == short_url,
        models.Click.clicked_at >= cutoff_date
    )
    
    daily_breakdown = []
    for i in range(days, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        count = clicks_query.filter(
            func.date(models.Click.clicked_at) == day
        ).count()
        
        daily_breakdown.append({
            "date": day.isoformat(),
            "clicks": count
        })
    
    country_stats = db.query(
        models.Click.country,
        func.count(models.Click.id).label('clicks')
    ).filter(
        models.Click.short_url == short_url
    ).group_by(
        models.Click.country
    ).order_by(
        func.count(models.Click.id).desc()
    ).limit(5).all()
    
    top_countries = [
        {"country": country or "Unknown", "clicks": clicks}
        for country, clicks in country_stats
    ]
    
    referer_stats = db.query(
        models.Click.referer,
        func.count(models.Click.id).label('clicks')
    ).filter(
        models.Click.short_url == short_url
    ).group_by(
        models.Click.referer
    ).order_by(
        func.count(models.Click.id).desc()
    ).limit(5).all()
    
    top_referers = [
        {"referer": referer or "Direct", "clicks": clicks}
        for referer, clicks in referer_stats
    ]
    
    return BaseResponse(
        status=200,
        message="Dashboard statistics retrieved successfully",
        timestamp=datetime.now(),
        data={
            "short_url": url.short_url,
            "full_url": url.full_url,
            "total_clicks": url.click,
            "daily_breakdown": daily_breakdown,
        }
    )
