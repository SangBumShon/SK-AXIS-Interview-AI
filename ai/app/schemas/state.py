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
    # 한 스텝에 여러 값을 리스트로 모아 줍니다.
    interviewee_ids: Annotated[List[int], operator.add]

    audio_path: str

    # stt 결과 dict를 병합합니다.
    stt: Annotated[Dict[str, Any], dict_merge]

    # rewrite 결과 dict를 병합합니다.
    rewrite: Annotated[Dict[str, Any], dict_merge]

    # evaluation 결과 dict를 병합합니다.
    evaluation: Annotated[Dict[str, Any], dict_merge]

    # report 결과 dict를 병합합니다.
    report: Annotated[Dict[str, Any], dict_merge]

    # decision_log는 여러 로그를 리스트로 붙여 줍니다.
    decision_log: Annotated[List[Any], operator.add]

    # nonverbal_counts dict도 병합
    nonverbal_counts: Annotated[Dict[str, int], dict_merge]
