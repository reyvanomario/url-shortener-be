from fastapi import Depends, HTTPException, status
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..utils import jwt_utils
from ..core.database import SessionDep
from .. import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user_optional(token: Annotated[Optional[str], Depends(oauth2_scheme)],db: SessionDep) -> Optional[models.User]:
    if token is None:
        return None
    
    # Tidak pakai exception karena bisa shorten url walaupun tidak login
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    
    try:
        payload = jwt_utils.verify_token(token)
        username = payload.get("sub")
        
        if username is None:
            return None
        
        user = db.query(models.User).filter(models.User.username == username).first()
        return user
    except:
        return None
    

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = jwt_utils.verify_token(token, credentials_exception)
    username = payload.get("sub")
    
    if username is None:
        raise credentials_exception
    
    
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    return user
     