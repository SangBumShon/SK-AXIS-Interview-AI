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
    질문은 QUESTION_STORE에 저장합니다.
    """
    questions_per_interviewee = {}

    for interviewee_id in req.interviewee_ids:
        questions = await fetch_interviewee_questions(interviewee_id)
        if not questions:
            raise HTTPException(status_code=404, detail=f"{interviewee_id} 질문 없음")
        
        questions_per_interviewee[str(interviewee_id)] = questions
        # ✅ 질문 저장소에 등록
        QUESTION_STORE[interviewee_id] = questions
    
    return StartInterviewResponse(
        questions_per_interviewee=questions_per_interviewee
    )

@router.post("/end", response_model=EndInterviewResponse)
async def end_interview(req: EndInterviewRequest):
    """
    인터뷰 종료: 각 면접자의 비언어적 데이터를 처리하고 최종 보고서를 생성합니다.
    
    - interview_id: 면접 세션 ID
    - data: 면접자별 비언어적 데이터 (Dict[str, NonverbalData])
    """
    try:
        # interview_id 저장
        interview_id = req.interview_id
        
        # req.data의 각 면접자 ID와 비언어적 데이터를 처리
        for interviewee_id, nonverbal_data in req.data.items():
            # 문자열 ID를 정수로 변환
            interviewee_id_int = int(interviewee_id)
            
            # 상태 확인
            state = INTERVIEW_STATE_STORE.get(interviewee_id_int)
            if not state:
                raise HTTPException(
                    status_code=404, 
                    detail=f"면접자 ID {interviewee_id}의 상태 정보가 없습니다."
                )

            # interview_id를 상태에 추가
            state["interview_id"] = interview_id
            
            # 마지막 오디오 세그먼트 처리
            await process_last_audio_segment(state)
            
            # 비언어적 데이터 저장
            save_nonverbal_counts(state, nonverbal_data)

            # 최종 보고서 생성
            await final_report_flow_executor(state)

        return EndInterviewResponse(result="done", report_ready=True)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"잘못된 요청 형식: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
