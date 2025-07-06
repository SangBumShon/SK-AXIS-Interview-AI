"""
SK AXIS AI 면접 시스템 데이터 스키마

이 파일은 면접 관련 API의 요청/응답 모델을 정의하는 Pydantic 스키마입니다.
주요 기능:
- 면접 시작/종료 요청/응답 모델
- STT 업로드 응답 모델
- 질문 및 비언어적 데이터 모델
- 다중 면접자 처리 모델

데이터 흐름:
1. StartInterviewRequest → 면접 시작
2. STTUploadResponse → 음성 업로드 응답
3. EndInterviewRequest → 면접 종료 (비언어적 데이터 포함)
4. QuestionsResponse → 질문 목록 조회

스키마 설계 원칙:
- 타입 안전성 보장 (Pydantic 기반)
- 명확한 필드 구조 정의
- API 문서 자동 생성 지원
"""

# app/schemas/interview.py
from pydantic import BaseModel
from typing import List, Dict, Literal
from app.schemas.nonverbal import Posture, FacialExpression

# ──────────────── 📝 질문 관련 ────────────────

class Question(BaseModel):
    """
    면접 질문 모델
    
    Attributes:
        question_id (int): 질문 고유 ID
        type (str): 질문 유형 (예: "기술", "인성")
        content (str): 질문 내용
        
    Note:
        - SpringBoot에서 전달받는 질문 구조
        - 면접자별로 다른 질문 세트 가능
    """
    question_id: int
    type: str
    content: str

# ──────────────── 🚀 면접 시작 관련 ────────────────

class StartInterviewRequest(BaseModel):
    """
    면접 시작 요청 모델
    
    Attributes:
        interviewee_ids (List[int]): 면접자 ID 목록
        interview_ids (List[int]): 면접 세션 ID 목록
        
    Note:
        - 다중 면접자 동시 처리 지원
        - SpringBoot 백엔드와 연동
    """
    interviewee_ids: List[int]
    interview_ids: List[int]

class StartInterviewResponse(BaseModel):
    """
    면접 시작 응답 모델
    
    Attributes:
        questions_per_interviewee (Dict[str, List[Question]]): 면접자별 질문 목록
        
    Note:
        - 키: 면접자 ID (문자열)
        - 값: 해당 면접자의 질문 목록
    """
    questions_per_interviewee: Dict[str, List[Question]]

class QuestionsResponse(BaseModel):
    """
    질문 목록 조회 응답 모델
    
    Attributes:
        questions (List[Question]): 질문 목록
        
    Note:
        - 단일 면접자용 질문 조회
        - 면접 진행 중 질문 확인용
    """
    questions: List[Question]

# ──────────────── 🎭 비언어적 데이터 관련 ────────────────

class NonverbalData(BaseModel):
    """
    비언어적 분석 데이터 모델
    
    Attributes:
        posture (Posture): 자세 분석 데이터
        facial_expression (FacialExpression): 표정 분석 데이터
        gaze (int): 시선 처리 횟수
        gesture (int): 제스처 횟수
        timestamp (int): 데이터 수집 시점
        
    Note:
        - 프론트엔드에서 실시간 수집
        - 면접 종료 시 일괄 전송
        - AI 평가에 활용
    """
    posture: Posture
    facial_expression: FacialExpression
    gaze: int
    gesture: int
    timestamp: int

# ──────────────── 🏁 면접 종료 관련 ────────────────

class EndInterviewRequest(BaseModel):
    """
    면접 종료 요청 모델
    
    Attributes:
        interview_id (int): 면접 세션 ID
        data (Dict[str, NonverbalData]): 면접자별 비언어적 데이터
        
    Note:
        - 키: 면접자 ID (문자열)
        - 값: 해당 면접자의 비언어적 분석 데이터
        - 면접 완료 시 최종 평가 트리거
    """
    interview_id: int
    data: Dict[str, NonverbalData]

class EndInterviewResponse(BaseModel):
    """
    면접 종료 응답 모델
    
    Attributes:
        result (str): 처리 결과 메시지
        report_ready (bool): 리포트 생성 완료 여부
        
    Note:
        - 면접 종료 처리 상태 반환
        - 리포트 생성 완료 시 다운로드 가능
    """
    result: str
    report_ready: bool

# ──────────────── 👥 다중 면접자 관련 ────────────────

class MultipleIntervieweesRequest(BaseModel):
    """
    다중 면접자 처리 요청 모델
    
    Attributes:
        interviewee_ids (List[int]): 처리할 면접자 ID 목록
        
    Note:
        - 여러 면접자 동시 처리용
        - 질문 배정 및 상태 관리
    """
    interviewee_ids: List[int]

class MultipleIntervieweesResponse(BaseModel):
    """
    다중 면접자 처리 응답 모델
    
    Attributes:
        questions_per_interviewee (Dict[str, List[Question]]): 면접자별 질문 목록
        
    Note:
        - StartInterviewResponse와 동일한 구조
        - 다중 면접자용 질문 배정 결과
    """
    questions_per_interviewee: Dict[str, List[Question]]

# ──────────────── 🎤 STT 관련 ────────────────

class STTUploadResponse(BaseModel):
    """
    STT 음성 업로드 응답 모델
    
    Attributes:
        result (str): 업로드 처리 상태 ("Queued")
        
    Note:
        - 비동기 처리로 즉시 응답
        - 실제 STT 처리는 백그라운드 진행
        - 상태 조회는 별도 API 사용
    """
    result: str
