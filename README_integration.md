# Career-HY 🎯


**맞춤 채용공고 추천 RAG 시스템**

https://careerhy.com/

<br>

## 📋 프로젝트 개요

Career-HY는 한양대학교 학생들의 수강 이력과 개인 프로필을 기반으로 맞춤형 채용공고를 추천하는 AI 시스템입니다. 사람인 채용공고 데이터와 수강편람 데이터를 결합하여 개인 역량에 최적화된 취업 기회를 제공합니다.

<br>

### 1차 개발 목표 (~ 2025년 6월 18일)
- **초기 데이터 수집**
   - 2025-1 수강편람 데이터 -> 검색 쿼리에 사용
   - 2025-5월 시점 사람인 신입 채용 공고 PDF 및 메타데이터 -> 벡터 DB 임베딩에 사용
- **MVP 선정 및 주기능 개발**
- **초기 RAG 환경을 통해 데이터 파이프라인 구축**
   - 초기 임베딩 모델 : OpenAI `text-embedding-ada-002`
   - 초기 벡터 DB : Chroma DB
   - 초기 LLM 모델 : GPT-4.0
   - 초기 청킹 전략 : 문서 단위
- **백엔드 - 프론트엔드 - 검색 - 출력 - 크롤링 서버 통합 연동**
- **LangSmith 도입을 통한 LLM 애플리케이션 모니터링 및 디버깅**

<br>

> ⚠️ **데이터 제약사항**  
> 현재는 2025년도 1학기 수강편람 데이터만 확보되어있는 상태입니다.  
> 따라서 과거에 수강한 과목이 2025년 1학기 시점에 폐강된 상태라면, 해당 과목을 프로필에 추가할 수 없어 검색 쿼리로 사용하지 못합니다.

<br>

### 2차 개발 목표 (1차 완료 이후)
- **RAG 파라미터 최적화 실험**
- **답변 품질 개선을 위한 A/B 테스트**
- **다양한 임베딩 모델 성능 비교**
- **청킹 전략 최적화**
- **다양한 Vector DB 및 Graph DB 성능 실험**
- **과거 한양대학교 수강편람 데이터 추가 수집**
- **프로덕트 관점 편의 기능 및 부가기능 개발**
   - 채용 공고 스크랩
   - JWT 도입
   - 비동기 메시징 등
- **프론트엔드 모바일 최적화**

<br>
<br>

## RAG 아키텍처

![RAG 아키텍처 1 1](https://github.com/user-attachments/assets/9c33450c-913e-4e7f-885c-9e1584a2bb34)



<br>


## 🏗️ 시스템 아키텍처

<img width="2120" height="1360" alt="시스템아키텍처 1 1 1 1 1 2 1" src="https://github.com/user-attachments/assets/31c8bca1-6fda-40ce-900f-2d5455753261" />


docker swarm 기반 분산환경 구축

<br>

## 🚀 주요 컴포넌트

### 1. 📥 Ingestion
**임베딩 처리 및 검색 서버**
- PDF(채용 공고) 문서 로딩 및 텍스트 추출
- 텍스트 전처리 및 정제
- OpenAI `text-embedding-ada-002` 모델 임베딩
- 벡터 DB 적재 및 문서 검색

### 2. 🔗 Backend
**핵심 비즈니스 로직 및 데이터 관리**
- 사용자 관리 (회원가입, 로그인)
- 프로필 관리 (전공, 수강 이력, 관심 분야)
- 사용자 인풋 입력

### 3. 🧠 LLM Service
**AI 기반 상담 및 추천**
- 요청받은 사용자 인풋 + 프로필 정보 기반 Ingestion 서버의 검색 API 호출
- 프롬프팅
- 사용자 맞춤형 답변 생성

### 4. 🕷️ Crawler Service
**실시간 채용정보 수집**
- 채용 사이트 사람인 신입 채용 공고 크롤링 스케줄링
- 수집한 데이터를 S3에 적재

### 5. 📲 Frontend
**사용자 인터페이스 및 상호작용**
- 사용자 회원가입 및 로그인 화면
- 개인 프로필 설정 (전공, 수강 과목, 관심 분야 등)
- AI 상담 채팅 인터페이스
- 채용공고 스크랩 및 관리 기능

<br>

## 🛠️ 기술 스택

### Core Technologies
- **벡터 DB**: ChromaDB
- **웹 프레임워크**: FastAPI
- **데이터베이스**: MySQL (RDS)
- **클라우드 스토리지**: AWS S3
- **문서 처리 및 프롬프팅**: PyMuPDF, LangChain
- **프론트엔드**: React, Next.JS
- **컨테이너**: Docker

### 데이터 소스 ( 2025/6/3 기준 )
- **수강편람**: 한양대학교 2025-1학기 수강편람
- **채용공고**: 2025년 5월 기준 사람인 채용공고

<br>
<br>

## 🚀 빠른 시작

### 사전 준비사항

1. **필수 도구 설치**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **환경 변수 파일 준비**
   프로젝트 루트에 `.env` 파일을 생성하고 다음 변수들을 설정하세요:
   ```env
   # 데이터베이스 설정
   DB_HOST=your_db_host
   DB_PORT=3306
   DB_USER=your_db_user
   DB_PASS=your_db_password
   DB_NAME=your_db_name
   
   # 애플리케이션 설정
   SECRET_KEY=your_secret_key
   DEBUG=true
   CORS_ORIGINS=http://localhost:3000,http://localhost:5001
   
   # 세션 설정
   SESSION_COOKIE_DOMAIN=
   SESSION_COOKIE_SECURE=false
   SESSION_COOKIE_SAMESITE=lax
   
   # 서비스 URL 설정 (Docker 네트워크 내부 통신)
   LLM_SERVICE_URL=http://llm-service:5003
   INGESTION_SERVICE_URL=http://ingestion:5002
   
   # OpenAI API 설정
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-4o-mini
   ```

3. **데이터베이스 준비**
   - MySQL 데이터베이스가 실행 중이어야 합니다
   - 데이터베이스 스키마가 생성되어 있어야 합니다

### 서비스 시작

```bash
# 모든 서비스 빌드 및 시작
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 특정 서비스만 시작
docker-compose up backend
```

### 서비스 상태 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 서비스 로그 확인
docker-compose logs -f backend
docker-compose logs -f llm-service
docker-compose logs -f ingestion

# 헬스체크
curl http://localhost:5001/health
```

### API 문서

- **Swagger UI**: http://localhost:5001/docs
- **ReDoc**: http://localhost:5001/redoc

---

## 🧪 API 테스트

### 테스트 스크립트 사용

프로젝트 루트에 제공된 테스트 스크립트를 사용할 수 있습니다:

```bash
# Bash 스크립트
./test_api.sh

# Python 스크립트
python test_api.py
```

### 주요 API 엔드포인트

#### 사용자 관리
```bash
# 회원가입
curl -X POST http://localhost:5001/users/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "pwd": "password123"}'

# 로그인 (세션 쿠키 저장)
curl -X POST http://localhost:5001/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "pwd": "password123"}' \
  -c cookies.txt
```

#### 프로필 관리
```bash
# 프로필 조회 (인증 필요)
curl -X GET http://localhost:5001/profiles -b cookies.txt

# 프로필 수정
curl -X PATCH http://localhost:5001/profiles \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"major": "컴퓨터소프트웨어학부", ...}'
```

#### 채팅
```bash
# 채팅방 생성
curl -X POST http://localhost:5001/chatrooms \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "첫 번째 채팅방"}'

# LLM 응답 생성
curl -X POST http://localhost:5003/generate-llm \
  -H "Content-Type: application/json" \
  -d '{
    "query": "신입 개발자 채용공고 추천해줘",
    "profile": {...}
  }'
