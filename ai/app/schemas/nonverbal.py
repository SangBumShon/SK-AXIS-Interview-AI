from pydantic import BaseModel
from typing import List, Optional, Dict 

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

class Posture(BaseModel):
    leg_spread: int 
    leg_shake: int
    head_down: int

class FacialExpression(BaseModel):
    smile: int
    neutral: int
    embarrassed: int
    tearful: int
    frown: int

class NonverbalData(BaseModel):
    interviewee_id: int            # "person1", "person2" 등 문자열 ID
    is_speaking: bool              # 화자인지 여부 (true/false)
    posture: Posture               # 자세 정보
    facial_expression: FacialExpression  # 표정 정보

class NonverbalScore(BaseModel):
    posture_score: float  # 0.0 ~ 1.0
    facial_score: float   # 0.0 ~ 1.0
    overall_score: float  # 0.0 ~ 1.0
    feedback: Dict[str, str]  # 각 요소별 피드백
    detailed_analysis: str    # AI의 상세 분석