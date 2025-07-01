from typing import Dict
from app.schemas.state import InterviewState

# 인터뷰 상태를 메모리에 저장하는 전역 스토어
# 키: interviewee_id (예: "person1"), 값: 해당 인터뷰의 상태 객체
INTERVIEW_STATE_STORE: Dict[str, InterviewState] = {}

def debug_dump_state_store():
    print("[DUMP] INTERVIEW_STATE_STORE 전체 상태:")
    for k, v in INTERVIEW_STATE_STORE.items():
        print(f"  interviewee_id={k}, type={type(v)}, value={v}")