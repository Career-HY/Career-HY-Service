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

        # ------------------------------------------------------------------
        # Few-shot 예시: 상담(Consultation) / 추천(Recommendation) 상황별 분리
        # ------------------------------------------------------------------

        # ---- 가상 프로필 예시 ----
        _demo_profile = (
            "전공: 컴퓨터공학\n"
            "관심 직무: 백엔드, 클라우드\n"
            "자격증: SQLD\n"
            "수강 과목: 자료구조, 운영체제, 네트워크, 데이터베이스, 클라우드컴퓨팅"
        )

        self._consultation_examples = (
            "[예시: 일반 상담]\n"
            f"<사용자 프로필>\n{_demo_profile}\n\n"
            "user: 이 프로필을 가진 학생이 면접 준비를 어떻게 하면 좋을까요?\n"
            "assistant:\n"
            "1) 전공 과목(운영체제, 네트워크)을 기반으로 시스템 이해도를 강조하세요.\n"
            "2) SQLD는 이미 취득하셨으니 정보처리기사 자격증을 준비하시는 것도 좋게 작용할수 있습니다.\n"
            "3) 기술 면접 대비로 자료구조·DB 질문 리스트를 만들어 답변을 연습하세요.\n"
            "4) 팀을 꾸려서 프로젝트를 진행하고 실제로 배포하고 운영경험을 쌓아보는 것도 좋습니다.\n"
        )

        self._recommendation_examples = (
            "[예시: 채용공고 추천 + 후속 질문]\n"
            f"<사용자 프로필>\n{_demo_profile}\n\n"
            "user: 클라우드 관련 인턴 채용공고 3개만 추천해줘\n"
            "assistant: 1) AWS 클라우드 인턴 (마감 4/10) ... 2) Azure 백엔드 인턴 (마감 4/18) ... 3) GCP DevOps 인턴 (마감 4/25) ...\n"
            "user: 방금 추천한 공고 중 기술 스택이 가장 다양한 곳을 알려줘\n"
            "assistant: 세 공고 중 가장 다양한 스택을 다루는 곳은 GCP DevOps 인턴입니다. 이유는 ...\n"
        )


    def _format_chat_history(self, chat_history: Optional[List[Dict[str, Any]]], limit: int = None) -> str:
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
                msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
            )

            line = f"{role}: {content}"

            # recommended_jobs가 있으면, 최대 3개 제목만 요약하여 추가
            rec_jobs = (
                msg.get("recommended_jobs") if isinstance(msg, dict) else getattr(msg, "recommended_jobs", None)
            ) or []
            if rec_jobs:
                job_summaries = []
                for idx, job in enumerate(rec_jobs[:3], 1):
                    # dict 또는 Pydantic model 모두 지원
                    get = (lambda k, default="": job.get(k, default)) if isinstance(job, dict) else (lambda k, default="": getattr(job, k, default))

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
    async def _classify_query_intent(self, query: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """LLM을 이용해 질문의 의도를 3가지로 분류합니다."""
        try:
            logger.info(f"🔍 의도 분류 시작 - 질문: '{query}'")
            
            # 대화 이력 로깅 (recommended_jobs 포함)
            if chat_history:
                logger.info(
                    f"📝 의도 분류에 사용되는 대화 이력 (최근 {min(len(chat_history), 2)}개):"
                )
                history_preview = self._format_chat_history(chat_history, limit=2)
                for line in history_preview.split("\n"):
                    logger.info(f"  - {line}")
            
            # 대화 이력 포맷팅
            history_text = ""
            if chat_history:
                history_text = self._format_chat_history(chat_history, limit=2)
                history_text = f"\n최근 대화 내용:\n{history_text}\n"
            
            classification_prompt = f"""
                {history_text}
                당신은 Career-HY의 AI 어시스턴트 답변 전 질문의 의도를 분류하는 전문가입니다.
                Career-HY는 한양대학교 학생들을 대상으로 하는 채용공고 추천 챗봇 서비스입니다.
                사용자 질문에 대해 질문의 의도를 다음 3가지 중 하나로 분류해주세요:

                1. REJECT: 서비스 이용, 취업/채용과 전혀 무관한 질문
                예시: 
                - "오늘 날씨 어때?"
                - "맛집 추천해줘"
                - "2+2는 뭐야?"
                - 서비스 이용, 취업, 채용, 경력과 완전히 관련 없는 주제

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

                이전 추천 채용공고에 대한 추가 질문은 새로운 검색이 필요없으므로 NO_SEARCH로 분류하세요.
                "안녕 넌 누구야?"와 같은 질문은 서비스 이용에 대한 질문입니다. NO_SEARCH로 분류하세요.
                REJECT에 대해서는 엄격하게 검사하지 말고 서비스 이용, 취업/채용 과 아주 관련없는 질문에 대해서만 본류해주세요. 
                
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

    def _create_profile_summary(self, profile: "RetrievalRequest") -> str:
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

    def _build_base_prompt(self, profile_summary: str, history_text: str, query: str) -> str:
        """공통 프롬프트(서두 + 프로필 + 이전 대화 + 사용자 질문) 생성"""
        return (
            "당신은 Career-HY의 AI 커리어 어시스턴트입니다.\n"
            "Career-HY는 한양대학교 학생들을 대상으로 하는 채용공고 추천 챗봇 서비스입니다.\n\n"
            "우리의 서비스에 대해 묻는 질문이 있다면, 학생들의 수강 이력, 자격증, 관심사 등의 프로필 정보를 활용해 개인 맞춤형 채용공고를 추천할수 있다는 점을 꼭 드러내야해\n"
            "사용자가 아직 프로필 정보를 등록하지 않은 상태라면, 프로필 정보를 등록할 것을 요구해줘 (이미 프로필 정보가 등록이 되어있다면, 굳이 언급할 필요는 없어)\n"
            "사용자의 프로필 정보, 이전 대화 기록을 바탕으로 사용자의 질문에 적절한 답변을 해주세요.\n\n"
            f"이전 대화 기록: {history_text}\n"
            f"사용자 프로필 정보: {profile_summary}\n\n"
            f"사용자 질문: {query}\n"
        )


    async def generate_response(
        self, 
        query: str, 
        documents: List[JobPosting],
        profile: RetrievalRequest,
        chat_history: Optional[List[Dict[str, Any]]] = None
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
                history_text = self._format_chat_history(chat_history, limit=10)
                history_text = f"이전 대화 내용:\n{history_text}\n"

            # ----- Profile Summary -----
            profile_summary = self._create_profile_summary(profile)

            # ----- Base Prompt ----- 모든 분기에 사용되는 공통 프롬프트
            base_prompt = self._build_base_prompt(profile_summary, history_text, query)

            # ----- Intent Classification -----
            intent = await self._classify_query_intent(query, chat_history)
            
            if intent == "REJECT":
                logger.info(f"🚫 REJECT 경로 - 거부 응답 반환")
                return LLMResponse(
                    content="죄송합니다. 저는 채용공고 추천 및 취업 상담 전문 AI입니다. 서비스 이용이나 취업/채용 관련된 질문을 부탁드립니다.",
                    recommended_jobs=[]
                )
            
            elif intent == "NO_SEARCH":
                logger.info(f"💬 NO_SEARCH 경로 - 일반 상담 응답 생성")
                # ----- Consultation Response -----
                response = await self._generate_consultation_response(query, profile, chat_history, base_prompt=base_prompt)
                return LLMResponse(**response)
            
            elif intent == "SEARCH_NEEDED":
                logger.info(f"🔍 SEARCH_NEEDED 경로 - 채용공고 추천 응답 생성")
                # ----- Recommendation Response -----
                response = await self._generate_recommendation_response(query, documents, profile, chat_history, base_prompt=base_prompt)
                return LLMResponse(**response)
            
            else:
                logger.warning(f"⚠️ 예상치 못한 의도: '{intent}' - SEARCH_NEEDED로 처리")
                # ----- Recommendation Response -----
                response = await self._generate_recommendation_response(query, documents, profile, chat_history, base_prompt=base_prompt)
                return LLMResponse(**response)

        except Exception as e:
            logger.error(f"💥 LLM 응답 생성 중 오류: {str(e)}")
            raise

    async def _generate_consultation_response(
        self,
        query: str,
        profile: RetrievalRequest,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        *,
        base_prompt: str | None = None,
    ) -> Dict:
        """문서 검색 없이 일반 취업 상담 응답을 생성합니다."""
        try:
            # 이미 base_prompt 가 준비되어 있으면 그대로 사용, 아니면 기존 방식 유지
            if base_prompt is None:
                profile_summary = self._create_profile_summary(profile)
                history_text = ""
                if chat_history:
                    history_text = self._format_chat_history(chat_history, limit=10)
                    history_text = f"이전 대화 내용:\n{history_text}\n"
                base_prompt = self._build_base_prompt(profile_summary, history_text, query)

            additional_guideline = (
                "다음 형식으로 답변해주세요:\n"
                "1. 사용자의 질문 의도를 파악하고 올바른 답변을 제시하세요."
                "2. 필요한 경우에만 사용자의 프로필을 직접 언급하며 맞춤형 조언 제공하세요.\n"
                "3. 취업 관련 상담이라면, 전공·수강과목·자격증을 활용한 직무 준비 방법 제시해도 좋습니다.\n"
                "3. 필요 시 단계별 실행 방법/체크리스트 포함해주세요.\n"
                "중요!: 사용자가 물어보지 않은 질문에 대해서는 대답하지마세요."
            )

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
        chat_history: Optional[List[Dict[str, Any]]] = None,
        *,
        base_prompt: str | None = None,
    ) -> Dict:
        """문서 검색 기반 채용공고 추천 응답을 생성합니다."""
        try:

            # 문서 포맷팅
            doc_texts = [
                f"채용공고 {i+1}:\n제목: {doc.title}\nURL: {doc.url}\n내용: {doc.content[:300]}..."
                for i, doc in enumerate(documents)
            ]
            formatted_docs = "\n\n".join(doc_texts)

            prompt = (
                base_prompt
                + "\n다음은 사용자의 프로필과 관심사에 맞춰 검색된 10개 채용공고입니다:\n"
                + formatted_docs

                + "\n\n**중요 지침:**\n"
                + "1. 사용자의 질문 의도를 정확히 파악하세요.\n"
                + "2. 사용자의 프로필(전공·수강 과목·자격증·관심 직무)을 적극 활용하여 추천 이유를 작성하세요.\n"

                # + "\n\n=== 추천 예시 ===\n"
                # + self._recommendation_examples
            )
            
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

