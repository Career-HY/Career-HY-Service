import os
import time
from fastapi import APIRouter, HTTPException
from .models import RetrievalRequest, RetrievalResponse, JobPosting, VectorSearchRequest, VectorSearchResponse
from services import OpenAITextEmbedder, DataProcessor, ProfileQueryBuilder
from storage import query_chroma
from util.logging import log_api_call
from typing import Dict, Any

# 임베딩 모델 초기화
embedder = OpenAITextEmbedder()

# ChromaDB 저장 경로 - 환경변수 사용 (Docker 환경 고려)
PERSIST_DIR = os.getenv(
    "VECTOR_STORE_PATH", 
    "/app/data/vector_store_pymupdf_text-embedding-ada-002_chroma"
)

# 데이터 프로세서 초기화
data_processor = DataProcessor()

router = APIRouter()


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
        profile_query = ProfileQueryBuilder.create_profile_query(
            major=request.major,
            catalogs=request.catalogs,
            interest_job=request.interest_job,
            certification=request.certification,
            club_activities=request.club_activities,  
            query=request.query,  
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
                    rec_idx=metadata.get("rec_idx"),
                    title=metadata.get("post_title", "제목 없음"),
                    url=metadata.get("detail_url", ""),
                    deadline=metadata.get("deadline", "미정"),
                    start_date=metadata.get("start_date"),
                    crawling_time=metadata.get("crawling_time"),
                    content=doc,
                )
                job_postings.append(job_posting)

        return RetrievalResponse(results=job_postings)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during document retrieval: {str(e)}",
        )


@router.post("/process-s3-data")
@log_api_call
async def process_s3_data() -> Dict[str, Any]:
    """
    S3에서 초기 데이터셋을 로드하고 벡터 데이터베이스에 저장하는 API 엔드포인트
    
    Returns:
    - Dict[str, Any]: 처리 결과 요약
    """
    try:
        result = data_processor.process_s3_data()
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"S3 데이터 처리 실패: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "message": "S3 데이터 처리 완료",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"S3 데이터 처리 중 오류 발생: {str(e)}"
        )


@router.post("/vector-search-test", response_model=VectorSearchResponse)
@log_api_call
async def vector_search_test(request: VectorSearchRequest) -> VectorSearchResponse:
    """
    벡터 검색 테스트 API 엔드포인트
    
    Parameters:
    - request: VectorSearchRequest
        - query: 검색할 쿼리 텍스트
        - top_k: 반환할 문서 개수 (기본값: 5)
    
    Returns:
    - VectorSearchResponse: 검색 결과와 메타데이터
    """
    try:
        # 검색 시간 측정 시작
        start_time = time.time()
        
        # ChromaDB에서 벡터 검색
        results = query_chroma(
            query=request.query,
            embedder=embedder,
            persist_dir=PERSIST_DIR,
            top_k=request.top_k,
        )
        
        # 검색 시간 계산
        search_time_ms = (time.time() - start_time) * 1000
        
        # 검색 결과 포맷팅
        job_postings = []
        total_found = 0
        
        if results and results.get("documents"):
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            total_found = len(documents)
            
            for doc, metadata in zip(documents, metadatas):
                job_posting = JobPosting(
                    rec_idx=metadata.get("rec_idx"),
                    title=metadata.get("post_title", "제목 없음"),
                    url=metadata.get("detail_url", ""),
                    deadline=metadata.get("deadline", "미정"),
                    start_date=metadata.get("start_date"),
                    crawling_time=metadata.get("crawling_time"),
                    content=doc,
                )
                job_postings.append(job_posting)

        return VectorSearchResponse(
            query=request.query,
            total_found=total_found,
            results=job_postings,
            search_time_ms=round(search_time_ms, 2)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"벡터 검색 테스트 중 오류 발생: {str(e)}",
        )


@router.get("/similar/{seed_id}")
async def similar_docs(seed_id: str, top_n: int = 10, pick_k: int = 4):
    """시드 채용공고 기준 유사 문서 목록(distance 포함) 반환"""
    from storage.vector_store import get_similar_postings

    candidates = get_similar_postings(
        seed_id=seed_id,
        persist_dir=PERSIST_DIR,
        top_n=top_n,
        pick_k=pick_k,
    )

    return {"seed_rec_idx": seed_id, "candidates": candidates}


@router.get("/all-ids")
async def all_ids():
    """컬렉션에 존재하는 모든 rec_idx 리스트 반환"""
    from storage.vector_store import get_all_rec_ids
    ids = get_all_rec_ids(PERSIST_DIR)
    return ids


@router.get("/post/{rec_idx}")
async def get_post(rec_idx: str):
    """단일 rec_idx에 대한 메타데이터와 텍스트 일부 반환"""
    import chromadb
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    col = client.get_or_create_collection(name="job-postings")
    data = col.get(ids=[rec_idx], include=["metadatas", "documents"])
    if not data["metadatas"]:
        raise HTTPException(status_code=404, detail="rec_idx not found")
    meta = data["metadatas"][0]
    excerpt = data["documents"][0][:500]
    return {"rec_idx": rec_idx, "metadata": meta, "excerpt": excerpt}
