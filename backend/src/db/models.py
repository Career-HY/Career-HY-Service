import uuid
from sqlalchemy import Column, String, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "member"   

    id = Column(
        String(36),
        primary_key=True,
        nullable=False,
        server_default=text("UUID()")
    )

    email       = Column(String(255), unique=True, nullable=False)
    pwd         = Column(String(255), nullable=False)

    signup_date = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
