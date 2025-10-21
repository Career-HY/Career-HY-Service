# 크롤러 코드 정리 완료 보고서

## 작업 개요

크롤러 컴포넌트의 모든 코드를 점검하여 사용되지 않는(Dead Code) 항목을 식별하고 정리했습니다.

---

## ✅ 완료된 작업

### 1. config.py - 스케줄 설정 정리

**문제**: `CRAWL_SCHEDULE_HOUR` 변수가 정의되어 있지만 실제로 사용되지 않음

**원인**:
- `scheduler.py`가 환경변수를 **직접** 읽음 (`os.getenv()`)
- `config.py`의 `CRAWL_SCHEDULE_HOUR`는 어디서도 import되지 않음

**해결**:
```python
# 이전
CRAWL_SCHEDULE_HOUR = int(os.getenv("CRAWL_SCHEDULE_HOUR", "2"))
CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "3"))

# 이후
# 주의: CRAWL_SCHEDULE_HOUR/MINUTE은 scheduler.py에서 직접 환경변수를 읽음
CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "3"))
```

**변경 파일**:
- [config.py:21-23](crawler/src/config.py#L21-L23) - 변수 제거
- [config.py:84](crawler/src/config.py#L84) - 테스트 코드에서 참조 제거

**참고**: 실제 스케줄 설정은 [scheduler.py:49-50](crawler/scheduler.py#L49-L50)에서 처리

---

## 📋 Dead Code 목록 (제거 권장)

### 2. main.py - 기존 일괄 처리 크롤러

**상태**: 현재 사용되지 않음 (main_streaming.py로 대체됨)

**설명**:
- `main.py`: 일괄 처리 방식 (1000개 메모리 보관 → OOM 위험)
- `main_streaming.py`: 스트리밍 방식 (10개씩 배치 → 메모리 효율적)
- `scheduler.py`는 현재 `main_streaming.py`를 사용

**제거 여부**:
- ❌ **즉시 제거하지 말 것**
- 이유: 백업/참조용으로 유지
- 권장: 파일명을 `main_legacy.py`로 변경하여 명확히 표시

**제거 시기**: 스트리밍 모드가 안정화된 후 (1-2주 운영 후)

---

### 3. s3_uploader.py - 사용되지 않는 메서드

#### 3.1 `upload_pair()` 메서드 (Line 107-131)

**사용 현황**: ❌ 사용되지 않음

**설명**: 로컬 파일 경로를 받아 PDF/JSON을 업로드하는 기존 방식

**대체 메서드**: `upload_data()` (메모리에서 직접 업로드)

**제거 영향**: 없음 (어디서도 호출되지 않음)

#### 3.2 `upload_pair_by_deadline()` 메서드 (Line 133-164)

**사용 현황**: ❌ 사용되지 않음

**설명**: 마감일 기준 경로로 로컬 파일 업로드 (`by-deadline` 구조)

**참고**: S3 구조가 날짜별 (`datasets/{YYYY-MM-DD}/`)로 변경됨

**제거 영향**: 없음

#### 3.3 `upload_data_by_deadline()` 메서드 (Line 230-293)

**사용 현황**: ❌ 사용되지 않음

**설명**: 마감일 기준 경로로 메모리 데이터 업로드

**제거 영향**: 없음

#### 3.4 `list_active_rec_ids()` 메서드 (Line 417-495)

**사용 현황**: ⚠️ 간접적으로 사용됨 (하지만 호출되지 않음)

**호출 체인**:
```
list_active_rec_ids()
    ↑
load_existing_rec_ids() (saramin_crawler.py:152)
    ↑
(어디서도 호출되지 않음)
```

**제거 영향**: `load_existing_rec_ids()`도 함께 제거 필요

---

### 4. saramin_crawler.py - 사용되지 않는 메서드

#### 4.1 `load_existing_rec_ids()` 메서드 (Line 145-158)

**사용 현황**: ❌ 사용되지 않음

**설명**: S3에서 기존 공고 목록을 로드하여 중복 체크

**참고**: 현재는 `latest_rec_idx` 비교 방식으로 중복 방지

**제거 영향**: 없음

#### 4.2 `existing_rec_ids` 속성 (Line 47)

**사용 현황**: ❌ 사용되지 않음 (`load_existing_rec_ids()`가 사용되지 않음)

**제거 영향**: 없음

#### 4.3 `get_skipped_results()` 메서드 (Line 508-510)

**사용 현황**: ❌ 사용되지 않음

**설명**: 중복으로 스킵된 결과 반환

**참고**: 현재 크롤링 로직에서 'skipped_duplicate' 상태를 사용하지 않음

**제거 영향**: 없음

---

## 📊 Dead Code 제거 효과

### 제거 가능한 코드량

| 파일 | 메서드/변수 | 라인 수 | 제거 여부 |
|------|-----------|--------|----------|
| config.py | `CRAWL_SCHEDULE_HOUR` | 1줄 | ✅ **완료** |
| main.py | 전체 파일 | 261줄 | ⚠️ 레거시로 유지 |
| s3_uploader.py | `upload_pair` | 25줄 | 🟡 권장 |
| s3_uploader.py | `upload_pair_by_deadline` | 32줄 | 🟡 권장 |
| s3_uploader.py | `upload_data_by_deadline` | 64줄 | 🟡 권장 |
| s3_uploader.py | `list_active_rec_ids` | 79줄 | 🟡 권장 |
| saramin_crawler.py | `load_existing_rec_ids` | 14줄 | 🟡 권장 |
| saramin_crawler.py | `existing_rec_ids` | 1줄 | 🟡 권장 |
| saramin_crawler.py | `get_skipped_results` | 3줄 | 🟡 권장 |
| **합계** | | **~480줄** | |

---

## 🔧 현재 사용 중인 코드

### 활성화된 메인 파일
- ✅ **main_streaming.py** - 스케줄러가 사용
- ⚠️ main.py - 레거시 (사용 안 함)

### 사용 중인 s3_uploader 메서드
- ✅ `upload_data()` - 메모리에서 직접 업로드
- ✅ `get_latest_rec_idx()` - 이전 latest 조회
- ✅ `save_latest_rec_idx()` - 최신 latest 저장
- ✅ `check_file_exists()` - 파일 존재 확인
- ✅ `check_rec_idx_exists()` - rec_idx 중복 확인
- ✅ `list_all_rec_idx()` - 전체 목록 조회 (테스트용)

### 사용 중인 saramin_crawler 메서드
- ✅ `create_driver()` - 브라우저 드라이버 생성
- ✅ `extract_job_links()` - 페이지별 공고 링크 추출
- ✅ `crawl_job_detail()` - 개별 공고 크롤링
- ✅ `crawl_with_latest_stop()` - main.py 전용 (레거시)
- ✅ `parse_deadline_to_standard_format()` - 마감일 파싱
- ✅ `get_successful_results()` - 성공 결과 반환
- ✅ `get_failed_results()` - 실패 결과 반환
- ✅ `get_new_rec_ids()` - 신규 rec_idx 목록

---

## 📝 권장 작업 순서

### 1단계: main.py 레거시 표시 (즉시)
```bash
cd crawler
mv main.py main_legacy.py
```

주석 추가:
```python
"""
⚠️ LEGACY FILE - 사용하지 않음

이 파일은 일괄 처리 방식의 크롤러입니다.
현재는 main_streaming.py (스트리밍 방식)를 사용합니다.

메모리 문제로 인해 deprecated 되었습니다.
백업/참조용으로만 유지됩니다.
"""
```

### 2단계: Dead Code 주석 처리 (1주 후)

각 Dead Code에 `@deprecated` 주석 추가:

```python
# s3_uploader.py
def upload_pair(self, ...):
    """
    ⚠️ DEPRECATED - 사용하지 않음

    대체: upload_data() 사용
    제거 예정: 2025-11-01
    """
    ...
```

### 3단계: Dead Code 제거 (2주 운영 후)

```bash
# s3_uploader.py에서 제거:
# - upload_pair()
# - upload_pair_by_deadline()
# - upload_data_by_deadline()
# - list_active_rec_ids()

# saramin_crawler.py에서 제거:
# - load_existing_rec_ids()
# - existing_rec_ids
# - get_skipped_results()

# main_legacy.py 제거
```

---

## 🔍 환경변수 정리

### 현재 사용 중인 환경변수

| 변수명 | 사용 위치 | 기본값 | 설명 |
|-------|----------|-------|------|
| `AWS_ACCESS_KEY_ID` | config.py | - | AWS 인증 |
| `AWS_SECRET_ACCESS_KEY` | config.py | - | AWS 인증 |
| `AWS_DEFAULT_REGION` | config.py | `ap-northeast-2` | AWS 리전 |
| `S3_BUCKET_NAME` | config.py | `career-hi` | S3 버킷명 |
| `CRAWL_MAX_PAGES` | config.py | `3` | 최대 크롤링 페이지 수 |
| `CRAWL_MODE` | config.py | `daily` | 크롤링 모드 |
| `INGESTION_SERVICE_URL` | config.py | `http://localhost:5002` | Ingestion API URL |
| **`CRAWL_SCHEDULE_HOUR`** | **scheduler.py** | **`9`** | **스케줄 시간** |
| **`CRAWL_SCHEDULE_MINUTE`** | **scheduler.py** | **`0`** | **스케줄 분** |
| `CRAWL_RUN_IMMEDIATELY` | scheduler.py | `false` | 즉시 실행 여부 |

### 제거된 환경변수

| 변수명 | 이전 위치 | 상태 |
|-------|----------|------|
| ~~`CRAWL_SCHEDULE_HOUR`~~ | ~~config.py~~ | ✅ 제거됨 (scheduler.py에서만 사용) |

---

## 📌 주요 변경 사항 요약

### config.py
```diff
- CRAWL_SCHEDULE_HOUR = int(os.getenv("CRAWL_SCHEDULE_HOUR", "2"))
+ # 주의: CRAWL_SCHEDULE_HOUR/MINUTE은 scheduler.py에서 직접 환경변수를 읽음
  CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "3"))
```

### scheduler.py
```diff
- from main import main as run_crawler
+ from main_streaming import main as run_crawler
```

### 실행 파일
- ✅ **main_streaming.py**: 활성 (스케줄러 사용)
- ⚠️ **main.py**: 레거시 (보관용)

---

## ✅ 체크리스트

- [x] config.py의 CRAWL_SCHEDULE_HOUR 제거
- [x] scheduler.py의 import 경로 변경 (main_streaming.py)
- [x] Dead Code 목록 작성
- [x] 제거 권장 사항 문서화
- [ ] main.py를 main_legacy.py로 이름 변경
- [ ] Dead Code에 @deprecated 주석 추가
- [ ] 2주 운영 후 Dead Code 제거

---

## 🎯 결론

**완료된 작업**:
- ✅ config.py 정리 (CRAWL_SCHEDULE_HOUR 제거)
- ✅ Dead Code 식별 및 문서화
- ✅ 제거 권장 사항 및 순서 정의

**총 Dead Code**: ~480줄 (제거 가능)

**다음 단계**:
1. main.py → main_legacy.py 이름 변경
2. 스트리밍 모드 안정성 확인 (2주)
3. Dead Code 최종 제거

이제 크롤러 코드가 더 명확하고 유지보수하기 쉬워졌습니다!
