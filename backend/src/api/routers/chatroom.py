from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas.chatroom import (
    ChatroomCreate,
    ChatroomRead,
    ChatroomUpdate
)
from crud.chatroom import (
    create_chatroom,
    get_chatroom,
    get_chatrooms_by_member,
    update_chatroom,
    delete_chatroom
)
from db.session import get_db
from util.deps import get_current_user
from util.logging import log_api_call

router = APIRouter(prefix="/chatrooms", tags=["chatrooms"])


@router.post("", response_model=ChatroomRead, status_code=201)
@log_api_call
def create_new_chatroom(
    data: ChatroomCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 채팅방을 생성합니다.
    
    - **title**: 채팅방 제목 (선택적)
    """
    return create_chatroom(db, current_user.id, data)


@router.get("", response_model=List[ChatroomRead])
@log_api_call
def get_my_chatrooms(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 모든 채팅방 목록을 조회합니다.
    
    - 최근 업데이트 순으로 정렬됩니다.
    """
    return get_chatrooms_by_member(db, current_user.id)


@router.get("/{chatroom_id}", response_model=ChatroomRead)
@log_api_call
def get_chatroom_detail(
    chatroom_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 채팅방의 정보를 조회합니다.
    """
    chatroom = get_chatroom(db, chatroom_id, current_user.id)
    if not chatroom:
        raise HTTPException(
            status_code=404,
            detail="채팅방을 찾을 수 없습니다."
        )
    return chatroom


@router.patch("/{chatroom_id}", response_model=ChatroomRead)
@log_api_call
def update_chatroom_info(
    chatroom_id: int,
    data: ChatroomUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅방 정보를 수정합니다.
    
    - **title**: 채팅방 제목
    """
    chatroom = update_chatroom(db, chatroom_id, current_user.id, data)
    if not chatroom:
        raise HTTPException(
            status_code=404,
            detail="채팅방을 찾을 수 없습니다."
        )
    return chatroom


@router.delete("/{chatroom_id}")
@log_api_call
def delete_chatroom_by_id(
    chatroom_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅방을 삭제합니다. (논리적 삭제)
    """
    success = delete_chatroom(db, chatroom_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="채팅방을 찾을 수 없습니다."
        )
    return {"message": "채팅방이 삭제되었습니다."} 