```

---

## 🔧 문제 해결

### 서비스 간 연결 오류

**증상**: `llm-service`가 `ingestion` 서비스에 연결하지 못함

**해결**:
1. `docker-compose.yml`에서 `INGESTION_SERVICE_URL=http://ingestion:5002` 설정 확인
2. 서비스 재시작:
   ```bash
   docker-compose stop llm-service
   docker-compose rm -f llm-service
   docker-compose up -d llm-service
   ```

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인 (macOS)
lsof -i :5001

# 포트 변경 (docker-compose.yml 수정)
ports:
  - "5002:5001"  # 호스트 포트를 5002로 변경
```

### 로그 확인

```bash
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f llm-service

# 에러만 필터링
docker-compose logs llm-service | grep -i error
```

---

## 📝 작업 순서 및 커밋 전략

### 현재 진행 중인 작업

전체 작업은 3개의 Phase로 나뉘어 진행됩니다:

#### Phase 1: 서비스 코드를 Experiment 전략대로 변경 (우선순위: 높음) ✅ 완료
- 청킹 전략 변경 (섹션별 청킹)
- ChromaDB 저장 방식 변경 (청크 단위)
- 메타데이터 보존 강화
- Docker Compose 서비스 간 통신 설정 개선
- Pydantic v2 호환성 개선
- 에러 핸들링 개선

#### Phase 2: GT AGENT API 서비스 병합 (우선순위: 중간)
- GT Agent 관련 API를 Backend 서비스에 통합
- 기존 LLM Service의 GT Agent 기능을 Backend로 이동

#### Phase 3: 통합 문서 및 README 정리 (우선순위: 낮음) ✅ 완료
- 여러 MD 파일 통합
- README에 서비스 설정 및 테스트 가이드 추가
- 문서 구조 정리

<br>
<br>

## 🐹 주요 화면

<img width="1822" alt="스크린샷 2025-06-09 오전 3 33 29" src="https://github.com/user-attachments/assets/d711bf56-1994-46a8-82ab-2945ae07384a" />

<img width="1822" alt="스크린샷 2025-06-09 오전 3 38 43" src="https://github.com/user-attachments/assets/37151680-47ba-4d06-9369-de6836c53dee" />


<br>
<br>

**Developers**: 한양대학교 데이터사이언스 전공 [이의준](https://github.com/LeeEuyJoon), [최하영](https://github.com/rettooo) <br>
**Contact**: hyuds.careerhi@gmail.com

