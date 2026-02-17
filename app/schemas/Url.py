from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional

import re
from pydantic import HttpUrl

class UrlBase(BaseModel):
    full_url: str = Field(..., description="URL lengkap yang akan dipendekkan")
    short_url: Optional[str] = Field(None, min_length=3, max_length=50, description="Kode custom untuk short URL")
    
    @validator('full_url')
    def validate_full_url(cls, v):
        try:

            HttpUrl(v)
        except:
            raise ValueError('Format URL tidak valid. Pastikan URL dimulai dengan http:// atau https://')
        
      
        if len(v) > 2000:
            raise ValueError('URL terlalu panjang (maksimal 2000 karakter)')
        
        return v
    
    @validator('short_url')
    def validate_short_url(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Short URL hanya boleh berisi huruf, angka, tanda hubung (-) dan underscore (_)')
        
        return v


class UrlCreate(UrlBase):
    pass


class UrlResponse(UrlBase):
    id: int
    click: int = 0

    user_id: Optional[int] = None
    
    model_config = {
        "from_attributes": True
    }