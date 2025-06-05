# app/services/interview/interview_state.py

# 현재 면접 중인 지원자 ID 목록
CURRENT_INTERVIEWEE_IDS: set[int] = set()

# STT 스트리밍 상태
IS_STREAMING: bool = False 
REPRESENTATIVE_QUESTIONS: list[dict[str, str]] = []
