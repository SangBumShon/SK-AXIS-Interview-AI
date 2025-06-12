from typing import TypedDict, List, Dict, Any

class InterviewState(TypedDict, total=False):
    interviewee_id: int
    audio_path: str
    stt: dict
    rewrite: dict
    evaluation: dict
    report: dict
    decision_log: list
    nonverbal_counts: Dict[str, int]