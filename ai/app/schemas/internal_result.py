# app/schemas/internal_result.py

from pydantic import BaseModel
from typing import List

class InterviewResult(BaseModel):
    interviewee_id: int
    score: int
    comment: str
    pdf_path: str
    excel_path: str
    stt_path: str

class InterviewResultBatch(BaseModel):
    interview_id: int
    results: List[InterviewResult]
