from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from crud.user import get_user_by_id

# 로그인된 사용자 정보를 가져오는 함수입니다.
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="인증이 필요합니다")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다")
    return user
