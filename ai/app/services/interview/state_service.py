"""
SK AXIS AI 면접 상태 관리 서비스

이 파일은 면접 상태 객체의 초기화를 담당하는 서비스입니다.
주요 기능:
- 새로운 면접 세션의 초기 상태 생성
- 파이프라인 각 단계별 상태 구조 정의
- 기본값 설정 및 데이터 구조 표준화

상태 구조:
- interviewee_id: 면접자 고유 ID
- questions: 면접 질문 목록
- audio_path: 현재 처리 중인 오디오 파일 경로
- stt: 음성인식 결과 저장소
- rewrite: 답변 정제 결과 저장소  
- evaluation: 평가 결과 저장소
- summary: 최종 요약 점수 저장소
- report: 리포트 생성 결과 저장소 (프론트로 기능 이전)
- decision_log: 처리 과정 로그 저장소
"""

from typing import List, Dict, Any

def create_initial_state(interviewee_id: int, questions: List[Dict], file_path: str) -> Dict[str, Any]:
    """
    새로운 면접 세션을 위한 초기 상태를 생성합니다.
    
    Args:
        interviewee_id (int): 면접자 고유 식별자
        questions (List[Dict]): 면접 질문 목록
        file_path (str): 초기 오디오 파일 경로
        
    Returns:
        Dict[str, Any]: 면접 상태 초기값
        
    Note:
        - 모든 처리 단계(done 플래그)는 False로 초기화
        - 각 단계별 결과 저장소는 빈 컨테이너로 초기화
        - decision_log로 전체 처리 과정 추적 가능
    """
    return {
        # ─── 기본 정보 ───
        "interviewee_id": interviewee_id,    # 면접자 ID
        "questions": questions,              # 면접 질문 목록
        "audio_path": file_path,            # 현재 처리할 오디오 파일 경로
        
        # ─── 파이프라인 단계별 상태 ───
        "stt": {                            # 음성인식 단계
            "done": False,                   # STT 처리 완료 여부
            "segments": []                   # STT 결과 세그먼트 목록
        },
        "rewrite": {                        # 답변 정제 단계
            "done": False,                   # 리라이팅 처리 완료 여부
            "items": []                      # 정제된 답변 목록
        },
        "evaluation": {                     # 평가 단계
            "done": False,                   # 평가 처리 완료 여부
            "results": {}                    # 키워드별 평가 결과
        },
        
        # ─── 최종 결과 ───
        "summary": {                        # 요약 점수 (score_summary_agent에서 생성)
            "total_score": 0,               # 총점 (100점 만점)
            "language_score": 0,            # 언어적 점수 (인성+기술/도메인)
            "language_reason": "",          # 언어적 평가 사유
            "nonverbal_score": 0,           # 비언어적 점수 (15점 만점)
            "nonverbal_reason": ""          # 비언어적 평가 사유
        },
        "report": {                         # 리포트 생성 결과  (프론트로 기능 이전)
            "pdf_path": ""                  # 생성된 PDF 리포트 파일 경로 (프론트로 기능 이전)
        },
        
        # ─── 처리 과정 로그 ───
        "decision_log": [],                 # 각 단계별 처리 로그 (디버깅용)
    }