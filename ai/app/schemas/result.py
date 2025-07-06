"""
SK AXIS AI 면접 평가 결과 스키마

이 파일은 면접 평가 결과 조회 API의 응답 모델을 정의하는 Pydantic 스키마입니다.
주요 기능:
- 평가 상태 조회 응답 모델 (PENDING/DONE)
- 최종 평가 결과 응답 모델 (점수 및 상세 분석)
- 언어적/비언어적 평가 분리 모델
- 다중 면접자 결과 통합 모델

API 엔드포인트 연동:
- /api/v1/results/statuses → ResultStatusResponse
- /api/v1/results/final → FinalResultResponse
- 프론트엔드 폴링 → 실시간 상태 확인

데이터 변환 처리:
- float → int 변환 (total_score)
- list → string 변환 (verbal_reason)
- 100점 만점 환산 점수 제공
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional

# ──────────────── 📊 평가 상태 조회 ────────────────

class ResultStatusResponse(BaseModel):
    """
    면접자 한 명의 평가 상태 응답 모델
    
    Attributes:
        interviewee_id (int): 면접자 고유 ID
        status (str): 평가 상태 ("PENDING" 또는 "DONE")
        score (Optional[int]): 총점 (100점 만점, DONE 시에만 제공)
        
    Note:
        - 프론트엔드에서 주기적으로 폴링하여 상태 확인
        - PENDING: 평가 진행 중 (STT, 리라이팅, 평가 단계)
        - DONE: 평가 완료 (score_summary_agent 완료 후)
        - score는 summary.total_score에서 추출 (round 처리)
    """
    interviewee_id: int
    status: str = Field(..., description="평가 상태 (PENDING 또는 DONE)")
    score: Optional[int] = Field(None, description="총점 (100점 만점)")

# ResultStatusListResponse는 ResultStatusResponse의 리스트
ResultStatusListResponse = List[ResultStatusResponse]

# ──────────────── 📝 세부 평가 결과 ────────────────

class LanguageEvaluation(BaseModel):
    """
    언어적 평가 결과 모델
    
    Attributes:
        score (int): 언어적 평가 점수 
        reason (str): 평가 이유 및 상세 분석
        
    Note:
        - 8개 키워드 × 3개 기준 = 24개 항목 평가 결과 통합
        - 인성적 요소 + 기술/도메인 점수 합계
        - GPT 분석 기반 상세한 평가 사유 제공
    """
    score: int = Field(..., description="언어적 평가 점수 (1-5)")
    reason: str = Field(..., description="평가 이유")

class NonverbalEvaluation(BaseModel):
    """
    비언어적 평가 결과 모델
    
    Attributes:
        score (int): 비언어적 평가 점수 
        reason (str): 평가 이유 및 상세 분석
        
    Note:
        - 표정 분석 결과 기반 (smile, neutral, frown, angry)
        - GPT-4o-mini로 패턴 분석 후 점수 산출
        - 최종 점수의 10% 비중
    """
    score: int = Field(..., description="비언어적 평가 점수 (1-5)")
    reason: str = Field(..., description="평가 이유")

# ──────────────── 🏆 최종 결과 모델 ────────────────

class FinalResultResponse(BaseModel):
    """
    면접자 한 명의 최종 평가 결과 응답 모델
    
    Attributes:
        interviewee_id (int): 면접자 고유 ID
        competencies (Dict[str, int]): 역량별 점수 (키워드별 총점)
        language (LanguageEvaluation): 언어적 평가 결과
        nonverbal (NonverbalEvaluation): 비언어적 평가 결과
        
    Note:
        - competencies: 8개 키워드별 15점 만점 점수
          (SUPEX, VWBE, Passionate, Proactive, Professional, People, 기술/직무, 도메인 전문성)
        - language: 언어적 요소 통합 점수 및 분석
        - nonverbal: 비언어적 요소 점수 및 분석
    """
    interviewee_id: int
    competencies: Dict[str, int] = Field(..., description="역량별 점수")
    language: LanguageEvaluation
    nonverbal: NonverbalEvaluation

class FinalResultListResponse(BaseModel):
    """
    다수 면접자의 최종 평가 결과 응답 모델
    
    Attributes:
        weights (Dict[str, str]): 평가 항목별 비중 (문자열 퍼센트 표현)
        results (List[FinalResultResponse]): 면접자별 평가 결과 리스트
        
    Note:
        - weights: 고정 비중 정보
          {"인성적 요소": "45%", "직무·도메인": "45%", "비언어적 요소": "10%"}
        - results: 각 면접자의 상세 평가 결과
        - 다중 면접자 비교 분석 지원
    """
    weights: Dict[str, str] = Field(..., description="평가 항목별 비중 (문자열 퍼센트 표현)")
    results: List[FinalResultResponse] = Field(..., description="면접자별 평가 결과 리스트")
