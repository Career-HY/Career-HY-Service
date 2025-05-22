from pydantic import BaseModel

class UserCreate(BaseModel):
    emaiL: str
    password: str

class UserRead(BaseModel):
    id: int
    email: str
    class Config:
        orm_mode = True
