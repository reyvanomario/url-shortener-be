from pydantic import BaseModel
from .User import UserResponse

class UrlBase(BaseModel):
    full_url: str
    short_url: str


class UrlCreate(UrlBase):
    user_id: int
    pass


class UrlUpdate(BaseModel):
    full_url: str | None = None
    short_url: str | None = None


class UrlResponse(UrlBase):
    creator: UserResponse
    model_config = {
        "from_attributes": True
    }