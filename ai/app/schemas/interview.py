# app/schemas/interview.py

from pydantic import BaseModel
from typing import List, Dict, Literal

class Question(BaseModel):
    question_id: int
    type: Literal["공통질문", "개별질문"]
    content: str

class StartInterviewRequest(BaseModel):
    interviewee_ids: List[int]
    interviewer_ids: List[int]

class StartInterviewResponse(BaseModel):
    questions_per_interviewee: Dict[int, List[Question]]
    status: str

class EndInterviewRequest(BaseModel):
    interview_id: int

class EndInterviewResponse(BaseModel):
    result: str
    report_ready: bool
