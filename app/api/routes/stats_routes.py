from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from ...core.database import SessionDep
from ...services import stats_service
from ...core import oauth2
from ... import schemas
from typing import Annotated

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/{short_url}")
async def get_url_stats(short_url: str, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]):
    stats = await stats_service.get_url_stats(short_url, db)

    return stats