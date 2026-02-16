from fastapi import APIRouter, HTTPException, status, Request, Depends
from ...core.database import SessionDep
from ... import schemas
from fastapi.responses import RedirectResponse
from ...services import url_service, click_service
from ...exceptions.url_exception import UrlNotFoundError, DuplicateShortUrlError
from ...exceptions.user_exception import UserNotFoundError
from typing import List, Annotated
import asyncio
from ...utils.ip_utils import get_user_ip, get_real_client_ip
from ...core import oauth2

router = APIRouter(tags=["Urls"])

@router.post("/shorten", status_code=status.HTTP_201_CREATED, response_model=schemas.UrlResponse)
def shorten_url(request: schemas.UrlCreate, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    try:
        return url_service.shorten_url(request, db)
    
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found with id " + str(request.user_id))
    
    except DuplicateShortUrlError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Short url already taken")


@router.get("/url/all", response_model=List[schemas.UrlResponse])
def get_all_urls(db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    urls = url_service.get_all_urls(db)

    return urls


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
    

@router.put("/{id}")
async def update_url(id: int, request: schemas.UrlUpdate, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    try:
        updated_count = await url_service.update_url(id, request, db)

        return updated_count
    
    except DuplicateShortUrlError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Short url already taken")

    except UrlNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")


@router.delete("/{id}")
def delete_url(id: int, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    try:
        deleted_count = url_service.delete_url(id, db)

        return deleted_count

    except UrlNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
    

@router.get("/debug/ip")
async def debug_ip(request: Request):
    return {
        "client_host": request.client.host if request.client else None,
        "scope_client": request.scope.get("client"),
        "headers": {
            "x-real-ip": request.headers.get("x-real-ip"),
            "x-forwarded-for": request.headers.get("x-forwarded-for"),
        },
        "user_ip": get_user_ip(request),
        "connection_ip": get_real_client_ip(request)
    }


@router.get("/debug/ip/detailed")
async def debug_ip_detailed(request: Request):
    return {
        "client_host": request.client.host,
        "client_port": request.client.port,
        "headers": dict(request.headers),
        "method": request.method,
        "url": str(request.url),
        "server": {
            "host": request.url.hostname,
            "port": request.url.port,
            "scheme": request.url.scheme
        }
    }