# 사람인 크롤러 테스트 가이드

## 📋 사전 준비

### 1. Python 환경
```bash
# Python 3.11 이상 권장
python --version
```

### 2. 의존성 설치
```bash
cd crawler
pip install -r requirements.txt
```

### 3. Chrome 브라우저 설치 확인
- Chrome 브라우저가 설치되어 있어야 합니다
- ChromeDriver는 `webdriver-manager`가 자동으로 설치합니다

---

## 🚀 테스트 실행

### 기본 실행 (3개 공고 수집)
```bash
python test_crawler.py
```

### 실행 결과
```
crawler/
└── test_output/
    ├── pdf/
    │   ├── 49421173.pdf
    │   ├── 49421174.pdf
    │   └── 49421175.pdf
    └── metadata/
        ├── 49421173.json
        ├── 49421174.json
        └── 49421175.json
```

---

## 📊 출력 예시

### 성공 케이스
```
✅ Chrome 드라이버 생성 중...
✅ 드라이버 생성 완료
📄 페이지 1 접속 중...
✅ 페이지 로드 완료

🔍 채용공고 링크 추출 중...
✅ 38개의 채용공고 링크 발견
📋 수집 대상: 3개 공고

────────────────────────────────────────────────────────────
📌 [1/3] rec_idx: 49421173
────────────────────────────────────────────────────────────
🌐 상세 페이지 접속 중...
✅ 페이지 로드 완료
📝 제목: [삼성전자] 백엔드 개발자 신입 채용
📅 시작일: 2025.01.15
⏰ 마감일: 2025.02.28
🧹 불필요한 요소 제거 중...
💾 PDF 저장 중: test_output/pdf/49421173.pdf
✅ PDF 저장 완료
💾 메타데이터 저장 중: test_output/metadata/49421173.json
✅ 메타데이터 저장 완료

🎉 [1/3] 수집 완료!
```

### 실패 케이스
```
❌ 채용공고 링크를 찾을 수 없습니다.
   사람인 사이트 구조가 변경되었을 수 있습니다.
```

---

## 🔍 문제 해결

### 1. ChromeDriver 오류
```bash
# webdriver-manager 캐시 삭제
rm -rf ~/.wdm

# 다시 실행
python test_crawler.py
```

### 2. Selenium 오류
```bash
# Selenium 재설치
pip uninstall selenium
pip install selenium==4.16.0
```

### 3. 사이트 구조 변경
- CSS Selector가 변경되었을 가능성
- 사람인 사이트 직접 확인 필요
- 개발자 도구(F12)로 요소 검사

### 4. 네트워크 오류
- 방화벽 확인
- VPN 연결 확인
- 사람인 사이트 접속 가능 여부 확인

---

## 📝 파일 구조 설명

### test_crawler.py
- **목적**: 크롤링 로직 검증
- **특징**:
  - 1페이지만 크롤링
  - 최대 3개 공고만 수집
  - 상세한 로그 출력
  - 에러 발생 시 스택 트레이스 출력

### 출력 파일

#### PDF (test_output/pdf/{rec_idx}.pdf)
- 채용공고 상세 내용
- 불필요한 광고/추천 섹션 제거됨
- 인쇄 가능한 깨끗한 레이아웃

#### JSON (test_output/metadata/{rec_idx}.json)
```json
{
  "rec_idx": "49421173",
  "post_title": "[삼성전자] 백엔드 개발자 신입 채용",
  "start_date": "2025.01.15",
  "deadline": "2025.02.28",
  "detail_url": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=49421173",
  "crawling_time": "2025-01-20 14:30:45"
}
```

---

## ✅ 테스트 체크리스트

- [ ] Python 3.11 이상 설치됨
- [ ] Chrome 브라우저 설치됨
- [ ] `pip install -r requirements.txt` 실행 완료
- [ ] `python test_crawler.py` 실행 성공
- [ ] `test_output/pdf/` 디렉토리에 PDF 파일 생성됨
- [ ] `test_output/metadata/` 디렉토리에 JSON 파일 생성됨
- [ ] PDF 파일 열어서 내용 확인 가능
- [ ] JSON 파일에 올바른 메타데이터 포함

---

## 🎯 다음 단계

테스트 성공 후:
1. ✅ **S3 업로드 기능 구현**
2. ✅ **Ingestion API 증분 업데이트 구현**
3. ✅ **크롤러 ↔ Ingestion 통합**
4. ✅ **APScheduler 스케줄링 추가**
5. ✅ **Docker 컨테이너화**

---

## 📞 문제 발생 시

에러 메시지와 함께 다음 정보를 제공해주세요:
- Python 버전
- Chrome 버전
- OS 정보
- 에러 스택 트레이스
- `test_output/` 디렉토리 내용
