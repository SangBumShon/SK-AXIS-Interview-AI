from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv

from app.schemas.interview import (
    StartInterviewRequest, StartInterviewResponse,
    EndInterviewRequest, EndInterviewResponse
)
from app.services.pipeline_service import run_pipeline
from app.services.internal_client import fetch_interviewee_questions

# 환경 변수 로드
load_dotenv()

router = APIRouter(prefix="/interview", tags=["Interview"])

# 결과 저장 경로 설정
RESULT_DIR = os.getenv("RESULT_DIR", "./result")
os.makedirs(RESULT_DIR, exist_ok=True)

@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(req: StartInterviewRequest):
    questions_per_interviewee = {}
    for interviewee_id in req.interviewee_ids:
        questions = await fetch_interviewee_questions(interviewee_id)
        if not questions:
            raise HTTPException(status_code=404, detail=f"{interviewee_id} 질문 없음")
        questions_per_interviewee[str(interviewee_id)] = questions

    return StartInterviewResponse(
        questions_per_interviewee=questions_per_interviewee,
        status="started"
    )

@router.post("/end", response_model=EndInterviewResponse)
async def end_interview(req: EndInterviewRequest):
    try:
        json_input_path = f"./data/interview_{req.interview_id}_stt.json"
        radar_chart_path = os.path.join(RESULT_DIR, f"interview_{req.interview_id}_chart.png")
        pdf_output_path = os.path.join(RESULT_DIR, f"interview_{req.interview_id}_report.pdf")

        if not os.path.exists(json_input_path):
            raise FileNotFoundError(f"STT JSON 파일이 존재하지 않습니다: {json_input_path}")

        # 비언어적 요소 로그 출력 (또는 저장 처리)
        for iv in req.interviewees:
            print(f"[비언어적 요소] ID: {iv.interviewee_id}, Counts: {iv.counts.dict()}")

        # 분석 파이프라인 실행
        await run_pipeline(
            input_json=json_input_path,
            chart_path=radar_chart_path,
            output_pdf=pdf_output_path
        )

        return EndInterviewResponse(result="done", report_ready=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
