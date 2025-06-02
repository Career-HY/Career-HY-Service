"""
JSON 데이터 구조 확인용 디버깅 스크립트
"""
from s3_loader import S3DataLoader
import json

def debug_json_structure():
    """JSON 데이터의 실제 구조를 확인합니다."""
    loader = S3DataLoader()
    
    try:
        # S3에서 JSON 파일 로드
        json_data = loader.load_json_files()
        
        if json_data:
            print(f"📊 총 {len(json_data)}개의 JSON 레코드 로드됨")
            
            # 첫 번째 JSON 객체 구조 확인
            print("\n🔍 첫 번째 JSON 객체 구조:")
            first_item = json_data[0]
            print(json.dumps(first_item, indent=2, ensure_ascii=False))
            
            print("\n📋 모든 필드명 목록:")
            if isinstance(first_item, dict):
                for key in first_item.keys():
                    print(f"  - {key}: {type(first_item[key])}")
            
            # 제목 관련 필드 찾기
            print("\n🔎 제목 관련 필드:")
            title_fields = [k for k in first_item.keys() if 'title' in k.lower() or '제목' in str(first_item.get(k, ''))]
            for field in title_fields:
                print(f"  - {field}: {first_item.get(field)}")
            
            # URL 관련 필드 찾기
            print("\n🔗 URL 관련 필드:")
            url_fields = [k for k in first_item.keys() if 'url' in k.lower() or 'link' in k.lower()]
            for field in url_fields:
                print(f"  - {field}: {first_item.get(field)}")
            
            # 날짜 관련 필드 찾기
            print("\n📅 날짜 관련 필드:")
            date_fields = [k for k in first_item.keys() if any(word in k.lower() for word in ['date', 'deadline', 'close', 'end', '마감', '날짜'])]
            for field in date_fields:
                print(f"  - {field}: {first_item.get(field)}")
                
        else:
            print("❌ JSON 데이터가 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    debug_json_structure() 