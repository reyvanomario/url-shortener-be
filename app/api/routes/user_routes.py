from fastapi import APIRouter, HTTPException, status, Depends
from ...core.database import SessionDep
from ... import schemas
from ...services import user_service
from ...exceptions.user_exception import DuplicateUsernameError, UserNotFoundError
from ...core import oauth2
from typing import Annotated

router = APIRouter(prefix="/user", tags=["Users"])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(request: schemas.UserCreate, db: SessionDep):
    try:
        user = user_service.create_user(request, db)

        return user
    except DuplicateUsernameError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user(id: int, db: SessionDep, current_user: Annotated[schemas.UserBase, Depends(oauth2.get_current_user)]): # contoh rout yg diprotect
    try:
        user = user_service.get_user(id, db)

        return user
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")