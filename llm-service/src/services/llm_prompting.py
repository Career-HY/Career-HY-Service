from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
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
import re

logger = logging.getLogger(__name__)


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

    def _extract_recommended_jobs(
        self, response_text: str, documents: List[JobPosting]
    ) -> List[RecommendedJob]:
        """LLM 응답에서 추천된 채용공고를 찾아 RecommendedJob 형태로 반환합니다."""
        recommended_jobs = []

        # 정규식으로 추천된 채용공고의 제목과 회사명 추출
        pattern = r"""(\d)\. [^제]*제목: (.*?)\n회사명: (.*?)\n"""
        matches = re.finditer(pattern, response_text, re.DOTALL)

        for match in matches:
            rank = int(match.group(1))
            title = match.group(2).strip()
            company = match.group(3).strip()

            # 원본 문서에서 일치하는 문서 찾기
            for doc in documents:
                if doc.title.strip() == title:
                    # 원본 문서의 메타데이터를 RecommendedJob 형식으로 변환
                    recommended_job = RecommendedJob(
                        title=doc.title,
                        company=company,
                        url=doc.url,
                        recommendation_reason="",  # 나중에 LLM 응답에서 추출
                        relevance_score=1.0,  # 기본값
                    )
                    recommended_jobs.append(recommended_job)
                    break

        return recommended_jobs[:3]  # 최대 3개만 반환

    async def generate_response(
        self, query: str, documents: List[JobPosting]
    ) -> LLMResponse:
        """사용자 질문에 대한 응답을 생성합니다."""
        try:
            # 문서 포맷팅
            doc_texts = [
                f"문서 {i+1}:\n제목: {doc.title}\n회사명: {getattr(doc, 'company', 'Unknown')}\nURL: {doc.url}\n내용: {doc.content[:200]}..."
                for i, doc in enumerate(documents[: settings.MAX_DOCUMENTS])
            ]
            formatted_docs = "\n\n".join(doc_texts)

            # 프롬프트 템플릿 생성
            prompt = f"""
                아래는 벡터 검색을 통해 불러온 채용공고 10건입니다.

                참고 문서(Top 10 채용공고 요약 및 메타데이터 포함):

                참고 채용공고:
                {formatted_docs}

                사용자 질문: {query}

                사용자의 질문에 반영된 선호와 상황을 바탕으로 위 채용공고 중 **가장 적합한 3개를 선택**하여 아래 형식에 맞춰 구체적으로 추천해주세요.

                답변 형식을 반드시 다음과 같이 작성해주세요:
                [추천 채용공고]
                1. 첫 번째 추천  
                제목: <제목>  
                회사명: <회사명>  
                공고 URL: <URL>  
                추천 이유: <추천 이유>  

                2. 두 번째 추천  
                제목: <제목>  
                회사명: <회사명>  
                공고 URL: <URL>  
                추천 이유: <추천 이유>  

                3. 세 번째 추천  
                제목: <제목>  
                회사명: <회사명>  
                공고 URL: <URL>  
                추천 이유: <추천 이유>  

                [요약]  
                <전체적인 요약 및 추천 기준에 대한 설명>

                [실행 가능한 조언]  
                <사용자가 실제 지원 시 참고할 수 있는 구체적이고 실용적인 팁을 제시해주세요>
                """
            # LLM 호출 (새로운 방식)
            response = await self.llm.ainvoke(prompt)
            llm_response = response.content

            # 추천된 채용공고 파싱 (이전에 만든 간단한 방식 사용)
            recommended_jobs = self._create_recommended_jobs(documents)

            # 토큰 사용량 - 기본값으로 설정 (response에서 접근하기 어려움)
            token_usage = TokenUsage(
                prompt_tokens=len(prompt.split()) * 1.3,  # 대략적 계산
                completion_tokens=len(llm_response.split()) * 1.3,  # 대략적 계산
                total_tokens=len(prompt.split()) * 1.3 + len(llm_response.split()) * 1.3,
            )

            # 메타데이터 생성
            metadata = LLMMetadata(
                model=settings.OPENAI_MODEL,
                tokens=token_usage,
                document_count=len(recommended_jobs),
                total_cost=self._calculate_cost(token_usage),
            )

            # Langsmith에 메타데이터 기록
            self.client.create_run(
                name="job_recommendation",
                inputs={"query": query, "num_documents": len(documents)},
                outputs={
                    "recommended_jobs": [job.dict() for job in recommended_jobs],
                    "token_usage": token_usage.dict(),
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

    def _calculate_cost(self, token_usage: TokenUsage) -> float:
        """토큰 사용량에 따른 비용을 계산합니다."""
        input_cost_per_1k = 0.0015  # $0.0015 per 1K tokens
        output_cost_per_1k = 0.002  # $0.002 per 1K tokens

        input_cost = (token_usage.prompt_tokens / 1000) * input_cost_per_1k
        output_cost = (token_usage.completion_tokens / 1000) * output_cost_per_1k

        return input_cost + output_cost
