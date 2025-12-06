from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langsmith import traceable
from ..api.models import (
    LLMResponse,
    RecommendedJob,
    JobPosting,
    RetrievalRequest,
)
from ..config.config import settings
from .prompt_templates import (
    CONSULTATION_EXAMPLES,
    RECOMMENDATION_EXAMPLES,
    CONSULTATION_GUIDELINE,
    RECOMMENDATION_GUIDANCE,
    BASE_PROMPT_STATIC,
    INTENT_ROUTER_STATIC,
)
import logging
from enum import Enum

logger = logging.getLogger(__name__)


# -----------------------------
# 모듈 상수
# -----------------------------
INTENT_HISTORY_LIMIT = 2  # 의도 분류 시 최근 대화 메시지 수
CHAT_HISTORY_LIMIT = 10  # 프롬프트에 포함할 최대 대화 메시지 수
MAX_RECOMMENDATIONS = 3  # LLM이 반환할 최대 추천 공고 수
NUM_SEARCH_DOCS = 10  # 검색으로 전달되는 채용공고 수


# -----------------------------
# Intent Enum
# -----------------------------
class IntentType(str, Enum):
    """사용자 질문 의도 종류"""

    REJECT = "REJECT"
    SEARCH_NEEDED = "SEARCH_NEEDED"
    NO_SEARCH = "NO_SEARCH"


# -----------------------------
# LangChain with_structured_output을 위한 Pydantic 모델
# -----------------------------
class JobRecommendationResponse(BaseModel):
    """채용공고 추천 응답 구조"""

    recommended_job_indices: List[int] = Field(
        description="추천하는 채용공고의 번호 (1-10). 적합한 공고가 있다면 1~3개를 추천해야 함. 정말 적합한 공고가 없는 경우에만 빈 배열 반환.",
        max_items=3,
        min_items=0,
    )
    overall_advice: str = Field(
        description="전반적인 취업 준비 방향성과 조언, 또는 질문에 대한 답변"
    )
    recommendation_reasons: List[str] = Field(
        description="각 추천 채용공고의 추천 이유를 자세히 설명. recommended_job_indices의 개수와 정확히 일치해야 함.",
        max_items=3,
        min_items=0,
    )
    practical_tips: str = Field(
        description="지원 시 도움이 될 수 있는 구체적인 팁, 또는 추가 조언"
    )


