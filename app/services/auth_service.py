from .. import schemas
from .. import models
from sqlalchemy.orm import Session
from ..exceptions.user_exception import InvalidCredentialError
from ..utils import password_utils
from datetime import timedelta
from ..utils import jwt_utils

def login(db: Session, request):
    user = db.query(models.User).filter(models.User.username == request.username).first()

    if not user:
        raise InvalidCredentialError()

    if not password_utils.verify_password(request.password, user.password):
        raise InvalidCredentialError()


    # generate jwt and return
    access_token_expires = timedelta(minutes=jwt_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_utils.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


