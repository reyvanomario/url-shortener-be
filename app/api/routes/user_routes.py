from fastapi import APIRouter, HTTPException, status, Depends
from ...core.database import SessionDep
from ... import schemas
from ...services import user_service
from ...exceptions.user_exception import DuplicateUsernameError, UserNotFoundError
from ...core import oauth2
from typing import Annotated
from ...schemas.base_response import BaseResponse
from datetime import datetime

router = APIRouter(prefix="/user", tags=["Users"])


@router.post('', status_code=status.HTTP_201_CREATED, response_model=BaseResponse[schemas.UserResponse])
def create_user(request: schemas.UserCreate, db: SessionDep):
    try:
        user = user_service.create_user(request, db)

        return BaseResponse(
            status=201,
            message="User registered successfully",
            timestamp=datetime.now(),
            data=user
        )
    
    except DuplicateUsernameError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=BaseResponse[schemas.UserResponse])
def get_user(id: int, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]): # contoh route yg diprotect
    try:
        user = user_service.get_user(id, db)

        return BaseResponse(
            status=200,
            message="User data retrieved successfully",
            timestamp=datetime.now(),
            data=user
        )
      
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    

# @router.get("/me", response_model=schemas.UserResponse)
# async def get_current_user_info(
#     current_user: Annotated[models.User, Depends(oauth2.get_current_user)]
# ):
#     return current_user