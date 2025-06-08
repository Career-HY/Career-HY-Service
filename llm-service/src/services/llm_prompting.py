from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from ..api.models import (
    LLMResponse,
    RecommendedJob,
    JobPosting,
    RetrievalRequest,
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
        description="추천하는 채용공고의 번호 (1-10), 채용공고 추천이 불필요한 경우 빈 배열", 
        max_items=3,
        # default=[]
        min_items=3
    )
    overall_advice: str = Field(description="전반적인 취업 준비 방향성과 조언, 또는 질문에 대한 답변")
    recommendation_reasons: List[str] = Field(
        description="각 추천 채용공고의 추천 이유 설명 자세히, 채용공고 추천이 없으면 빈 배열", 
        max_items=3,
        # default=[]
        min_items=3
    )
    practical_tips: str = Field(description="지원 시 도움이 될 수 있는 구체적인 팁, 또는 추가 조언")


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

    async def _classify_query_intent(self, query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """LLM을 이용해 질문의 의도를 3가지로 분류합니다."""
        try:
            logger.info(f"🔍 의도 분류 시작 - 질문: '{query}'")
            
            # 대화 이력 로깅
            if chat_history:
                logger.info(f"📝 의도 분류에 사용되는 대화 이력 (최근 {len(chat_history[-2:])}개):")
                for msg in chat_history[-2:]:
                    logger.info(f"  - {msg['role']}: {msg['content']}")
            
            # 대화 이력 포맷팅
            history_text = ""
            if chat_history:
                history_text = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in chat_history[-2:]  # 최근 2개 메시지만 사용
                ])
                history_text = f"\n최근 대화 내용:\n{history_text}\n"
            
            classification_prompt = f"""
                {history_text}
                질문을 다음 3가지 중 하나로 분류해주세요:

                1. REJECT: 취업/채용과 전혀 무관한 질문
                예시: 
                - "오늘 날씨 어때?"
                - "맛집 추천해줘"
                - "2+2는 뭐야?"
                - 취업, 채용, 경력과 완전히 관련 없는 주제

                2. SEARCH_NEEDED: 새로운 채용공고 검색이 필요한 질문
                예시: 
                - "추천 채용공고 알려줘"
                - "백엔드 개발자 채용 정보 찾아줘"
                - "○○ 회사 채용 있어?"
                - "신입 개발자 공고 추천해줘"
                - 새로운 채용공고를 찾아야 하는 질문들

                3. NO_SEARCH: 검색이 필요없는 취업 관련 질문
                예시:
                - "자기소개서 작성법 알려줘"
                - "면접 준비 방법 알려줘"
                - "이전에 추천해준 공고에 대해 더 자세히 설명해줘"
                - "방금 추천한 첫 번째 공고는 어떤 공고야?"
                - "그 회사 면접은 어떻게 준비하면 좋을까?"
                - 기존 추천에 대한 추가 질문
                - 일반적인 취업 상담 질문

                중요: 이전 추천 채용공고에 대한 추가 질문은 새로운 검색이 필요없으므로 NO_SEARCH로 분류하세요.
                
                사용자 질문: {query}

                답변: REJECT, SEARCH_NEEDED, NO_SEARCH 중 하나만
                """
            
            logger.debug(f"📝 의도 분류 프롬프트 전송 중...")
            response = await self.llm.ainvoke(classification_prompt)
            result = response.content.strip().upper()
            
            logger.info(f"🤖 LLM 의도 분류 응답: '{result}'")
            
            # 유효한 답변인지 확인
            if "REJECT" in result:
                logger.info(f"❌ 의도 분류 결과: REJECT - 취업/채용과 무관한 질문")
                return "REJECT"
            elif "SEARCH_NEEDED" in result:
                logger.info(f"🔍 의도 분류 결과: SEARCH_NEEDED - 채용공고 검색 필요")
                return "SEARCH_NEEDED"
            elif "NO_SEARCH" in result:
                logger.info(f"💬 의도 분류 결과: NO_SEARCH - 일반 취업 상담")
                return "NO_SEARCH"
            else:
                # 애매한 경우 NO_SEARCH로 처리
                logger.warning(f"⚠️ 의도 분류 결과가 애매함: '{result}' -> NO_SEARCH로 처리")
                return "NO_SEARCH"
            
        except Exception as e:
            logger.warning(f"💥 의도 분류 실패, 안전하게 NO_SEARCH로 처리: {e}")
            return "NO_SEARCH"

    def _extract_recommended_jobs_from_function_call(
        self, function_args: Dict[str, Any], documents: List[JobPosting]
    ) -> List[RecommendedJob]:
        """Function Call 결과에서 추천된 채용공고를 추출합니다."""
        recommended_jobs = []
        
        try:
            # Function Call에서 추천 인덱스와 이유 추출
            indices = function_args.get("recommended_job_indices", [])
            reasons = function_args.get("recommendation_reasons", [])
            
            # 빈 배열인 경우 (일반 상담/조언) 빈 리스트 반환
            if not indices:
                return []
            
            # RecommendedJob 객체 생성
            for i, idx in enumerate(indices[:3]):  # 최대 3개
                try:
                    doc_idx = int(idx) - 1  # 1-based를 0-based로 변환
                    if 0 <= doc_idx < len(documents):
                        doc = documents[doc_idx]
                        reason = reasons[i] if i < len(reasons) else f"{i+1}번째 추천 채용공고"
                        
                        recommended_job = RecommendedJob(
                            rec_idx=doc.rec_idx,
                            title=doc.title,
                            url=doc.url,
                            deadline=doc.deadline,
                            start_date=doc.start_date,
                            crawling_time=doc.crawling_time,
                            recommendation_reason=reason,
                        )
                        recommended_jobs.append(recommended_job)
                except (ValueError, IndexError):
                    continue
                    
        except Exception as e:
            logger.warning(f"Function Call 결과 파싱 실패: {e}")
            # 빈 인덱스 배열이면 빈 리스트 반환 (fallback하지 않음)
            if not function_args.get("recommended_job_indices", []):
                return []
            
            # 파싱 실패하고 인덱스가 있는 경우만 fallback
            logger.warning("상위 3개로 fallback 사용")
            for i, doc in enumerate(documents[:3]):
                recommended_job = RecommendedJob(
                    rec_idx=doc.rec_idx,
                    title=doc.title,
                    url=doc.url,
                    deadline=doc.deadline,
                    start_date=doc.start_date,
                    crawling_time=doc.crawling_time,
                    recommendation_reason=f"{i+1}번째 추천 - 상위 검색 결과",
                )
                recommended_jobs.append(recommended_job)

        return recommended_jobs

    def _create_prompt(
        self, 
        query: str, 
        documents: List[str],
        profile: Dict,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """프롬프트 생성"""
        
        # 대화 이력 포맷팅
        history_text = ""
        if chat_history:
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history[-5:]  # 최근 5개 메시지만 사용
            ])
            history_text = f"\n이전 대화 내용:\n{history_text}\n"

        # 문서 컨텍스트 포맷팅
        docs_text = "\n---\n".join(documents) if documents else "관련 문서가 없습니다."
        
        return f"""당신은 Career-Hi의 AI 커리어 어시스턴트입니다.
            사용자의 프로필과 질문을 바탕으로 커리어 관련 조언을 제공해주세요.

            {history_text}
            사용자 프로필:
            {profile}

            관련 문서:
            {docs_text}

            사용자 질문: {query}

            답변:"""

    async def generate_response(
        self, 
        query: str, 
        documents: List[JobPosting],
        profile: RetrievalRequest,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> LLMResponse:
        """사용자 질문에 대한 응답을 생성합니다."""
        try:
            logger.info(f"🚀 LLM 응답 생성 시작 - 질문: '{query}'")
            logger.info(f"📊 검색된 문서 수: {len(documents)}")
            
            # 1단계: LLM으로 질문 의도 분류 (토큰 절약을 위한 간단한 프롬프트)
            intent = await self._classify_query_intent(query, chat_history)
            
            if intent == "REJECT":
                logger.info(f"🚫 REJECT 경로 - 거부 응답 반환")
                return LLMResponse(
                    content="죄송합니다. 저는 채용공고 추천 및 취업 상담 전문 AI입니다. 취업이나 채용과 관련된 질문을 부탁드립니다.",
                    recommended_jobs=[]
                )
            
            elif intent == "NO_SEARCH":
                logger.info(f"💬 NO_SEARCH 경로 - 일반 상담 응답 생성")
                # 문서 검색 없이 일반 취업 상담 응답 생성
                response = await self._generate_consultation_response(query, profile, chat_history)
                return LLMResponse(**response)
            
            elif intent == "SEARCH_NEEDED":
                logger.info(f"🔍 SEARCH_NEEDED 경로 - 채용공고 추천 응답 생성")
                # 기존 로직: 문서 검색
                response = await self._generate_recommendation_response(query, documents, profile, chat_history)
                return LLMResponse(**response)
            
            else:
                logger.warning(f"⚠️ 예상치 못한 의도: '{intent}' - SEARCH_NEEDED로 처리")
                # 예상치 못한 경우, 안전하게 검색 진행
                response = await self._generate_recommendation_response(query, documents, profile, chat_history)
                return LLMResponse(**response)

        except Exception as e:
            logger.error(f"💥 LLM 응답 생성 중 오류: {str(e)}")
            raise

    async def _generate_consultation_response(
        self, 
        query: str, 
        profile: RetrievalRequest,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """문서 검색 없이 일반 취업 상담 응답을 생성합니다."""
        try:
            # 사용자 프로필 정보 정리
            profile_summary = f"""
사용자 프로필:
- 전공: {profile.major}
- 관심 직무: {', '.join(profile.interest_job)}
- 자격증: {', '.join(profile.certification)}
- 수강 과목: {', '.join([course.course_name for course in profile.catalogs[:5]])}{"..." if len(profile.catalogs) > 5 else ""}
"""
            # 대화 이력 포맷팅
            history_text = ""
            if chat_history:
                history_text = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in chat_history[-5:]  # 최근 5개 메시지만 사용
                ])
                history_text = f"\n이전 대화 내용:\n{history_text}\n"
            
            consultation_prompt = f"""
당신은 취업 상담 전문가입니다. 사용자의 프로필을 고려하여 실용적이고 도움이 되는 조언을 제공해주세요.

{history_text}
{profile_summary}

사용자 질문: {query}

다음 형식으로 답변해주세요:
1. 사용자의 프로필을 구체적으로 언급하며 맞춤형 답변 제공
2. 전공, 수강 과목, 자격증을 직접 언급하며 관련된 실무 팁 제공
3. 단계별 실행 방법이나 체크리스트 (필요한 경우)

**중요**: 답변에서 반드시 사용자의 구체적인 프로필 요소를 활용하세요.
- 전공명을 언급하며 해당 분야와 연관된 조언
- 수강 과목을 언급하며 관련 기술이나 지식 활용법
- 자격증을 언급하며 취업 시 활용 방안
- 관심 직무와 연결된 구체적인 방향성

전문적이지만 친근한 톤으로 답변해주세요.
"""
            
            response = await self.llm.ainvoke(consultation_prompt)
            
            return {
                "content": response.content.strip(),
                "recommended_jobs": []  # 상담에는 채용공고 추천 없음
            }
            
        except Exception as e:
            logger.error(f"상담 응답 생성 실패: {str(e)}")
            raise

    async def _generate_recommendation_response(
        self, 
        query: str, 
        documents: List[JobPosting], 
        profile: RetrievalRequest,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """문서 검색 기반 채용공고 추천 응답을 생성합니다."""
        try:
            # 사용자 프로필 정보 정리
            profile_summary = f"""
사용자 프로필:
- 전공: {profile.major}
- 관심 직무: {', '.join(profile.interest_job)}
- 자격증: {', '.join(profile.certification)}
- 수강 과목: {', '.join([course.course_name for course in profile.catalogs[:5]])}{"..." if len(profile.catalogs) > 5 else ""}
"""
            # 대화 이력 포맷팅
            history_text = ""
            if chat_history:
                history_text = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in chat_history[-5:]  # 최근 5개 메시지만 사용
                ])
                history_text = f"\n이전 대화 내용:\n{history_text}\n"
                logger.info(f"📝 추천 응답 생성에 사용되는 대화 이력:\n{history_text}")
            
            # 문서 포맷팅
            doc_texts = [
                f"채용공고 {i+1}:\n제목: {doc.title}\nURL: {doc.url}\n내용: {doc.content[:300]}..."
                for i, doc in enumerate(documents)
            ]
            formatted_docs = "\n\n".join(doc_texts)

            # 프롬프트 템플릿 생성 (채용공고 추천 전용)
            prompt = f"""
당신은 취업 상담 전문가입니다. 사용자의 프로필과 질문에 맞춰 적절한 채용공고를 추천하거나 이전 추천에 대해 설명해주세요.

{history_text}
{profile_summary}

다음은 사용자의 프로필과 관심사에 맞춰 검색된 10개 채용공고입니다:
{formatted_docs}

사용자 질문: {query}

**중요 지침:**
1. 사용자의 질문 의도를 정확히 파악하세요:
   - 새로운 채용공고 추천을 원하는 질문인가요? (예: "어떤 회사에 지원하면 좋을까요?", "추천 채용공고 알려주세요")
   - 이전에 추천한 채용공고에 대한 추가 설명을 요청하는 질문인가요? (예: "첫 번째 공고에 대해 더 자세히 설명해주세요")
   - 특정 기술/직무 관련 채용공고를 찾는 질문인가요?

2. **이전 추천 공고에 대한 설명 요청인 경우:**
   - 대화 이력에서 해당 채용공고를 찾아 구체적으로 설명
   - 해당 공고의 주요 내용, 요구사항, 우대사항 등을 상세히 설명
   - 사용자 프로필과 연관지어 설명 (프로필 정보가 있는 경우)
   - recommended_job_indices는 빈 배열로 설정 (새로운 추천이 아니므로)
   - overall_advice에 해당 공고에 대한 구체적인 설명을 포함
   - practical_tips에 해당 공고 지원 시 도움될 실용적인 조언 포함

3. **새로운 채용공고 추천이 필요한 경우:**
   - 위 10개 채용공고 중에서 사용자의 프로필에 가장 적합한 1~3개를 선별하여 추천
   - recommended_job_indices에 해당 번호들을 포함
   - recommendation_reasons에 추천 이유를 상세히 명시
   - 사용자의 프로필 데이터가 있다면 적극 활용:
     * 전공과 해당 포지션의 연관성
     * 수강 과목과 업무의 연결점
     * 자격증과 채용 우대 조건
     * 관심 직무와 포지션의 일치도
   - "채용공고 1", "채용공고 2" 같은 번호 언급은 피하고 구체적인 회사명/직무로 언급
   - 각 채용공고의 추천 이유는 독립적으로 작성

4. **일반 상담이 필요한 경우:**
   - recommended_job_indices는 빈 배열로 설정
   - overall_advice에 질문에 대한 구체적인 답변 제공
   - practical_tips에 실행 가능한 구체적인 조언 제공
   - 가능한 경우 사용자 프로필 요소를 활용한 맞춤형 조언 제공

답변 시 주의사항:
1. 항상 구체적이고 명확하게 답변하세요
2. 실제 채용공고 내용을 기반으로 답변하세요
3. 이전 대화 맥락을 충분히 고려하세요
4. 불필요하게 장황한 설명은 피하고 핵심적인 내용에 집중하세요
5. 사용자가 요청하지 않은 일반적인 조언은 최소화하세요

사용자의 질문 의도에 가장 적합한 방식으로 응답해주세요.
"""
            
            # LangChain with_structured_output 방식
            structured_llm = self.llm.with_structured_output(JobRecommendationResponse)
            result: JobRecommendationResponse = await structured_llm.ainvoke(prompt)
            function_args = result.dict()
            
            # LLM structured output 결과 로깅
            logger.info(f"🤖 LLM Structured Output 결과:")
            logger.info(f"  - recommended_job_indices: {function_args.get('recommended_job_indices', [])}")
            logger.info(f"  - overall_advice 길이: {len(function_args.get('overall_advice', ''))}")
            logger.info(f"  - recommendation_reasons 개수: {len(function_args.get('recommendation_reasons', []))}")
            logger.info(f"  - practical_tips 길이: {len(function_args.get('practical_tips', ''))}")
            

            # 전체 응답 텍스트 생성
            if function_args['recommended_job_indices']:
                # 채용공고 추천이 있는 경우 - 제목 목록 제거, 조언과 팁만 포함
                llm_response = f"""
{function_args['overall_advice']}

실무 팁:
{function_args['practical_tips']}
""".strip()
            else:
                # 일반 상담/조언인 경우 (채용공고 추천 없음)
                llm_response = f"""
{function_args['overall_advice']}

{function_args['practical_tips']}
""".strip()

            # 추천된 채용공고 파싱
            recommended_jobs = self._extract_recommended_jobs_from_function_call(function_args, documents)

            # Langsmith에 메타데이터 기록
            self.client.create_run(
                name="job_recommendation",
                run_type="llm",
                inputs={"query": query, "num_documents": len(documents)},
                outputs={
                    "recommended_jobs": [job.dict() for job in recommended_jobs],
                },
            )

            return {
                "content": llm_response,
                "recommended_jobs": recommended_jobs,
            }
            
        except Exception as e:
            logger.error(f"추천 응답 생성 실패: {str(e)}")
            raise

