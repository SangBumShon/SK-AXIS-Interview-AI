from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

from app.state.store import INTERVIEW_STATE_STORE
from app.schemas.result import (
    ResultStatusResponse,
    ResultStatusListResponse,
    FinalResultResponse,
    FinalResultListResponse
)

# 환경 변수 로드
load_dotenv()

router = APIRouter(prefix="/results", tags=["Result"])

@router.get("/statuses", response_model=ResultStatusListResponse)
async def get_result_statuses(
    interviewee_ids: str = Query(..., description="쉼표로 구분된 면접자 ID 목록 ex) 101,102")
):
    """
    다수 면접자의 평가 상태를 확인하는 API (폴링용)
    """
    try:
        id_list = [int(id_str) for id_str in interviewee_ids.split(",") if id_str.strip()]
        if not id_list:
            raise HTTPException(status_code=400, detail="유효한 면접자 ID가 제공되지 않았습니다.")

        result_statuses: list[ResultStatusResponse] = []
        for interviewee_id in id_list:
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            status = "DONE" if state and isinstance(state, dict) and state.get("done", False) else "PENDING"
            score = None
            if status == "DONE":
                summary = state.get("summary", {}) if isinstance(state.get("summary"), dict) else {}
                score = summary.get("total_score")

            result_statuses.append(
                ResultStatusResponse(
                    interviewee_id=interviewee_id,
                    status=status,
                    score=score
                )
            )

        return result_statuses
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류 발생: {e}")

@router.get("", response_model=FinalResultListResponse)
async def get_final_results(
    interviewee_ids: str = Query(..., description="쉼표로 구분된 면접자 ID 목록 ex) 101,102")
):
    """
    다수 면접자의 최종 평가 결과를 조회하는 API
    """
    try:
        id_list = [int(id_str) for id_str in interviewee_ids.split(",") if id_str.strip()]
        if not id_list:
            raise HTTPException(status_code=400, detail="유효한 면접자 ID가 제공되지 않았습니다.")

        results: list[FinalResultResponse] = []
        for interviewee_id in id_list:
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            if not state or not isinstance(state, dict) or not state.get("done", False):
                continue

            # 요약 노드에서 계산된 weights 값을 가져와 문자열 퍼센트로 변환
            summary = state.get("summary", {}) if isinstance(state.get("summary"), dict) else {}
            raw_weights = summary.get("weights", {})  # ex: {'인성적 요소':45.0, '직무·도메인':45.0, '비언어적 요소':10.0}
            weights = {
                "언어적 요소": f"{raw_weights.get('인성적 요소', 0)}%",
                "직무·도메인": f"{raw_weights.get('직무·도메인', 0)}%",
                "비언어적 요소": f"{raw_weights.get('비언어적 요소', 0)}%",
            }

            # 역량 점수 추출
            competencies: dict[str, int] = {}
            eval_results = state.get("evaluation", {}).get("results", {})
            sk_keys = ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]
            for key in sk_keys:
                competencies[key] = eval_results.get(key, {}).get("score", 0)

            domain_keys = ["기술/직무", "도메인 전문성"]
            for key in domain_keys:
                safe_key = key.replace("/", ".")
                competencies[safe_key] = eval_results.get(key, {}).get("score", 0)

            # 요약 정보에서 언어적/비언어적 점수와 이유 추출
            verbal_score = summary.get("verbal_score", 0)
            verbal_reason = summary.get("verbal_reason", "평가 정보가 없습니다.")
            nonverbal_score = summary.get("nonverbal_score", 0)
            nonverbal_reason = summary.get("nonverbal_reason", "평가 정보가 없습니다.")

            results.append(
                FinalResultResponse(
                    interviewee_id=interviewee_id,
                    competencies=competencies,
                    language={"score": verbal_score, "reason": verbal_reason},
                    nonverbal={"score": nonverbal_score, "reason": nonverbal_reason}
                )
            )

        # weights는 첫번째 유효 지원자의 summary에서 가져온 값을 사용
        # 만약 id_list 중 최소 하나라도 DONE 상태가 있으면 해당 weights를 리턴, 없으면 기본 퍼센트
        response_weights = weights if results else {
            "언어적 요소": "45%",
            "직무·도메인": "45%",
            "비언어적 요소": "10%"
        }

        return FinalResultListResponse(weights=response_weights, results=results)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"결과 조회 중 오류 발생: {e}")
