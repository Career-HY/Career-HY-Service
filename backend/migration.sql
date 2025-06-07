-- ChatMessage 테이블에 recommended_jobs JSON 컬럼 추가
-- 실행 전에 데이터베이스 백업을 권장합니다.

ALTER TABLE chat_history 
ADD COLUMN recommended_jobs JSON NULL 
COMMENT '추천된 채용공고 목록 (JSON 형태)';

-- 변경사항 확인
DESCRIBE chat_history; 