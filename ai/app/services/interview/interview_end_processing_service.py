"""
SK AXIS AI 면접 종료 처리 서비스

이 파일은 면접 종료 시 마지막 처리 작업을 담당하는 서비스입니다.
주요 기능:
- 마지막 오디오 세그먼트 처리 및 평가 파이프라인 실행
- 비언어적 데이터(표정, 자세, 시선, 제스처) 상태 저장
- 면접 상태 정리 및 최종 데이터 보관

처리 순서:
1. 마지막 오디오 세그먼트가 있으면 전체 평가 파이프라인 실행
2. 비언어적 분석 결과를 상태에 저장
3. 임시 파일 경로 정리
"""

# app/services/interview/interview_end_processing_service.py

from app.schemas.state import InterviewState
from app.services.pipeline.graph_pipeline import interview_flow_executor
from app.schemas.nonverbal import NonverbalData


async def process_last_audio_segment(state: InterviewState) -> None:
    """
    면접 종료 시 마지막 오디오 세그먼트를 처리합니다.
    
    마지막으로 녹음된 오디오가 있는 경우 전체 평가 파이프라인을 실행하여
    STT → 리라이팅 → 평가 → 요약까지 완료합니다.
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Note:
        - audio_path가 있으면 interview_flow_executor 실행
        - 처리 완료 후 audio_path 초기화
        - 비동기 처리로 파이프라인 완료까지 대기
    """
    if state.get("audio_path"):
        # 마지막 오디오 세그먼트에 대해 전체 평가 파이프라인 실행
        # STT → 리라이팅 → 평가 → 요약 순서로 처리
        await interview_flow_executor(state)
        
        # 처리 완료 후 임시 파일 경로 초기화
        state["audio_path"] = ""


def save_nonverbal_counts(state: InterviewState, iv: NonverbalData) -> None:
    """
    비언어적 분석 결과를 면접 상태에 저장합니다.
    
    프론트엔드에서 수집된 비언어적 데이터(표정, 자세, 시선, 제스처)를
    평가 시스템에서 사용할 수 있도록 상태에 저장합니다.
    
    Args:
        state (InterviewState): 면접 상태 객체
        iv (NonverbalData): 비언어적 분석 데이터
        
    Note:
        - 표정(expression): smile, neutral, frown, angry 횟수
        - 자세(posture): 자세 관련 분석 데이터
        - 시선(gaze): 시선 처리 관련 데이터
        - 제스처(gesture): 손동작 관련 데이터
        - dict() 변환으로 JSON 직렬화 가능한 형태로 저장
    """
    state["nonverbal_counts"] = {
        "posture": iv.posture.dict(),           # 자세 데이터 (Pydantic 모델 → dict)
        "expression": iv.facial_expression.dict(),  # 표정 데이터 (smile, neutral, frown, angry)
        "gaze": iv.gaze,                        # 시선 데이터
        "gesture": iv.gesture,                  # 제스처 데이터
    }
