# app/schemas/nonverbal.py
from pydantic import BaseModel
from typing import Dict

class Posture(BaseModel):
    upright: int
    leaning: int
    slouching: int

class FacialExpression(BaseModel):
    smile: int
    neutral: int
    frown: int
    angry: int

class NonverbalData(BaseModel):
    interviewee_id: str
    posture: Posture
    facial_expression: FacialExpression
    gaze: int
    gesture: int

class NonverbalScore(BaseModel):
    interviewee_id: str
    posture_score: float
    facial_score: float
    overall_score: float
    feedback: Dict[str, str]
    detailed_analysis: str
    posture_raw_llm_response: str
    facial_raw_llm_response: str
    overall_raw_llm_response: str