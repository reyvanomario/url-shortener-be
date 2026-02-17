from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class BaseResponse(GenericModel, Generic[T]):
    status: int
    message: str
    timestamp: datetime
    data: T
