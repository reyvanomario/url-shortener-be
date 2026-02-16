from .. import schemas
from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..exceptions.user_exception import DuplicateUsernameError, UserNotFoundError
from ..utils import password_utils


def create_user(request: schemas.UserCreate, db: Session):
    if request.username:
        existing = db.scalar(
            select(models.User).where(
                models.User.username == request.username
            )
        )
        if existing:
            raise DuplicateUsernameError()
        
    
    hashed_password = password_utils.hash_password(request.password)


    new_user = models.User(
        username= request.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user(id: int, db: Session):
    user = db.get(models.User, id)

    if user is None:
        raise UserNotFoundError()
    
    return user



