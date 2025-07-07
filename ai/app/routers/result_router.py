"""
SK AXIS AI 면접 결과 조회 라우터

이 파일은 면접 평가 결과를 조회하는 API 엔드포인트들을 정의합니다.
주요 기능:
- 면접 평가 상태 확인 (PENDING/DONE) - 폴링용
- 최종 평가 결과 조회 (점수, 사유 등 상세 정보)

API 엔드포인트:
- GET /api/v1/results/statuses : 평가 상태 확인 (프론트엔드 폴링용)
- GET /api/v1/results : 최종 평가 결과 조회 (상세 정보 포함)
"""

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

# 결과 조회 관련 API 라우터 생성
router = APIRouter(prefix="/results", tags=["Result"])

@router.get("/statuses", response_model=ResultStatusListResponse)
async def get_result_statuses(
    interviewee_ids: str = Query(..., description="쉼표로 구분된 면접자 ID 목록 ex) 101,102")
):
    """
    다수 면접자의 평가 상태를 확인하는 API (폴링용)
    
    프론트엔드에서 평가 진행 상태를 실시간으로 확인하기 위해 주기적으로 호출됩니다.
    
    Args:
        interviewee_ids: 쉼표로 구분된 면접자 ID 목록 (예: "101,102,103")
    
    Returns:
        ResultStatusListResponse: 각 면접자별 상태 정보
        - interviewee_id: 면접자 ID
        - status: "PENDING" (평가 중) 또는 "DONE" (평가 완료)
        - score: 평가 완료 시 총점 (100점 만점)
    
    Note:
        - state.done 플래그를 기준으로 상태 판단
        - 평가 완료 시 총점을 float → int로 반올림 처리
    """
    try:
        # 쉼표로 구분된 ID 문자열을 정수 리스트로 변환
        id_list = [int(id_str) for id_str in interviewee_ids.split(",") if id_str.strip()]
        if not id_list:
            raise HTTPException(status_code=400, detail="유효한 면접자 ID가 제공되지 않았습니다.")

        result_statuses: list[ResultStatusResponse] = []
        for interviewee_id in id_list:
            # 메모리 저장소에서 면접 상태 조회
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            print(f"[DEBUG] /statuses - interviewee_id={interviewee_id}, state_exists={state is not None}")
            if state:
                print(f"[DEBUG] /statuses - state_type={type(state)}, done_flag={state.get('done') if isinstance(state, dict) else 'N/A'}")
            
            # done 플래그 기준으로 상태 판단
            status = "DONE" if state and isinstance(state, dict) and state.get("done", False) else "PENDING"
            score = None
            
            # 평가 완료 시 총점 추출
            if status == "DONE":
                summary = state.get("summary", {}) if isinstance(state.get("summary"), dict) else {}
                total_score = summary.get("total_score")
                # float를 int로 반올림 처리 (API 스키마 요구사항)
                score = round(total_score) if total_score is not None else None

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
    
    평가가 완료된 면접자들의 상세한 평가 결과를 반환합니다.
    
    Args:
        interviewee_ids: 쉼표로 구분된 면접자 ID 목록 (예: "101,102,103")
    
    Returns:
        FinalResultListResponse: 평가 결과 상세 정보
        - weights: 영역별 가중치 (언어적 45%, 직무·도메인 45%, 비언어적 10%)
        - results: 각 면접자별 상세 결과
          - competencies: 역량별 점수 (SUPEX, VWBE, Passionate 등)
          - language: 언어적 평가 (점수, 사유)
          - nonverbal: 비언어적 평가 (점수, 사유)
    
    Note:
        - 평가 완료(done=True)된 면접자만 결과에 포함
        - 타입 변환 처리: float → int, list → string
    """
    try:
        # 쉼표로 구분된 ID 문자열을 정수 리스트로 변환
        id_list = [int(id_str) for id_str in interviewee_ids.split(",") if id_str.strip()]
        if not id_list:
            raise HTTPException(status_code=400, detail="유효한 면접자 ID가 제공되지 않았습니다.")

        results: list[FinalResultResponse] = []
        for interviewee_id in id_list:
            # 메모리 저장소에서 면접 상태 조회
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            
            # 평가 완료되지 않은 면접자는 결과에서 제외
            if not state or not isinstance(state, dict) or not state.get("done", False):
                continue

            # ─── 가중치 정보 추출 ───
            # 요약 노드에서 계산된 weights 값을 가져와 문자열 퍼센트로 변환
            summary = state.get("summary", {}) if isinstance(state.get("summary"), dict) else {}
            raw_weights = summary.get("weights", {})  # ex: {'인성적 요소':45.0, '직무·도메인':45.0, '비언어적 요소':10.0}
            weights = {
                "언어적 요소": f"{raw_weights.get('인성적 요소', 0)}%",
                "직무·도메인": f"{raw_weights.get('직무·도메인', 0)}%",
                "비언어적 요소": f"{raw_weights.get('비언어적 요소', 0)}%",
            }

            # ─── 역량별 점수 추출 ───
            competencies: dict[str, int] = {}
            keyword_scores = summary.get("keyword_scores", {})
            
            # SK 핵심 가치 영역
            sk_keys = ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]
            for key in sk_keys:
                competencies[key] = keyword_scores.get(key, 0)

            # 기술/도메인 영역 (키에 "/"가 포함되어 있어 "."로 변환)
            domain_keys = ["기술/직무", "도메인 전문성"]
            for key in domain_keys:
                safe_key = key.replace("/", ".")  # API 스키마 호환성을 위한 변환
                competencies[safe_key] = keyword_scores.get(key, 0)

            # ─── 언어적/비언어적 평가 결과 추출 ───
            # 요약 정보에서 언어적/비언어적 점수와 이유 추출
            verbal_score = summary.get("verbal_score", 0)
            verbal_reason = summary.get("verbal_reason", "평가 정보가 없습니다.")
            nonverbal_score = summary.get("nonverbal_score", 0)
            nonverbal_reason = summary.get("nonverbal_reason", "평가 정보가 없습니다.")
            
            # ─── 타입 변환 처리 ───
            # 🔧 Pydantic 스키마 호환성을 위한 타입 변환
            
            # verbal_score를 int로 변환
            verbal_score = round(verbal_score) if isinstance(verbal_score, (int, float)) else 0
            
            # verbal_reason이 list인 경우 string으로 변환
            if isinstance(verbal_reason, list):
                verbal_reason = " ".join(verbal_reason)
            elif not isinstance(verbal_reason, str):
                verbal_reason = "평가 정보가 없습니다."
                
            # nonverbal_score를 int로 변환
            nonverbal_score = round(nonverbal_score) if isinstance(nonverbal_score, (int, float)) else 0
            
            # nonverbal_reason이 list인 경우 string으로 변환
            if isinstance(nonverbal_reason, list):
                nonverbal_reason = " ".join(nonverbal_reason)
            elif not isinstance(nonverbal_reason, str):
                nonverbal_reason = "평가 정보가 없습니다."

            # 최종 결과 객체 생성
            results.append(
                FinalResultResponse(
                    interviewee_id=interviewee_id,
                    competencies=competencies,
                    language={"score": verbal_score, "reason": verbal_reason},
                    nonverbal={"score": nonverbal_score, "reason": nonverbal_reason}
                )
            )

        # ─── 응답 가중치 설정 ───
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
