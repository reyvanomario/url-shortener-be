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
    
    plain_password = request.password.get_secret_value()
    hashed_password = password_utils.hash_password(plain_password)


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


def get_current_user(token_data: schemas.TokenData, db: Session):
    user = get_user_by_username(token_data.username, db)
    return user


def get_user_by_username(username: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        raise UserNotFoundError()
    
    return user



