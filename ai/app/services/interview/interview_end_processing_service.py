# app/services/interview/interview_end_processing_service.py

from app.schemas.state import InterviewState
from app.services.pipeline.graph_pipeline import interview_flow_executor
from app.schemas.interview import NonverbalData

async def process_last_audio_segment(state: InterviewState) -> None:
    if state.get("audio_path"):
        await interview_flow_executor(state)
        state["audio_path"] = ""


def save_nonverbal_counts(state: InterviewState, iv: NonverbalData) -> None:
    state["nonverbal_counts"] = {
        "posture": iv.posture.dict(),
        "expression": iv.facial_expression.dict(),
        "gaze": iv.gaze,
        "gesture": iv.gesture,
    }
