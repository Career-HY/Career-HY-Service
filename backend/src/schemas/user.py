from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    pwd: str

class UserRead(BaseModel):
    id: str
    email: str
    signup_date: Optional[datetime]
    class Config:
        orm_mode = True
