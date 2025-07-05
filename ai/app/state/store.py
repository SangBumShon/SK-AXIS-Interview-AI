from typing import Dict
from app.schemas.state import InterviewState

# 인터뷰 상태를 메모리에 저장하는 전역 스토어
# 키: interviewee_id (예: "person1"), 값: 해당 인터뷰의 상태 객체
INTERVIEW_STATE_STORE: Dict[str, InterviewState] = {}

