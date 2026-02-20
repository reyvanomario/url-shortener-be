from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from ...core.database import SessionDep
from ...core import oauth2
from ... import schemas
from typing import Annotated
from ...schemas.base_response import BaseResponse
from ...services import stats_service
from ...exceptions.url_exception import UrlNotFoundError

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/{short_url}/dashboard")
async def get_url_dashboard(
    short_url: str, 
    db: SessionDep, 
    current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)],
):
    try:
        stats = await stats_service.get_url_stats(short_url, db)
        
        return BaseResponse(
            status=200,
            message="Dashboard statistics retrieved successfully",
            timestamp=datetime.now(),
            data=stats
        )
    except UrlNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")
