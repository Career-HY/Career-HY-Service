from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.feedback import JobRecommendationFeedbackCreate, JobRecommendationFeedbackRead
from crud.feedback import create_feedback, get_feedback_by_chat_history_and_member
from db.session import get_db
from util.deps import get_current_user
from typing import List

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/job-recommendation", response_model=JobRecommendationFeedbackRead)
def submit_job_recommendation_feedback(
    feedback_in: JobRecommendationFeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 중복 평가 방지
    existing = get_feedback_by_chat_history_and_member(db, feedback_in.chat_history_id, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="이미 평가를 제출하셨습니다.")
    feedback = create_feedback(db, current_user.id, feedback_in)
    return feedback 