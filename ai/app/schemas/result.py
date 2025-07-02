# app/schemas/result.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class ResultStatusResponse(BaseModel):
    """면접자 한 명의 평가 상태 응답 모델"""
    interviewee_id: int
    status: str = Field(..., description="평가 상태 (PENDING 또는 DONE)")
    score: Optional[int] = Field(None, description="총점 (100점 만점)")
    pdf_path: Optional[str] = Field(None, description="PDF 보고서 경로")

# ResultStatusListResponse는 ResultStatusResponse의 리스트
ResultStatusListResponse = List[ResultStatusResponse]

class LanguageEvaluation(BaseModel):
    """언어적 평가 결과"""
    score: int = Field(..., description="언어적 평가 점수 (1-5)")
    reason: str = Field(..., description="평가 이유")

class NonverbalEvaluation(BaseModel):
    """비언어적 평가 결과"""
    score: int = Field(..., description="비언어적 평가 점수 (1-5)")
    reason: str = Field(..., description="평가 이유")

class FinalResultResponse(BaseModel):
    """면접자 한 명의 최종 평가 결과 응답 모델"""
    interviewee_id: int
    competencies: Dict[str, int] = Field(..., description="역량별 점수")
    language: LanguageEvaluation
    nonverbal: NonverbalEvaluation
    pdf_path: str = Field(..., description="PDF 보고서 경로")

class FinalResultListResponse(BaseModel):
    """다수 면접자의 최종 평가 결과 응답 모델"""
    weights: Dict[str, str] = Field(..., description="평가 항목별 비중 (문자열 퍼센트 표현)")
    results: List[FinalResultResponse] = Field(..., description="면접자별 평가 결과 리스트")