# -----------------------------
# LLMPromptingService
# -----------------------------
class LLMPromptingService:
    def __init__(self):
        """LLM 서비스를 초기화합니다."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
        )

    def _format_chat_history(
        self, chat_history: Optional[List[Dict[str, Any]]], limit: int = None
    ) -> str:
        """chat_history 리스트를 사람이 읽을 수 있는 텍스트로 변환합니다.

        Args:
            chat_history: [{"role": str, "content": str, "recommended_jobs": List[dict]|None}, ...]
            limit: 뒤에서부터 몇 개까지 포함할지 (None이면 모두)
        Returns:
            str: 포맷팅된 문자열 (각 줄에 한 메시지)
        """
        if not chat_history:
            return ""

        msgs = chat_history[-limit:] if limit else chat_history

        formatted_lines: List[str] = []
        for msg in msgs:
            # msg가 dict 또는 Pydantic BaseModel 일 수 있음
            role = (
                msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "")
            )
            content = (
                msg.get("content")
                if isinstance(msg, dict)
                else getattr(msg, "content", "")
            )

            line = f"{role}: {content}"

            # recommended_jobs가 있으면, 최대 3개 제목만 요약하여 추가
            rec_jobs = (
                msg.get("recommended_jobs")
                if isinstance(msg, dict)
                else getattr(msg, "recommended_jobs", None)
            ) or []
            if rec_jobs:
                job_summaries = []
                for idx, job in enumerate(rec_jobs[:3], 1):
                    # dict 또는 Pydantic model 모두 지원
                    get = (
                        (lambda k, default="": job.get(k, default))
                        if isinstance(job, dict)
                        else (lambda k, default="": getattr(job, k, default))
                    )

                    title = get("title")
                    deadline = get("deadline") or "N/A"
                    start_date = get("start_date") or "N/A"
                    url = get("url") or "N/A"
                    reason = get("recommendation_reason") or "N/A"

                    summary_lines = [
                        f"{idx}. {title}",
                        f"   • 마감일: {deadline}",
                        f"   • 시작일: {start_date}",
                        f"   • URL: {url}",
                        f"   • 추천 이유: {reason}",
                    ]
                    job_summaries.append("\n".join(summary_lines))

                if job_summaries:
                    line += "\n    추천 채용공고 상세:\n" + "\n".join(job_summaries)

            formatted_lines.append(line)

        return "\n".join(formatted_lines)

    # Intent Router
    async def _classify_query_intent(
        self, query: str, chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """LLM을 이용해 질문의 의도를 3가지로 분류합니다."""
        try:
            logger.info(f"🔍 의도 분류 시작 - 질문: '{query}'")

            # 대화 이력 로깅 및 포맷팅 (recommended_jobs 포함)
            formatted_history = ""
            if chat_history:
                # 한 번만 포맷팅하여 로깅과 프롬프트 모두에 재사용 (슬라이싱 중복 제거)
                formatted_history = self._format_chat_history(
                    chat_history,
                    limit=INTENT_HISTORY_LIMIT,
                )

                logger.info(
                    f"📝 의도 분류에 사용되는 대화 이력 (최근 {min(len(chat_history), INTENT_HISTORY_LIMIT)}개):"
                )
                for line in formatted_history.split("\n"):
                    logger.info(f"  - {line}")

            # 대화 이력 텍스트 (없으면 빈 문자열)
            history_text = (
                f"\n최근 대화 내용:\n{formatted_history}\n" if formatted_history else ""
            )

            classification_prompt = (
                history_text
                + INTENT_ROUTER_STATIC
                + f"사용자 질문: {query}\n\n답변: REJECT, SEARCH_NEEDED, NO_SEARCH 중 하나만"
            )

            logger.debug(f"📝 의도 분류 프롬프트 전송 중...")
            response = await self.llm.ainvoke(classification_prompt)
            result = response.content.strip().upper()

            logger.info(f"🤖 LLM 의도 분류 응답: '{result}'")

            # 유효한 답변인지 확인
            if "REJECT" in result:
                logger.info(f"❌ 의도 분류 결과: REJECT - 취업/채용과 무관한 질문")
                return IntentType.REJECT
            elif "SEARCH_NEEDED" in result:
                logger.info(f"🔍 의도 분류 결과: SEARCH_NEEDED - 채용공고 검색 필요")
                return IntentType.SEARCH_NEEDED
            elif "NO_SEARCH" in result:
                logger.info(f"💬 의도 분류 결과: NO_SEARCH - 일반 취업 상담")
                return IntentType.NO_SEARCH
            else:
                # 애매한 경우 NO_SEARCH로 처리
                logger.warning(
                    f"⚠️ 의도 분류 결과가 애매함: '{result}' -> NO_SEARCH로 처리"
                )
                return IntentType.NO_SEARCH

        except Exception as e:
            logger.warning(f"💥 의도 분류 실패, 안전하게 NO_SEARCH로 처리: {e}")
            return IntentType.NO_SEARCH

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
                        reason = (
                            reasons[i]
                            if i < len(reasons)
                            else f"{i+1}번째 추천 채용공고"
                        )

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

    def _create_profile_summary(self, profile: RetrievalRequest) -> str:
        """사용자 프로필을 요약 문자열로 변환"""
        try:
            courses = ", ".join([c.course_name for c in profile.catalogs[:5]])
            if len(profile.catalogs) > 5:
                courses += "..."

            summary = (
                f"사용자 프로필:\n"
                f"- 전공: {profile.major}\n"
                f"- 관심 직무: {', '.join(profile.interest_job)}\n"
                f"- 자격증: {', '.join(profile.certification)}\n"
                f"- 수강 과목: {courses}"
            )
            return summary
        except Exception as e:
            logger.warning(f"프로필 요약 생성 실패: {e}")
            return str(profile)

    def _build_base_prompt(
        self, profile_summary: str, history_text: str, query: str
    ) -> str:
        """공통 프롬프트(서두 + 프로필 + 이전 대화 + 사용자 질문) 생성"""
        header = BASE_PROMPT_STATIC
        return (
            header
            + f"이전 대화 기록: {history_text}\n"
            + f"사용자 프로필 정보: {profile_summary}\n\n"
            + f"사용자 질문: {query}\n"
        )

    # ------------------------------------------------------------------
    # 프롬프트 빌더 (Recommendation 전용)
    # ------------------------------------------------------------------

    def _build_recommendation_prompt(
        self, base_prompt: str, documents: List[JobPosting]
    ) -> str:
        """base_prompt 에 검색 문서 및 지침을 붙여 최종 추천 프롬프트를 생성"""

        # 검색 결과 포맷팅 (최대 NUM_SEARCH_DOCS 개)
        doc_texts = [
            (
                f"채용공고 {i + 1}:\n"
                f"제목: {doc.title}\n"
                f"URL: {doc.url}\n"
                f"내용: {doc.content[:300]}..."
            )
            for i, doc in enumerate(documents[:NUM_SEARCH_DOCS])
        ]
        formatted_docs = "\n\n".join(doc_texts)

        guidance = RECOMMENDATION_GUIDANCE

        return (
            base_prompt + "\n다음은 사용자의 프로필과 관심사에 맞춰 검색된 "
            f"{NUM_SEARCH_DOCS}개 채용공고입니다:\n" + formatted_docs + guidance
        )

    @traceable(name="llm_response_generation")
    async def generate_response(
        self,
        query: str,
        documents: List[JobPosting],
        profile: RetrievalRequest,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        *,
        intent: Optional[IntentType] = None,
    ) -> LLMResponse:
        """사용자 질문에 대한 응답을 생성합니다."""
        try:
            logger.info(f"🚀 LLM 응답 생성 시작 - 질문: '{query}'")
            logger.info(f"📊 검색된 문서 수: {len(documents)}")

            # --------------------------------------------------------------------------------
            # 0단계: 공통 프롬프트 구성 (프로필 요약 + 대화 이력 문자열) 1회만 계산
            # --------------------------------------------------------------------------------

            # ----- Chat History -----
            history_text = ""
            if chat_history:
                history_text = self._format_chat_history(
                    chat_history, limit=CHAT_HISTORY_LIMIT
                )
                history_text = f"이전 대화 내용:\n{history_text}\n"

            # ----- Profile Summary -----
            profile_summary = self._create_profile_summary(profile)

            # ----- Base Prompt ----- 모든 분기에 사용되는 공통 프롬프트
            base_prompt = self._build_base_prompt(profile_summary, history_text, query)

            # ----- Intent Classification -----
            if intent is None:
                intent = await self._classify_query_intent(query, chat_history)

            if intent == IntentType.REJECT:
                logger.info(f"🚫 REJECT 경로 - 거부 응답 반환")
                return LLMResponse(
                    content="죄송합니다. 저는 채용공고 추천 및 취업 상담 전문 AI입니다. 서비스 이용이나 취업/채용 관련된 질문을 부탁드립니다.",
                    recommended_jobs=[],
                )

            elif intent == IntentType.NO_SEARCH:
                logger.info(f"💬 NO_SEARCH 경로 - 일반 상담 응답 생성")
                # ----- Consultation Response -----
                response = await self._generate_consultation_response(
                    base_prompt=base_prompt
                )
                return LLMResponse(**response)

            elif intent == IntentType.SEARCH_NEEDED:
                logger.info(f"🔍 SEARCH_NEEDED 경로 - 채용공고 추천 응답 생성")
                # ----- Recommendation Response -----
                response = await self._generate_recommendation_response(
                    documents, base_prompt=base_prompt
                )
                return LLMResponse(**response)

            else:
                logger.warning(f"⚠️ 예상치 못한 의도: '{intent}' - SEARCH_NEEDED로 처리")
                # ----- Recommendation Response -----
                response = await self._generate_recommendation_response(
                    documents, base_prompt=base_prompt
                )
                return LLMResponse(**response)

        except Exception as e:
            logger.error(f"💥 LLM 응답 생성 중 오류: {str(e)}")
            raise

    @traceable(name="consultation_response")
    async def _generate_consultation_response(
        self,
        *,
        base_prompt: str,
    ) -> Dict:
        """문서 검색 없이 일반 취업 상담 응답을 생성합니다."""
        try:
            # base_prompt 는 generate_response 단계에서 반드시 생성되어 전달됩니다.
            # 만약 None 이 넘어오면 로직 오류로 간주합니다.
            if base_prompt is None:
                raise ValueError(
                    "base_prompt must be provided for consultation response"
                )

            additional_guideline = CONSULTATION_GUIDELINE

            consultation_prompt = (
                base_prompt
                + "\n=== 지침 ===\n"
                + additional_guideline
                # + "\n\n=== 답변 예시 ===\n"
                # + self._consultation_examples
            )

            response = await self.llm.ainvoke(consultation_prompt)

            return {
                "content": response.content.strip(),
                "recommended_jobs": [],  # 상담에는 채용공고 추천 없음
            }

        except Exception as e:
            logger.error(f"상담 응답 생성 실패: {str(e)}")
            raise

    @traceable(name="recommendation_response")
    async def _generate_recommendation_response(
        self,
        documents: List[JobPosting],
        *,
        base_prompt: str,
    ) -> Dict:
        """문서 검색 기반 채용공고 추천 응답을 생성합니다."""
        try:
            # 검색된 채용공고 제목 로깅
            logger.info(f"📋 검색된 채용공고 제목들:")
            for i, doc in enumerate(documents[:10], 1):
                logger.info(f"  {i}. {doc.title}")

            # 최종 프롬프트 생성
            prompt = self._build_recommendation_prompt(base_prompt, documents)

            # 프롬프트 일부 로깅 (디버깅용)
            logger.debug(f"🔍 생성된 프롬프트 (앞 500자): {prompt[:500]}...")

            # LangChain with_structured_output 방식
            structured_llm = self.llm.with_structured_output(JobRecommendationResponse)
            result = await structured_llm.ainvoke(prompt)

            # Pydantic v2 호환: result 타입에 따라 dict 변환
            logger.debug(f"🔍 result 타입: {type(result)}")
            if isinstance(result, dict):
                function_args = result
            elif hasattr(result, 'model_dump'):
                function_args = result.model_dump()
            elif hasattr(result, 'dict'):
                function_args = result.dict()
            else:
                # dict로 변환 시도
                function_args = dict(result)

            logger.debug(f"🔍 function_args 타입: {type(function_args)}, keys: {list(function_args.keys()) if isinstance(function_args, dict) else 'N/A'}")

            # LLM structured output 결과 로깅
            logger.info(f"🤖 LLM Structured Output 결과:")
            logger.info(
                f"  - recommended_job_indices: {function_args.get('recommended_job_indices', [])}"
            )
            logger.info(
                f"  - overall_advice 길이: {len(function_args.get('overall_advice', ''))}"
            )
            logger.info(
                f"  - recommendation_reasons 개수: {len(function_args.get('recommendation_reasons', []))}"
            )
            logger.info(
                f"  - practical_tips 길이: {len(function_args.get('practical_tips', ''))}"
            )

            # 전체 응답 텍스트 생성
            if function_args.get("recommended_job_indices"):
                # 채용공고 추천이 있는 경우 - 제목 목록 제거, 조언과 팁만 포함
                llm_response = f"""
{function_args.get('overall_advice', '')}

실무 팁:
{function_args.get('practical_tips', '')}
""".strip()
            else:
                # 일반 상담/조언인 경우 (채용공고 추천 없음)
                llm_response = f"""
{function_args.get('overall_advice', '')}

{function_args.get('practical_tips', '')}
""".strip()

            # 추천된 채용공고 파싱
            recommended_jobs = self._extract_recommended_jobs_from_function_call(
                function_args, documents
            )

            return {
                "content": llm_response,
                "recommended_jobs": recommended_jobs,
            }

        except Exception as e:
            logger.error(f"추천 응답 생성 실패: {str(e)}")
            raise

    # --------------------------------------------------------------
    # 외부 공개용: 의도 분류 래퍼 (검색 여부 판단용)
    # --------------------------------------------------------------

    @traceable(name="query_intent_classification")
    async def classify_query_intent(
        self, query: str, chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> IntentType:
        """외부에서 호출 가능한 의도 분류 함수.

        LLMPromptingService 내부 구현(_classify_query_intent)을 노출하지 않고도
        라우트 레이어에서 문서 검색 필요 여부를 판단할 수 있게 해준다.
        """
        return await self._classify_query_intent(query, chat_history)
