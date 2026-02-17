from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from ... import schemas
from ...core.database import SessionDep
from ...services import auth_service
from ...exceptions.user_exception import InvalidCredentialError
from fastapi.security import OAuth2PasswordRequestForm
from ...schemas.base_response import BaseResponse
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", status_code=status.HTTP_200_OK, response_model=BaseResponse[schemas.LoginJwtResponse])
def login(db: SessionDep, request: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        token = auth_service.login(db, request)

        return BaseResponse(
            status=200,
            message="Login successfull",
            timestamp=datetime.now(),
            data=token
        )

    except InvalidCredentialError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
    
    
