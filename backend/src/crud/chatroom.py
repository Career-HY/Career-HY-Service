from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from db.models import Chatroom, ChatMessage
from schemas.chatroom import ChatroomCreate, ChatroomUpdate, ChatMessageCreate
from util.logging import log_db_operation


@log_db_operation("SELECT")
def get_chatroom(db: Session, chatroom_id: int, member_id: str) -> Optional[Chatroom]:
    """
    사용자의 특정 채팅방을 조회합니다. (삭제되지 않은 채팅방만)
    """
    return db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.member_id == member_id,
        Chatroom.is_deleted == False
    ).first()


@log_db_operation("SELECT")
def get_chatrooms_by_member(db: Session, member_id: str) -> List[Chatroom]:
    """
    사용자의 모든 채팅방을 조회합니다. (삭제되지 않은 채팅방만)
    """
    return db.query(Chatroom).filter(
        Chatroom.member_id == member_id,
        Chatroom.is_deleted == False
    ).order_by(Chatroom.created_at.desc()).all()


@log_db_operation("INSERT")
def create_chatroom(db: Session, member_id: str, data: ChatroomCreate) -> Chatroom:
    """
    새로운 채팅방을 생성합니다.
    """
    chatroom = Chatroom(
        member_id=member_id,
        title=data.title,
        is_deleted=False
    )
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)
    return chatroom


@log_db_operation("INSERT")
def create_chat_message(db: Session, chatroom_id: int, data: ChatMessageCreate) -> ChatMessage:
    """
    채팅방에 새로운 메시지를 추가합니다.
    """
    message = ChatMessage(
        chat_room_id=chatroom_id,
        sender=data.sender,
        content=data.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@log_db_operation("UPDATE")
def update_chatroom(db: Session, chatroom_id: int, member_id: str, data: ChatroomUpdate) -> Optional[Chatroom]:
    """
    채팅방 정보를 수정합니다.
    """
    chatroom = get_chatroom(db, chatroom_id, member_id)
    if not chatroom:
        return None
    
    if data.title is not None:
        chatroom.title = data.title
    
    db.commit()
    db.refresh(chatroom)
    return chatroom


@log_db_operation("UPDATE")
def delete_chatroom(db: Session, chatroom_id: int, member_id: str) -> bool:
    """
    채팅방을 논리적으로 삭제합니다. (is_deleted = True)
    """
    chatroom = get_chatroom(db, chatroom_id, member_id)
    if not chatroom:
        return False
    
    chatroom.is_deleted = True
    db.commit()
    return True 