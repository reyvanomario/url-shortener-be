from pydantic import BaseModel

class LoginJwtResponse(BaseModel):
    id: int
    username: str
    token: str
    tokenType: str


class TokenData(BaseModel):
    username: str | None = None