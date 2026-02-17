from fastapi import APIRouter, HTTPException, status, Request
from ...core.database import SessionDep
from ...services import url_service, click_service
import asyncio
from fastapi.responses import RedirectResponse
from ...exceptions.url_exception import UrlNotFoundError


router = APIRouter(tags=["Redirect URL"])


@router.get("/{short_url}")
async def redirect_url(short_url: str, db: SessionDep, request: Request):
    try:
        full_url = await url_service.get_url(short_url, db)  

        asyncio.create_task(
            click_service.track_click(short_url, db, request)  
        ) 

        return RedirectResponse(full_url)
    
    except UrlNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")