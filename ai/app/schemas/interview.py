# app/schemas/interview.py
from pydantic import BaseModel
from typing import List, Dict, Literal
from app.schemas.nonverbal import Posture, FacialExpression

class StartInterviewRequest(BaseModel):
    interviewee_ids: List[int]
    interview_ids: List[int]

class Question(BaseModel):
    question_id: int
    type: str
    content: str

class StartInterviewResponse(BaseModel):
    questions_per_interviewee: Dict[str, List[Question]]

class NonverbalData(BaseModel):
    posture: Posture
    facial_expression: FacialExpression
    gaze: int
    gesture: int
    timestamp: int

class EndInterviewRequest(BaseModel):
    interview_id: int
    data: Dict[str, NonverbalData]

class EndInterviewResponse(BaseModel):
    result: str
    report_ready: bool

class QuestionsResponse(BaseModel):
    questions: List[Question]

class MultipleIntervieweesRequest(BaseModel):
    interviewee_ids: List[int]

class MultipleIntervieweesResponse(BaseModel):
    questions_per_interviewee: Dict[str, List[Question]]

class STTUploadResponse(BaseModel):
    result: str
