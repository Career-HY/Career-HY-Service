from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .chat import RecommendedJob


# ——— 채팅방 스키마 ———
class ChatroomCreate(BaseModel):
    """채팅방 생성 요청 스키마"""
    title: Optional[str] = None  # 채팅방 제목 (선택적)


class ChatroomRead(BaseModel):
    """채팅방 조회 응답 스키마"""
    id: int
    member_id: str
    title: Optional[str] = None
    is_deleted: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatroomUpdate(BaseModel):
    """채팅방 수정 요청 스키마"""
    title: Optional[str] = None


# ——— 채팅 메시지 스키마 ———
class ChatMessageCreate(BaseModel):
    """채팅 메시지 생성 요청 스키마"""
    content: str
    sender: str = "user"  # "user" 또는 "llm"
    recommended_jobs: Optional[List[RecommendedJob]] = None


class ChatMessageRead(BaseModel):
    """채팅 메시지 조회 응답 스키마"""
    id: int
    chat_room_id: int
    sender: str
    content: Optional[str] = None
    recommended_jobs: Optional[List[RecommendedJob]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ——— 상세 채팅방 스키마 (메시지 포함) ———
class ChatroomDetail(ChatroomRead):
    """채팅방 상세 조회 응답 스키마 (메시지 포함)"""
    messages: List[ChatMessageRead] = [] 