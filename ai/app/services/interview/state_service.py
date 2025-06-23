from typing import List, Dict, Any

def create_initial_state(interviewee_id: int, questions: List[Dict], file_path: str) -> Dict[str, Any]:
    return {
        "interviewee_id": interviewee_id,
        "questions": questions,
        "audio_path": file_path,
        "stt": {"done": False, "segments": []},
        "rewrite": {"done": False, "items": []},
        "evaluation": {"done": False, "results": {}},
        "report": {"pdf_path": ""},
        "decision_log": [],
    }