# app/routers/internal_router.py

from fastapi import APIRouter, HTTPException
from typing import List, Dict

from app.services.internal_client import fetch_interviewee_questions
from app.schemas.interview import Question, MultipleIntervieweesRequest, MultipleIntervieweesResponse

router = APIRouter(tags=["Internal"])


@router.post(
    "/internal/interviewees/questions",
    response_model=MultipleIntervieweesResponse,
    summary="다중 지원자 질문 5개 조회 (FastAPI to Spring Boot)",
)
async def get_multiple_interviewee_questions(req: MultipleIntervieweesRequest):
    """
    Spring Boot ↔ FastAPI Internal API:
    - Body로 받은 여러 interviewee_id 리스트를 Spring Boot로 전달하여,
      각 지원자별 질문 5개를 한 번에 받아옵니다.
    - 현재 예시에서는 Spring Boot에 '한 번에 다중 조회' API가 없다고 가정하고,
      내부적으로 fetch_interviewee_questions()를 ID마다 반복 호출합니다.
    """
    questions_per_interviewee: Dict[str, List[Question]] = {}

    for interviewee_id in req.interviewee_ids:
        raw_questions = await fetch_interviewee_questions(interviewee_id)
        if not raw_questions:
            # 하나라도 실패하면 404 반환
            raise HTTPException(
                status_code=404,
                detail=f"지원자 {interviewee_id}의 질문을 찾을 수 없습니다."
            )

        return MultipleIntervieweesResponse(questions_per_interviewee=questions_per_interviewee)