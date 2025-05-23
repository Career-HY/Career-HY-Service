from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    pwd: str

class UserLogin(BaseModel):
    email: str
    pwd: str

class UserRead(BaseModel):
    id: str
    email: str
    signup_date: Optional[datetime]
    class Config:
        orm_mode = True
