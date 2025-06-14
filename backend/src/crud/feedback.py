from sqlalchemy.orm import Session
from db.models import JobRecommendationFeedback
from schemas.feedback import JobRecommendationFeedbackCreate
from typing import Optional, List

def create_feedback(db: Session, member_id: str, feedback_in: JobRecommendationFeedbackCreate) -> JobRecommendationFeedback:
    feedback = JobRecommendationFeedback(
        chat_history_id=feedback_in.chat_history_id,
        member_id=member_id,
        rating=feedback_in.rating,
        reason=feedback_in.reason
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def get_feedback_by_chat_history_and_member(db: Session, chat_history_id: int, member_id: str) -> Optional[JobRecommendationFeedback]:
    return db.query(JobRecommendationFeedback).filter_by(
        chat_history_id=chat_history_id,
        member_id=member_id
    ).first()

def get_feedbacks_by_chat_history(db: Session, chat_history_id: int) -> List[JobRecommendationFeedback]:
    return db.query(JobRecommendationFeedback).filter_by(chat_history_id=chat_history_id).all() 