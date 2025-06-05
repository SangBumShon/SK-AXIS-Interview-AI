from pydantic import BaseModel
from typing import List, Optional

class NonverbalCounts(BaseModel):
    posture: int
    gaze: int
    expression: int
    gesture: int

class IntervieweeCounts(BaseModel):
    interviewee_id: int
    counts: NonverbalCounts

class EndInterviewRequest(BaseModel):
    interview_id: int
    interviewees: List[IntervieweeCounts]

class EndInterviewResponse(BaseModel):
    result: str
    report_ready: bool