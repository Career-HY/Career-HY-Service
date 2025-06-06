from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from ..api.models import (
    LLMResponse,
    LLMMetadata,
    TokenUsage,
    RecommendedJob,
    JobPosting,
)
from ..config.config import settings
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
import logging

logger = logging.getLogger(__name__)


# LangChain with_structured_output을 위한 Pydantic 모델
class JobRecommendationResponse(BaseModel):
    """채용공고 추천 응답 구조"""
    recommended_job_indices: List[int] = Field(
        description="추천하는 채용공고의 번호 (1-10)", 
        min_items=3, 
        max_items=3
    )
    overall_advice: str = Field(description="전반적인 취업 준비 방향성과 조언")
    recommendation_reasons: List[str] = Field(
        description="각 추천 채용공고의 추천 이유", 
        min_items=3, 
        max_items=3
    )
    practical_tips: str = Field(description="지원 시 도움이 될 수 있는 구체적인 팁")


class LLMPromptingService:
    def __init__(self):
        """LLM 서비스를 초기화합니다."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )
        # Langsmith 설정
        self.client = Client()
        self.tracer = LangChainTracer(project_name="career-hi-rag")

    def _extract_recommended_jobs_from_function_call(
        self, function_args: Dict[str, Any], documents: List[JobPosting]
    ) -> List[RecommendedJob]:
        """Function Call 결과에서 추천된 채용공고를 추출합니다."""
        recommended_jobs = []
        
        try:
            # Function Call에서 추천 인덱스와 이유 추출
            indices = function_args.get("recommended_job_indices", [])
            reasons = function_args.get("recommendation_reasons", [])
            
            # RecommendedJob 객체 생성
            for i, idx in enumerate(indices[:3]):  # 최대 3개
                try:
                    doc_idx = int(idx) - 1  # 1-based를 0-based로 변환
                    if 0 <= doc_idx < len(documents):
                        doc = documents[doc_idx]
                        reason = reasons[i] if i < len(reasons) else f"{i+1}번째 추천 채용공고"
                        
                        recommended_job = RecommendedJob(
                            title=doc.title,
                            url=doc.url,
                            recommendation_reason=reason,
                        )
                        recommended_jobs.append(recommended_job)
                except (ValueError, IndexError):
                    continue
                    
        except Exception as e:
            logger.warning(f"Function Call 결과 파싱 실패, fallback 사용: {e}")
            # 파싱 실패 시 상위 3개로 fallback
            for i, doc in enumerate(documents[:3]):
                recommended_job = RecommendedJob(
                    title=doc.title,
                    url=doc.url,
                    recommendation_reason=f"{i+1}번째 추천 - 상위 검색 결과",
                )
                recommended_jobs.append(recommended_job)

        return recommended_jobs

    async def generate_response(
        self, query: str, documents: List[JobPosting]
    ) -> LLMResponse:
        """사용자 질문에 대한 응답을 생성합니다."""
        try:
            # 문서 포맷팅
            doc_texts = [
                f"채용공고 {i+1}:\n제목: {doc.title}\nURL: {doc.url}\n내용: {doc.content[:300]}..."
                for i, doc in enumerate(documents)
            ]
            formatted_docs = "\n\n".join(doc_texts)

            # 프롬프트 템플릿 생성 (Function Calling용으로 단순화)
            prompt = f"""
                다음은 사용자의 프로필과 관심사에 맞춰 검색된 10개 채용공고입니다.

                검색된 채용공고:
                {formatted_docs}

                사용자 질문: {query}

                위 10개 채용공고 중에서 사용자에게 가장 적합한 3개를 선별하여 추천해주세요.
                """
            
            # LangChain with_structured_output 방식 (파싱 없이 직접 JSON 받기)
            structured_llm = self.llm.with_structured_output(JobRecommendationResponse)
            
            # LLM 호출 (매우 간단!)
            result: JobRecommendationResponse = await structured_llm.ainvoke(prompt)
            
            # 결과를 dict로 변환 (function_args와 동일한 형태)
            function_args = result.dict()
            
            # 전체 응답 텍스트 생성 (사용자에게 보여줄 content)
            llm_response = f"""
                {function_args['overall_advice']}

                추천 채용공고:
                {chr(10).join([f"{i+1}. {reason}" for i, reason in enumerate(function_args['recommendation_reasons'])])}

                실무 팁:
                {function_args['practical_tips']}
            """.strip()

            # 추천된 채용공고 파싱 (Function Call 결과 직접 사용)
            recommended_jobs = self._extract_recommended_jobs_from_function_call(function_args, documents)

            # 메타데이터 생성 (with_structured_output은 토큰 정보 미제공)
            metadata = LLMMetadata(
                model=settings.OPENAI_MODEL,
                tokens=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                document_count=len(recommended_jobs),
                total_cost=0.0,
            )

            # Langsmith에 메타데이터 기록
            self.client.create_run(
                name="job_recommendation",
                run_type="llm",
                inputs={"query": query, "num_documents": len(documents)},
                outputs={
                    "recommended_jobs": [job.dict() for job in recommended_jobs],
                    "token_usage": metadata.tokens.dict(),
                },
            )

            return LLMResponse(
                content=llm_response,
                metadata=metadata,
                recommended_jobs=recommended_jobs,
                relevant_documents=documents,
            )

        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

