from fastapi import APIRouter, HTTPException
from .models import RetrievalRequest, RetrievalResponse, JobPosting
from src.embedder import OpenAITextEmbedder
from src.vector import query_chroma
from src.util.logging import log_api_call

# 임베딩 모델 초기화
embedder = OpenAITextEmbedder()

# ChromaDB 저장 경로
PERSIST_DIR = "./data/vector_store_pymupdf_text-embedding-ada-002_chroma"

router = APIRouter()


def create_profile_query(
    major: str, catalogs: list, interest_job: list, certification: list
) -> str:
    """사용자 프로필 기반 검색 쿼리 생성"""
    query_parts = []

    # 전공 정보 추가
    if major:
        query_parts.append(f"전공: {major}")

    # 관심 직무 추가
    if interest_job:
        query_parts.append(f"관심 직무: {', '.join(interest_job)}")

    # 자격증 정보 추가
    if certification:
        query_parts.append(f"자격증: {', '.join(certification)}")

    # 강의 정보에서 핵심 키워드 추출
    course_keywords = set()
    for course in catalogs:
        # 강의명과 핵심역량에서 키워드 추출
        course_keywords.update(course.course_name.split())
        course_keywords.update(course.core_competency.split())

    if course_keywords:
        query_parts.append(f"관련 키워드: {' '.join(course_keywords)}")
    

    return " ".join(query_parts)


@router.post("/retrieval", response_model=RetrievalResponse)
@log_api_call
async def retrieve_documents(request: RetrievalRequest) -> RetrievalResponse:
    """
    사용자 프로필 기반 문서 검색 API 엔드포인트

    Parameters:
    - request: RetrievalRequest
        - major: 전공
        - catalogs: 강의 목록
        - interest_job: 관심 직무 목록
        - certification: 자격증 목록

    Returns:
    - RetrievalResponse - 검색된 문서 목록 (상위 10개)
    """
    try:
        # 1. 사용자 프로필 기반 검색 쿼리 생성
        profile_query = create_profile_query(
            major=request.major,
            catalogs=request.catalogs,
            interest_job=request.interest_job,
            certification=request.certification,
        )

        # 2. ChromaDB에서 유사 문서 검색
        results = query_chroma(
            query=profile_query,
            embedder=embedder,
            persist_dir=PERSIST_DIR,
            top_k=10,  # 상위 10개 문서만 반환
        )

        # 3. 검색 결과 포맷팅
        job_postings = []
        if results and results.get("documents"):
            for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                job_posting = JobPosting(
                    title=metadata.get("post_title", "제목 없음"),
                    url=metadata.get("detail_url", ""),
                    deadline=metadata.get("deadline", "미정"),
                    content=doc,
                )
                job_postings.append(job_posting)

        return RetrievalResponse(results=job_postings)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during document retrieval: {str(e)}",
        )
