# 텍스트 정제
import re


def clean_text(text: str) -> str:
    """
    채용공고에서 불필요한 문구를 정규식을 이용해 제거합니다.

    Args:
        text (str): 원본 텍스트

    Returns:
        str: 전처리된 텍스트
    """
    # 제거할 정규식 패턴 리스트
    patterns_to_remove = [
        r"최저임금계산에 대한 알림하단에 명시된 급여, 근무 내용 등이 최저임금에[\s\n]*",  # 최저임금 관련 문장
        r"조회수\s?\d+",  # 조회수 123
        r"홈페이지접속\s?\d*",  # 홈페이지접속 22
        r"공유하기",  # 공유하기
        r"본\s?채용정보에\s?불법.*?신고해주세요!?",  # 신고 문구
        r"자사양식.*?다운수\s?\d*",
    ]
    # 정규식 패턴을 이용해 텍스트에서 제거
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    # 불필요한 공백 제거

    return text
