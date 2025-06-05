# app/routers/internal_router.py

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.services.internal_client import fetch_interviewee_questions
from app.schemas.internal_result import InterviewResultBatch

router = APIRouter(tags=["Internal"])


@router.get("/internal/interviewee/{interviewee_id}/questions")
async def get_interviewee_questions(interviewee_id: int):
    """
    Spring Boot → FastAPI: 지원자별 면접 질문 5개 조회
    """
    questions = await fetch_interviewee_questions(interviewee_id)
    if not questions:
        raise HTTPException(status_code=404, detail="해당 지원자 또는 질문 없음")
    return {"questions": questions}


@router.post("/internal/interview/{interview_id}/results")
async def post_interview_results(interview_id: int, batch: InterviewResultBatch):
    """
    FastAPI → Spring Boot: 면접 종료 후, 모든 지원자별 평가 결과 및 파일 경로를 전달
    """
    if batch.interview_id != interview_id:
        raise HTTPException(status_code=400, detail="interview_id 불일치")
    # (실제 Spring Boot 저장 로직이 필요하다면 여기에 구현)
    return {"result": "ok"}
