"""
SK AXIS AI 면접 비언어적 요소 분석 스키마

이 파일은 면접 중 수집되는 비언어적 데이터의 구조를 정의하는 Pydantic 스키마입니다.
주요 기능:
- 자세(Posture) 분석 데이터 모델
- 표정(FacialExpression) 분석 데이터 모델
- 비언어적 종합 데이터 모델
- 평가 결과 점수 모델

데이터 수집 방식:
- 프론트엔드에서 실시간 수집
- 웹캠 기반 얼굴/자세 인식
- 면접 종료 시 AI 평가 시스템으로 전달

평가 활용:
- 표정 데이터 → GPT-4o-mini 분석 → 15점 만점 환산
- 자세, 시선, 제스처 데이터 → 종합 평가
- 최종 점수의 10% 비중 (비언어적 요소)
"""

# app/schemas/nonverbal.py
from pydantic import BaseModel
from typing import Dict

# ──────────────── 🧍 자세 분석 ────────────────

class Posture(BaseModel):
    """
    자세 분석 데이터 모델
    
    Attributes:
        upright (int): 바른 자세 유지 횟수
        leaning (int): 기대어 앉은 횟수
        slouching (int): 구부정한 자세 횟수
        
    Note:
        - 면접 중 자세 변화 추적
        - 각 자세별 지속 시간 또는 빈도 기록
        - AI 평가 시 자신감 및 집중도 판단 지표
    """
    upright: int
    leaning: int
    slouching: int

# ──────────────── 😊 표정 분석 ────────────────

class FacialExpression(BaseModel):
    """
    표정 분석 데이터 모델
    
    Attributes:
        smile (int): 웃음 표정 횟수
        neutral (int): 무표정 횟수
        frown (int): 찡그림 표정 횟수
        angry (int): 화난 표정 횟수
        
    Note:
        - 면접 중 표정 변화 실시간 감지
        - 적절한 웃음과 표정 변화는 긍정적 평가
        - 과도한 무표정이나 부정적 표정은 감점 요소
        - GPT-4o-mini로 패턴 분석 후 0.0~1.0 점수 산출
    """
    smile: int
    neutral: int
    frown: int
    angry: int

# ──────────────── 🎭 종합 비언어적 데이터 ────────────────

class NonverbalData(BaseModel):
    """
    면접자별 비언어적 분석 종합 데이터 모델
    
    Attributes:
        interviewee_id (int): 면접자 고유 ID
        posture (Posture): 자세 분석 데이터
        facial_expression (FacialExpression): 표정 분석 데이터
        gaze (int): 시선 처리 관련 데이터
        gesture (int): 손동작/제스처 관련 데이터
        
    Note:
        - 면접 전체 기간 동안 수집된 데이터 통합
        - 면접 종료 시 EndInterviewRequest에 포함
        - AI 평가 파이프라인의 입력 데이터로 활용
    """
    interviewee_id: int
    posture: Posture
    facial_expression: FacialExpression
    gaze: int
    gesture: int

# ──────────────── 📊 평가 결과 ────────────────

class NonverbalScore(BaseModel):
    """
    비언어적 요소 평가 결과 모델
    
    Attributes:
        interviewee_id (int): 면접자 고유 ID
        posture_score (float): 자세 평가 점수 (0.0~1.0)
        facial_score (float): 표정 평가 점수 (0.0~1.0)
        overall_score (float): 종합 비언어적 점수 (0.0~1.0)
        feedback (Dict[str, str]): 영역별 피드백 메시지
        detailed_analysis (str): 상세 분석 내용
        posture_raw_llm_response (str): 자세 분석 원본 LLM 응답
        facial_raw_llm_response (str): 표정 분석 원본 LLM 응답
        overall_raw_llm_response (str): 종합 분석 원본 LLM 응답
        
    Note:
        - 현재 표정 평가만 활성화 (facial_score)
        - overall_score는 15점 만점으로 환산하여 최종 점수에 반영
        - 상세 분석 및 피드백으로 개선 방향 제시
        - LLM 원본 응답 보관으로 투명성 확보
    """
    interviewee_id: int
    posture_score: float
    facial_score: float
    overall_score: float
    feedback: Dict[str, str]
    detailed_analysis: str
    posture_raw_llm_response: str
    facial_raw_llm_response: str
    overall_raw_llm_response: str