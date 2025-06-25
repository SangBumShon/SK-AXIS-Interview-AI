# app/routers/interview_router.py

from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv

from app.schemas.interview import (
    StartInterviewRequest,
    StartInterviewResponse,
    EndInterviewRequest,
    EndInterviewResponse,
    Question
)
from app.services.internal_client import fetch_interviewee_questions
from app.services.pipeline.graph_pipeline import final_report_flow_executor
from app.schemas.state import InterviewState
from app.state.store import INTERVIEW_STATE_STORE  # 전역 메모리 스토어
from app.services.interview.nonverbal_service import evaluate
from app.state.question_store import QUESTION_STORE

from app.services.interview.interview_end_processing_service import (
    process_last_audio_segment,
    save_nonverbal_counts
)

# 환경 변수 로드
load_dotenv()

router = APIRouter(prefix="/interview", tags=["Interview"])

RESULT_DIR = os.getenv("RESULT_DIR", "./result")
os.makedirs(RESULT_DIR, exist_ok=True)


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(req: StartInterviewRequest):
    """
    인터뷰 시작: 각 지원자의 질문 목록을 로드해 반환하고,
    인터뷰 state를 초기화합니다.
    """
    questions_per_interviewee = {}

    for interviewee_id in req.interviewee_ids:
        # 1) 질문 조회
        questions = await fetch_interviewee_questions(interviewee_id)
        if not questions:
            raise HTTPException(status_code=404, detail=f"{interviewee_id} 질문 없음")
        questions_per_interviewee[str(interviewee_id)] = questions
        QUESTION_STORE[interviewee_id] = questions

    return StartInterviewResponse(
        questions_per_interviewee=questions_per_interviewee
    )


@router.post("/end", response_model=EndInterviewResponse)
async def end_interview(req: EndInterviewRequest):
    try:
        for iv in req.interviewees:
            state: InterviewState = INTERVIEW_STATE_STORE.get(iv.interviewee_id)
            if not state:
                raise HTTPException(status_code=404, detail=f"{iv.interviewee_id} 상태 없음")

            # --- (1) 마지막 녹음 파일 처리 ---
            # audio_path에 값이 남아 있으면 STT→Rewrite 파이프라인 실행
            if state.get("audio_path"):
                await interview_flow_executor(state)
                # 처리 후 중복 방지를 위해 비워줍니다
                state["audio_path"] = ""

            # --- (2) 비언어적 세부 카운트 저장 ---
            state["nonverbal_counts"] = {
                "posture": iv.posture.dict(),
                "expression": iv.facial_expression.dict(),
                "gaze": iv.gaze,
                "gesture": iv.gesture,
            }

            # --- (3) 최종 리포트(비언어 포함) 생성 ---
            await final_report_flow_executor(state)

        return EndInterviewResponse(result="done", report_ready=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))