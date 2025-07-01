import asyncio
from app.services.pipeline.graph_pipeline import final_report_flow_executor
from app.schemas.state import InterviewState
from app.constants.evaluation_constants_full_all import EVAL_CRITERIA_WITH_ALL_SCORES, TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES, DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES

def get_mock_state():
    return InterviewState(
        interviewee_id=3,
        rewrite={
            "final": [
                {"rewritten": "저는 파이썬을 가장 자신 있게 다룰 수 있습니다. 실제로 데이터 분석 프로젝트에서 파이썬을 활용해 팀의 효율을 크게 높인 경험이 있습니다."},
                {"rewritten": "문제가 발생했을 때 원인을 빠르게 파악하고, 팀원들과 소통하여 해결책을 찾는 데 주도적으로 참여한 경험이 있습니다."}
            ]
        },
        evaluation={
            "judge": {
                "total_score": 92
            }
        },
        nonverbal_counts={
            "expression": {
                "smile": 2,
                "neutral": 1
            },
            "timestamp": "2025-06-30T09:00:00"
        },
        decision_log=[]
    )

def get_mock_raw_report_json():
    # 모든 평가 키워드와 각 항목별 3개 사유 생성
    keyword_scores = {}
    keyword_reasons = {}
    # 일반
    for kw, criteria in EVAL_CRITERIA_WITH_ALL_SCORES.items():
        keyword_scores[kw] = 4
        keyword_reasons[kw] = [f"{list(criteria.keys())[i]}에 대한 예시 사유입니다." for i in range(3)]
    # 기술/직무
    for kw, criteria in TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES.items():
        keyword_scores[kw] = 4
        keyword_reasons[kw] = [f"{list(criteria.keys())[i]}에 대한 예시 사유입니다." for i in range(3)]
    # 도메인
    for kw, criteria in DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES.items():
        keyword_scores[kw] = 4
        keyword_reasons[kw] = [f"{list(criteria.keys())[i]}에 대한 예시 사유입니다." for i in range(3)]

    return {
        "applicant_id": 3,
        "interview_datetime": "2025-06-30T09:00:00",
        "report_title": "면접 종합 평가 리포트",
        "personality_score": 75,         # 언어(인성) 실제 점수 (예시)
        "job_domain_score": 24,          # 기술 및 도메인 실제 점수 (예시)
        "nonverbal_score": 12,           # 비언어 실제 점수 (예시)
        "max_personality_score": 90,     # 언어(인성) 만점
        "max_job_domain_score": 30,      # 기술/도메인 만점
        "max_nonverbal_score": 15,       # 비언어 만점
        "answers": {
            "A1": "저는 파이썬을 가장 자신 있게 다룰 수 있습니다. 실제로 데이터 분석 프로젝트에서 파이썬을 활용해 팀의 효율을 크게 높인 경험이 있습니다.",
            "A2": "문제가 발생했을 때 원인을 빠르게 파악하고, 팀원들과 소통하여 해결책을 찾는 데 주도적으로 참여한 경험이 있습니다."
        },
        "keyword_scores": keyword_scores,
        "keyword_reasons": keyword_reasons,
        "total_score": 92,
        "nonverbal_reasons": [
            "면접 내내 미소를 유지함.",
            "자세가 바르고 자신감이 느껴짐.",
            "면접관과의 시선 교환이 자연스러움."
        ],
        "generation_time": 1.23
    }

async def main():
    state = get_mock_state()
    state["raw_report_json"] = get_mock_raw_report_json()
    # 파이프라인 실행 (nonverbal_eval → ... → pdf_node → excel_node)
    result_state = await final_report_flow_executor.ainvoke(state)
    print("PDF 경로:", result_state.get("report", {}).get("pdf", {}).get("path"))
    print("엑셀 경로:", result_state.get("report", {}).get("excel", {}).get("path"))

if __name__ == "__main__":
    asyncio.run(main()) 