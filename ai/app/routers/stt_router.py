# app/routers/stt_router.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.schemas.interview import STTUploadResponse
from app.services.pipeline.graph_pipeline import interview_flow_executor
from app.state.store import INTERVIEW_STATE_STORE
from app.state.question_store import QUESTION_STORE
from app.services.interview.stt_service import save_audio_file
from app.services.interview.state_service import create_initial_state

router = APIRouter(prefix="/stt", tags=["STT"])


@router.post("/upload", response_model=STTUploadResponse)
async def upload_stt(
    interviewee_id: int = Form(...),
    audio: UploadFile = File(...),
):
    """답변 단위 음성 파일 업로드 및 STT 파이프라인 실행"""
    try:
        # 1) 오디오 파일 저장
        file_path = await save_audio_file(interviewee_id, audio)
        if not file_path:
            raise HTTPException(status_code=500, detail="파일 저장 실패")

        # 2) 상태 가져오기 또는 새로 초기화
        state = INTERVIEW_STATE_STORE.get(interviewee_id)
        if state is None:
            questions = QUESTION_STORE.get(interviewee_id, [])  # 질문이 없으면 빈 리스트
            state = create_initial_state(interviewee_id, questions, file_path)
        else:
            state["audio_path"] = file_path

        # 3) 파이프라인 실행
        await interview_flow_executor(state)

        # 4) 상태 저장
        INTERVIEW_STATE_STORE[interviewee_id] = state

        return STTUploadResponse(result="OK")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
