from fastapi import APIRouter, HTTPException
from .models import RetrievalRequest, RetrievalResponse, JobPosting
from embedder import OpenAITextEmbedder
from vector import query_chroma
from util.logging import log_api_call
from data_processor import DataProcessor
from typing import Dict, Any

# 임베딩 모델 초기화
embedder = OpenAITextEmbedder()

# ChromaDB 저장 경로
PERSIST_DIR = "./data/vector_store_pymupdf_text-embedding-ada-002_chroma"

# 데이터 프로세서 초기화
data_processor = DataProcessor()

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


@router.get("/vector-store-status")
@log_api_call
async def get_vector_store_status() -> Dict[str, Any]:
    """
    벡터 저장소 상태를 확인하는 API 엔드포인트
    
    Returns:
    - Dict[str, Any]: 벡터 저장소 상태 정보
    """
    try:
        status = data_processor.check_vector_store_status()
        return {
            "message": "벡터 저장소 상태 조회 완료",
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"벡터 저장소 상태 확인 중 오류 발생: {str(e)}"
        )


@router.post("/initialize-from-s3")
@log_api_call  
async def initialize_from_s3() -> Dict[str, Any]:
    """
    S3에서 데이터를 초기화하는 원클릭 API 엔드포인트
    벡터 저장소 상태를 확인하고, 비어있다면 S3에서 데이터를 로드합니다.
    
    Returns:
    - Dict[str, Any]: 초기화 결과
    """
    try:
        # 1. 벡터 저장소 상태 확인
        status = data_processor.check_vector_store_status()
        
        if status.get("status") == "available":
            return {
                "message": "벡터 저장소가 이미 초기화되어 있습니다.",
                "status": status,
                "action": "no_action_needed"
            }
        
        # 2. 벡터 저장소가 비어있거나 오류가 있다면 S3에서 데이터 로드
        result = data_processor.process_s3_data()
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"S3 데이터 초기화 실패: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "message": "S3에서 데이터 초기화 완료",
            "result": result,
            "action": "initialized_from_s3"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"S3 초기화 중 오류 발생: {str(e)}"
        )


@router.get("/debug-json-structure")
@log_api_call
async def debug_json_structure() -> Dict[str, Any]:
    """
    JSON 데이터 구조를 확인하는 디버깅 API 엔드포인트
    """
    try:
        from s3_loader import S3DataLoader
        loader = S3DataLoader()
        
        # S3에서 JSON 파일 로드
        json_data = loader.load_json_files()
        
        if not json_data:
            return {"error": "JSON 데이터가 없습니다."}
        
        # 첫 번째 JSON 객체 분석
        first_item = json_data[0]
        
        result = {
            "total_records": len(json_data),
            "first_item": first_item,
            "all_fields": list(first_item.keys()) if isinstance(first_item, dict) else [],
            "title_fields": [],
            "url_fields": [],
            "date_fields": []
        }
        
        if isinstance(first_item, dict):
            # 제목 관련 필드 찾기
            for key in first_item.keys():
                if 'title' in key.lower():
                    result["title_fields"].append({
                        "field": key,
                        "value": first_item[key]
                    })
            
            # URL 관련 필드 찾기
            for key in first_item.keys():
                if 'url' in key.lower() or 'link' in key.lower():
                    result["url_fields"].append({
                        "field": key,
                        "value": first_item[key]
                    })
            
            # 날짜 관련 필드 찾기
            for key in first_item.keys():
                if any(word in key.lower() for word in ['date', 'deadline', 'close', 'end', '마감', '날짜']):
                    result["date_fields"].append({
                        "field": key,
                        "value": first_item[key]
                    })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON 구조 확인 중 오류 발생: {str(e)}"
        )


@router.get("/debug-vector-metadata")
@log_api_call
async def debug_vector_metadata() -> Dict[str, Any]:
    """
    벡터 저장소에 실제로 저장된 메타데이터를 확인하는 디버깅 엔드포인트
    """
    try:
        from vector import query_chroma
        
        # 테스트 쿼리로 몇 개 문서 가져오기
        results = query_chroma(
            query="채용",
            embedder=embedder,
            persist_dir=PERSIST_DIR,
            top_k=3
        )
        
        if not results or not results.get('metadatas'):
            return {"error": "벡터 저장소에 데이터가 없습니다."}
        
        # 실제 저장된 메타데이터 분석
        sample_metadatas = results['metadatas'][0][:3]  # 첫 3개만
        
        result = {
            "total_found": len(results['metadatas'][0]) if results['metadatas'] else 0,
            "sample_metadatas": sample_metadatas,
            "metadata_analysis": []
        }
        
        # 각 메타데이터 분석
        for i, metadata in enumerate(sample_metadatas):
            analysis = {
                "index": i,
                "all_fields": list(metadata.keys()) if isinstance(metadata, dict) else [],
                "has_post_title": "post_title" in metadata if isinstance(metadata, dict) else False,
                "has_detail_url": "detail_url" in metadata if isinstance(metadata, dict) else False,
                "has_deadline": "deadline" in metadata if isinstance(metadata, dict) else False,
                "post_title_value": metadata.get("post_title") if isinstance(metadata, dict) else None,
                "detail_url_value": metadata.get("detail_url") if isinstance(metadata, dict) else None,
                "deadline_value": metadata.get("deadline") if isinstance(metadata, dict) else None,
            }
            result["metadata_analysis"].append(analysis)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"벡터 메타데이터 확인 중 오류 발생: {str(e)}"
        )
