"""
SK AXIS AI 면접 파이프라인 상태 관리 스키마

이 파일은 LangGraph 기반 면접 평가 파이프라인의 상태 구조를 정의합니다.
주요 기능:
- TypedDict 기반 상태 타입 정의
- 각 단계별 데이터 병합 전략 설정
- 파이프라인 진행 상황 추적
- 안전한 타입 체크 및 데이터 무결성 보장

상태 병합 전략:
- dict_merge: 딕셔너리 병합 (덮어쓰기)
- operator.add: 리스트 추가 (누적)
- 단일 값: 최신 값으로 덮어쓰기

LangGraph 연동:
- 각 노드에서 상태 읽기/쓰기
- 조건부 엣지에서 상태 기반 분기
- 파이프라인 완료까지 상태 유지
"""

import operator
from typing import TypedDict, Annotated, Dict, Any, List

# ──────────────── 🔧 유틸리티 함수 ────────────────

def dict_merge(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    두 딕셔너리를 병합하여 새 딕셔너리를 반환합니다.
    
    Args:
        a (Dict[Any, Any]): 기존 딕셔너리
        b (Dict[Any, Any]): 병합할 딕셔너리
        
    Returns:
        Dict[Any, Any]: 병합된 새 딕셔너리
        
    Note:
        - b의 키가 a의 동일한 키를 덮어씀
        - LangGraph에서 상태 업데이트 시 사용
        - 중첩된 딕셔너리는 얕은 병합 수행
    """
    merged = a.copy()
    merged.update(b)
    return merged

# ──────────────── 📊 면접 상태 정의 ────────────────

class InterviewState(TypedDict, total=False):
    """
    면접 평가 파이프라인의 전체 상태를 정의하는 TypedDict
    
    Attributes:
        interviewee_id (int): 면접자 고유 식별자 (단일 값)
        questions (List[Any]): 면접 질문 목록 (리스트 추가)
        audio_path (str): 현재 처리 중인 오디오 파일 경로 (단일 값)
        stt (Dict[str, Any]): STT 결과 딕셔너리 (병합)
        rewrite (Dict[str, Any]): 리라이팅 결과 딕셔너리 (병합)
        evaluation (Dict[str, Any]): 평가 결과 딕셔너리 (병합)
        summary (Dict[str, Any]): 최종 요약 결과 딕셔너리 (병합)
        report (Dict[str, Any]): 리포트 생성 결과 딕셔너리 (병합)
        decision_log (List[Any]): 파이프라인 처리 로그 (리스트 추가)
        nonverbal_counts (Dict[str, Any]): 비언어적 데이터 딕셔너리 (병합)
        
    Note:
        - total=False: 모든 필드가 선택적 (부분 상태 허용)
        - Annotated로 병합 전략 명시
        - LangGraph 노드 간 상태 전달에 사용
    """
    
    # ─── 기본 식별 정보 ───
    interviewee_id: int  # 면접자 ID (단일 값, 덮어쓰기)

    # ─── 면접 설정 정보 ───
    questions: Annotated[List[Any], operator.add]  # 질문 목록 (리스트 추가)

    # ─── 현재 처리 파일 ───
    audio_path: str  # 오디오 파일 경로 (단일 값, 덮어쓰기)

    # ─── 파이프라인 단계별 결과 (딕셔너리 병합) ───
    stt: Annotated[Dict[str, Any], dict_merge]  # STT 결과
    # 구조: {"done": bool, "segments": [{"raw": str, "timestamp": str}]}
    
    rewrite: Annotated[Dict[str, Any], dict_merge]  # 리라이팅 결과
    # 구조: {"done": bool, "items": [...], "final": [...], "retry_count": int}
    
    evaluation: Annotated[Dict[str, Any], dict_merge]  # 평가 결과
    # 구조: {"done": bool, "results": {키워드: {기준: {score, reason, quotes}}}, "ok": bool}
    
    summary: Annotated[Dict[str, Any], dict_merge]  # 최종 요약
    # 구조: {"total_score": float, "weights": {...}, "verbal_reason": [...]}

    # ─── 리포트 생성 결과 ───
    report: Annotated[Dict[str, Any], dict_merge]  # 리포트 결과
    # 구조: {"pdf_path": str}

    # ─── 로깅 및 추적 ───
    decision_log: Annotated[List[Any], operator.add]  # 처리 로그 (리스트 추가)
    # 구조: [{"step": str, "result": str, "time": str, "details": {...}}]

    # ─── 비언어적 데이터 ───
    nonverbal_counts: Annotated[Dict[str, Any], dict_merge]  # 비언어적 데이터
    # 구조: {"posture": {...}, "expression": {...}, "gaze": int, "gesture": int}
