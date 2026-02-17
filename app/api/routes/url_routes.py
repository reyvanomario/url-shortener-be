from fastapi import APIRouter, HTTPException, status, Request, Depends
from ...core.database import SessionDep
from ... import schemas
from ...services import url_service
from ...exceptions.url_exception import UrlNotFoundError, DuplicateShortUrlError
from ...exceptions.user_exception import UserNotFoundError
from typing import List, Annotated, Optional
from ...utils.ip_utils import get_user_ip, get_real_client_ip
from ...core import oauth2
from ...schemas.base_response import BaseResponse
from datetime import datetime

router = APIRouter(tags=["Urls"])

@router.post("/shorten", status_code=status.HTTP_201_CREATED, response_model=BaseResponse[schemas.UrlResponse])
def shorten_url(request: schemas.UrlCreate, db: SessionDep, current_user: Annotated[Optional[schemas.UserBase], Depends(oauth2.get_current_user_optional)]):
    try:
        url = url_service.shorten_url(request, db, current_user)

        return BaseResponse(
            status=201,
            message="Successfully shortened url",
            timestamp=datetime.now(),
            data=url
        )
    
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found with id " + str(request.user_id))
    
    except DuplicateShortUrlError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Short url already taken")


@router.get("/url/all", response_model=BaseResponse[List[schemas.UrlResponse]])
def get_all_urls(db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    urls = url_service.get_all_urls(db)

    return BaseResponse(
        status=200,
        message="Data url berhasil diambil",
        timestamp=datetime.now(),
        data=urls
    )


@router.get("/my-urls", response_model=BaseResponse[List[schemas.UrlResponse]])
async def get_my_urls(
    current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)],
    db: SessionDep
):
    urls = url_service.get_user_urls(current_user.id, db)
    
    return BaseResponse(
        status=200,
        message="Data url user berhasil diambil",
        timestamp=datetime.now(),
        data=urls
    )

    


@router.delete("/{id}")
def delete_url(id: int, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    try:
        deleted_count = url_service.delete_url(id, db)

        return BaseResponse(
            status=200,
            message="Data url berhasil diambil",
            timestamp=datetime.now(),
            data=deleted_count
        )

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