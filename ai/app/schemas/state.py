import operator
from typing import TypedDict, Annotated, Dict, Any, List

def dict_merge(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    두 dict를 병합해서 새 dict를 반환합니다.
    (b가 같은 키를 덮어씁니다)
    """
    merged = a.copy()
    merged.update(b)
    return merged

class InterviewState(TypedDict, total=False):
    # 지원자 ID (단일 값)
    interviewee_id: int

    # 질문 목록 저장
    questions: Annotated[List[Any], operator.add]

    # 현재 처리 중인 오디오 파일 경로
    audio_path: str

    # STT 결과 dict를 병합합니다.
    stt: Annotated[Dict[str, Any], dict_merge]

    # rewrite 결과 dict를 병합합니다.
    rewrite: Annotated[Dict[str, Any], dict_merge]

    # evaluation 결과 dict를 병합합니다.
    evaluation: Annotated[Dict[str, Any], dict_merge]

    # report 결과 dict를 병합합니다.
    report: Annotated[Dict[str, Any], dict_merge]

    # decision_log는 여러 로그를 리스트로 붙여 줍니다.
    decision_log: Annotated[List[Any], operator.add]

    # nonverbal_counts는 nested 구조(딕셔너리 혹은 int)가 혼합되므로 Any
    nonverbal_counts: Annotated[Dict[str, Any], dict_merge]
