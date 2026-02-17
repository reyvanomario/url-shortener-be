from pydantic import BaseModel, Field, field_validator, SecretStr
import re
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username harus 3-50 karakter")
    
    @field_validator('username')
    def validate_username(cls, v):
        # Username hanya boleh huruf, angka, underscore, dan titik
        if not re.match(r'^[a-zA-Z0-9_.]+$', v):
            raise ValueError('Username hanya boleh berisi huruf, angka, underscore (_) dan titik (.)')
        
        # Tidak boleh diawali dengan angka
        if v[0].isdigit():
            raise ValueError('Username tidak boleh diawali dengan angka')
        
        return v


class UserCreate(UserBase):
    password: SecretStr = Field(..., min_length=8, max_length=100, description="Password minimal 8 karakter")
    
    @field_validator('password')
    def validate_password(cls, v):
        password_str = v.get_secret_value()

        if not re.search(r'[a-z]', password_str):
            raise ValueError('Password harus mengandung huruf kecil')
        
        if not re.search(r'\d', password_str):
            raise ValueError('Password harus mengandung angka')
        
        return v



class UserResponse(UserBase):
    id: int
    created_at: datetime | None = None
    is_active: bool = True
    
    model_config = {
        "from_attributes": True
    }