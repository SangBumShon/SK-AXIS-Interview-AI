# app/schemas/nonverbal.py
from pydantic import BaseModel
from typing import Dict

class Posture(BaseModel):
    leg_spread: int
    leg_shake: int
    head_down: int

class FacialExpression(BaseModel):
    smile: int
    neutral: int
    frown: int

class NonverbalData(BaseModel):
    interviewee_id: int
    posture: Posture
    facial_expression: FacialExpression
    gaze: int
    gesture: int

class NonverbalScore(BaseModel):
    interviewee_id: int
    posture_score: float
    facial_score: float
    overall_score: float
    feedback: Dict[str, str]
    detailed_analysis: str
