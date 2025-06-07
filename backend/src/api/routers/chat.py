from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from schemas.chat import ChatRequest, ChatResponse
from schemas.chatroom import ChatMessageCreate
from crud.profile import get_profile
from crud.chatroom import get_chatroom, create_chat_message
from db.session import get_db
from util.deps import get_current_user
from util.logging import log_api_call
from util.llm_client import LLMServiceClient
from util.profile_converter import convert_profile_to_llm_format

router = APIRouter(prefix="/chatrooms", tags=["chat"])


@router.post("/{chatroom_id}/chat", response_model=ChatResponse)
@log_api_call
async def chat_with_llm(
    chatroom_id: int,
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채팅방에서 LLM과 대화합니다.
    
    1. 사용자 메시지를 DB에 저장
    2. 사용자 프로필 조회 및 변환
    3. LLM-service에 요청 전송
    4. LLM 응답을 DB에 저장
    5. 응답 반환
    
    Args:
        chatroom_id: 채팅방 ID
        request: 채팅 요청 (사용자 메시지)
        
    Returns:
        ChatResponse: LLM 응답과 추천 채용공고
    """
    
    # 1. 채팅방 존재 및 권한 확인
    chatroom = get_chatroom(db, chatroom_id, current_user.id)
    if not chatroom:
        raise HTTPException(
            status_code=404,
            detail="채팅방을 찾을 수 없습니다."
        )
    
    try:
        # 2. 사용자 메시지를 DB에 저장
        user_message_data = ChatMessageCreate(
            content=request.message,
            sender="user"
        )
        create_chat_message(db, chatroom_id, user_message_data)
        
        # 3. 사용자 프로필 조회
        profile = get_profile(db, current_user.id)
        if not profile:
            raise HTTPException(
                status_code=500,
                detail="사용자 프로필을 찾을 수 없습니다."
            )
        
        # 4. 프로필을 LLM-service 형식으로 변환
        llm_profile = convert_profile_to_llm_format(profile, db)
        
        # 5. LLM-service에 요청 전송
        llm_client = LLMServiceClient()
        llm_response = await llm_client.generate_response(
            query=request.message,
            profile=llm_profile
        )
        
        # 6. LLM 응답을 DB에 저장
        llm_message_data = ChatMessageCreate(
            content=llm_response.content,
            sender="llm",
            recommended_jobs=llm_response.recommended_jobs
        )
        create_chat_message(db, chatroom_id, llm_message_data)
        
        # 7. 응답 반환
        return ChatResponse(
            user_message=request.message,
            llm_response=llm_response.content,
            recommended_jobs=llm_response.recommended_jobs,
            created_at=datetime.now()
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
        
    except Exception as e:
        # 기타 모든 예외는 500 에러로 처리
        raise HTTPException(
            status_code=500,
            detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}"
        ) 