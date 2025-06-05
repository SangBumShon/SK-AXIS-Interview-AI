from pydantic import BaseModel
from typing import List, Dict, Literal

class StartInterviewRequest(BaseModel):
    interviewee_ids: List[int]
    interviewer_ids: List[int]

class Question(BaseModel):
    question_id: int
    type: Literal["공통질문", "개별질문"]
    content: str

class StartInterviewResponse(BaseModel):
    questions_per_interviewee: Dict[str, List[Question]]
    status: str

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

class QuestionsResponse(BaseModel):
    questions: List[Question]

class MultipleIntervieweesRequest(BaseModel):
    """
    POST /internal/interviewees/questions 요청 바디 스키마
    {
      "interviewee_ids": [101, 102, 103]
    }
    """
    interviewee_ids: List[int]


class MultipleIntervieweesResponse(BaseModel):
    """
    POST /internal/interviewees/questions 응답 바디 스키마
    {
      "questions_per_interviewee": {
        "101": [ Question, Question, ... ],
        "102": [ ... ],
        "103": [ ... ]
      }
    }
    """
    questions_per_interviewee: Dict[str, List[Question]]