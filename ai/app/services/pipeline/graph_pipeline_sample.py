from langgraph.graph import StateGraph
from datetime import datetime
import os
import asyncio
from typing import TypedDict, Literal
import openai
from app.services.interview.stt_service import transcribe_audio_file
from app.services.interview.rewrite_service import rewrite_answer
from app.services.interview.evaluation_service import evaluate_keywords_from_full_answer
from app.services.interview.report_service import create_radar_chart, generate_pdf
from app.schemas.nonverbal import Posture, FacialExpression, NonverbalData
from app.services.interview.nonverbal_service import evaluate  
from app.schemas.state import InterviewState
from langgraph.channels import LastValue, BinaryOperatorAggregate



# ──────────────── Typed State ────────────────

# class InterviewState(TypedDict, total=False):
#     interviewee_id: str
#     audio_path: str
#     stt: dict
#     rewrite: dict
#     evaluation: dict
#     report: dict
#     decision_log: list

# ──────────────── Nodes / Agents ────────────────
# stt node
def stt_node(state: InterviewState) -> InterviewState:
    audio_path = state.get("audio_path")
    raw = transcribe_audio_file(audio_path)
    ts = datetime.now().isoformat()
    state.setdefault("stt", {"done": False, "segments": []})
    state["stt"]["segments"].append({"raw": raw, "timestamp": ts})
    state.setdefault("decision_log", []).append({
        "step": "stt_node",
        "result": "success",
        "time": ts,
        "details": {"segment": raw[:30]}
    })
    return state


# rewrite agent
async def rewrite_agent(state: InterviewState) -> InterviewState:
    raw = state["stt"]["segments"][-1]["raw"]
    rewritten, _ = await rewrite_answer(raw)
    item = {"raw": raw, "rewritten": rewritten}
    state.setdefault("rewrite", {"done": False, "items": []})
    state["rewrite"]["items"].append(item)
    ts = datetime.now().isoformat()
    state["decision_log"].append({
        "step": "rewrite_agent",
        "result": "processing",
        "time": ts,
        "details": {"raw_preview": raw[:30]}
    })
    return state

# 리라이팅 검증 후 조건부 분기 함수
def should_retry_rewrite(state: InterviewState) -> Literal["retry", "done"]:
    """
    리라이팅 결과 검증 후 재시도 여부를 결정하는 함수
    
    Returns:
        "retry": 재리라이팅 필요
        "done": 완료
    """
    items = state.get("rewrite", {}).get("items", [])
    
    # 모든 항목이 ok=True인지 확인
    all_passed = all(item.get("ok", False) for item in items)
    
    # 재시도 횟수 확인
    retry_count = state.get("rewrite", {}).get("retry_count", 0)
    
    if not all_passed and retry_count < 3:  # 최대 3번까지 재시도
        state["rewrite"]["retry_count"] = retry_count + 1
        return "retry"
    
    return "done"

# rewrite judge agent
# rewrite judge agent에는 아래와 같은 검증이 필요합니다.
# 시스템: 당신은 텍스트 리라이팅 평가 전문가입니다.
# 원본: \"{raw}\"
# 리라이팅: \"{rewritten}\"
# 1) 의미 보존
# 2) 과잉 축약/확장
# 3) 오탈자/문맥 오류
# 위 기준에 따라 JSON 형식으로 ok(bool)와 notes(list)를 반환하세요.
#  """
#     1) rewrite.items 가 비어 있으면 에러
#     2) 각 item에 ok, judge_notes 설정
#     3) ok=True인 항목만 rewrite.final 에 {raw, rewritten, timestamp} 형태로 누적
#     4) rewrite.done = True, decision_log 기록
#     """
# # """

async def rewrite_judge_agent(state: InterviewState) -> InterviewState:
    """
    리라이팅된 텍스트를 평가하고 검증하는 에이전트
    
    Args:
        state (InterviewState): 현재 면접 상태
        
    Returns:
        InterviewState: 업데이트된 면접 상태
    """
    # 1. rewrite.items가 비어있는지 확인
    if not state.get("rewrite", {}).get("items"):
        state.setdefault("decision_log", []).append({
            "step": "rewrite_judge_agent",
            "result": "error",
            "time": datetime.now().isoformat(),
            "details": {"error": "No rewrite items found"}
        })
        return state

    # 2. 각 item 평가
    for item in state["rewrite"]["items"]:
        if "ok" in item:  # 이미 평가된 항목은 건너뛰기
            continue
            
        raw = item["raw"]
        rewritten = item["rewritten"]

        prompt = JUDGE_PROMPT.format(raw=raw, rewritten=rewritten)

        try:
            start = time.perf_counter()
            response = openai.chat.completions.create(
                model="gpt-4",  # gpt-4o-mini는 존재하지 않는 모델명입니다
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=512
            )
            elapsed = time.perf_counter() - start
            result_json = response.choices[0].message.content.strip()

            # GPT가 JSON 형식으로 응답한다고 가정하고 파싱
            import json
            result = json.loads(result_json)

            # 결과를 item에 반영
            item["ok"] = result.get("ok", False)
            item["judge_notes"] = result.get("judge_notes", [])
            
            # 3. ok=True인 항목만 final에 누적
            if item["ok"]:
                state.setdefault("rewrite", {}).setdefault("final", []).append({
                    "raw": raw,
                    "rewritten": rewritten,
                    "timestamp": datetime.now().isoformat()
                })

            # decision_log 기록
            state.setdefault("decision_log", []).append({
                "step": "rewrite_judge_agent",
                "result": f'ok={item["ok"]}',
                "time": datetime.now().isoformat(),
                "details": {
                    "notes": item["judge_notes"],
                    "elapsed_sec": round(elapsed, 2)
                }
            })

        except Exception as e:
            # 실패 시 fallback
            item["ok"] = False
            item["judge_notes"] = [f"judge error: {str(e)}"]
            state.setdefault("decision_log", []).append({
                "step": "rewrite_judge_agent",
                "result": "error",
                "time": datetime.now().isoformat(),
                "details": {"error": str(e)}
            })

    # 4. 모든 항목이 처리되었으면 done 플래그 설정
    if all("ok" in item for item in state["rewrite"]["items"]):
        state["rewrite"]["done"] = True

    return state

# 비언어적 요소 평가 agent
async def nonverbal_evaluation_agent(state: InterviewState) -> InterviewState:
    ts = datetime.now().isoformat()
    try:
        counts: Dict[str, Any] = state.get("nonverbal_counts", {})
        if not counts:
            raise ValueError("nonverbal_counts가 없습니다.")

        # 1) 세부 카운트 파싱
        posture_data = counts["posture"]              # 예: {"leg_spread":2, "leg_shake":1, "head_down":0, ...}
        facial_data  = counts["expression"]           # 예: {"smile":3, "neutral":2, "frown":1, ...}

        posture = Posture.parse_obj(posture_data)
        facial  = FacialExpression.parse_obj(facial_data)

        # 2) NonverbalData 생성 & AI 평가
        nv = NonverbalData(
            interviewee_id=state["interviewee_id"],
            is_speaking=False,  # end 시점이므로 speaking 여부 무관
            posture=posture,
            facial_expression=facial
        )
        nv_score = await evaluate(nv)  # NonverbalScore

        # 3) 0.0–1.0 → 0–15점 환산
        pts = int(round(nv_score.overall_score * 15))
        reason = nv_score.detailed_analysis or nv_score.feedback.get("종합", "")

        # 4) state에 병합
        state.setdefault("evaluation", {}).setdefault("results", {})["비언어적"] = {
            "score": pts,
            "reason": reason
        }
        state.setdefault("decision_log", []).append({
            "step": "nonverbal_evaluation",
            "result": "success",
            "time": ts,
            "details": {"score": pts}
        })

    except Exception as e:
        state.setdefault("evaluation", {})["nonverbal_error"] = str(e)
        state.setdefault("decision_log", []).append({
            "step": "nonverbal_evaluation",
            "result": "error",
            "time": ts,
            "details": {"error": str(e)}
        })

    return state


# 평가 검증 후 조건부 분기 함수
def should_retry_evaluation(state: InterviewState) -> Literal["retry", "continue"]:
    """
    평가 결과 검증 후 재평가 여부를 결정하는 함수
    
    Returns:
        "retry": 재평가 필요
        "continue": 다음 단계로 진행
    """
    evaluation = state.get("evaluation", {})
    
    # 평가가 완료되지 않았거나 검증에 실패한 경우
    if not evaluation.get("done") or not evaluation.get("ok", False):
        # 재시도 횟수 확인
        retry_count = evaluation.get("retry_count", 0)
        if retry_count < 3:  # 최대 3번까지 재시도
            # 재시도 횟수 증가
            state["evaluation"]["retry_count"] = retry_count + 1
            return "retry"
    
    return "continue"


# 평가 agent
async def evaluation_agent(state: InterviewState) -> InterviewState:
    """
    LLM 키워드 기반 평가 + 비언어적 요소 평가를 수행합니다.
    비언어적 요소 평가 관련 추가 필욮
    """
    rewritten_items = state.get("rewrite", {}).get("items", [])
    full_answer = "\n".join([item["rewritten"] for item in rewritten_items])
    results = await evaluate_keywords_from_full_answer(full_answer)
    state["evaluation"] = {
        "done": True,
        "results": results
    }
    ts = datetime.now().isoformat()
    state.setdefault("decision_log", []).append({
        "step": "evaluation_agent",
        "result": "done",
        "time": ts,
        "details": {}
    })
    return state



# 평가 judge agent
async def evaluation_judge_agent(state: InterviewState) -> InterviewState:
    """
    평가 결과를 검증하는 에이전트

    검증 기준:
    1. 키워드별 항목 수가 올바른지 (3개)
    2. 점수 범위가 1~5점인지
    3. 총점이 올바른 범위 내인지 (동적 max 기준)

    Args:
        state (InterviewState): 현재 면접 상태

    Returns:
        InterviewState: 업데이트된 면접 상태
    """
    if not state.get("evaluation", {}).get("results"):
        state.setdefault("decision_log", []).append({
            "step": "evaluation_judge_agent",
            "result": "error",
            "time": datetime.now().isoformat(),
            "details": {"error": "No evaluation results found"}
        })
        return state

    results = state["evaluation"]["results"]
    judge_notes = []
    is_valid = True

    # 1. 키워드별 항목 수 검증 (3개)
    for keyword, criteria in results.items():
        if len(criteria) != 3:
            judge_notes.append(f"Keyword '{keyword}' has {len(criteria)} criteria (expected 3)")
            is_valid = False

    # 2. 점수 범위 검증 (1~5점)
    for keyword, criteria in results.items():
        for criterion, data in criteria.items():
            score = data.get("score", 0)
            if not (1 <= score <= 5):
                judge_notes.append(f"Invalid score {score} in {keyword}.{criterion}")
                is_valid = False

    # 3. 총점 범위 검증
    total_score = sum(
        sum(criterion.get("score", 0) for criterion in criteria.values())
        for criteria in results.values()
    )
    max_possible_score = len(results) * 3 * 5  # 키워드 수 * 3개 항목 * 최대 점수 5

    if total_score > max_possible_score:
        judge_notes.append(f"Total score {total_score} exceeds maximum {max_possible_score}")
        is_valid = False

    # 평가 결과 상태에 기록
    state["evaluation"]["judge"] = {
        "ok": is_valid,
        "judge_notes": judge_notes,
        "total_score": total_score,
        "max_score": max_possible_score
    }

    # 상위 평가 상태에도 반영
    state["evaluation"]["ok"] = is_valid

    # decision_log 기록
    state.setdefault("decision_log", []).append({
        "step": "evaluation_judge_agent",
        "result": f"ok={is_valid}",
        "time": datetime.now().isoformat(),
        "details": {
            "total_score": total_score,
            "max_score": max_possible_score,
            "keywords_checked": len(results),
            "notes": judge_notes
        }
    })

    return state



async def pdf_node(state: InterviewState) -> InterviewState:
    from app.constants.evaluation_constants_full_all import (
        TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,
        DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES,
    )

    answers = [item["rewritten"] for item in state.get("rewrite", {}).get("items", [])]
    evaluation_results = state.get("evaluation", {}).get("results", {})
    questions = state.get("questions", [])

    if not evaluation_results:
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = False
        state["report"]["pdf"]["error"] = "평가 결과가 없습니다."
        return state

    keyword_results = {
        kw: {
            "score": sum(sub.get("score", 0) for sub in criteria.values()),
            "reasons": "\n".join(sub.get("reason", "") for sub in criteria.values())
        }
        for kw, criteria in evaluation_results.items()
    }

    cid = state.get("interviewee_id")
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    out_dir = './results'
    os.makedirs(out_dir, exist_ok=True)
    chart_path = os.path.join(out_dir, f"{cid}_chart_{ts}.png")
    pdf_path = os.path.join(out_dir, f"{cid}_report_{ts}.pdf")

    try:
        technical_keywords = set(TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES.keys())
        domain_keywords = set(DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES.keys())

        technical_total = 0
        domain_total = 0
        general_total = 0

        nonverbal_score = 0
        nonverbal_reason = ""
        if "비언어적" in keyword_results:
            nonverbal_score = keyword_results.pop("비언어적")["score"]
            nonverbal_reason = keyword_results.pop("비언어적", {}).get("reasons", "")

        for k, v in keyword_results.items():
            if k in technical_keywords:
                technical_total += v["score"]
            elif k in domain_keywords:
                domain_total += v["score"]
            else:
                general_total += v["score"]

        final_score = round(
            (general_total / 105 * 67.5) +
            (technical_total / 15 * 22.5) +
            (domain_total / 15 * 22.5) +
            (nonverbal_score / 15 * 15)
        )

        create_radar_chart(keyword_results, chart_path)
        generate_pdf(
            keyword_results=keyword_results,
            chart_path=chart_path,
            output_path=pdf_path,
            interviewee_id=cid,
            questions=questions,
            answers=answers,
            nonverbal_score=nonverbal_score,
            nonverbal_reason=nonverbal_reason,
            total_score=final_score
        )

        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = True
        state["report"]["pdf"]["path"] = pdf_path
        ts2 = datetime.now().isoformat()
        state["decision_log"].append({
            "step": "pdf_node",
            "result": "generated",
            "time": ts2,
            "details": {"path": pdf_path}
        })
    except Exception as e:
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = False
        state["report"]["pdf"]["error"] = str(e)
        ts2 = datetime.now().isoformat()
        state["decision_log"].append({
            "step": "pdf_node",
            "result": "error",
            "time": ts2,
            "details": {"error": str(e)}
        })
    return state


# excel node 
# async def excel_node(state: InterviewState) -> InterviewState:
#     # 지원자별 지원자 아이디, 지원자별 5개 질문 데이터, 지원자 답변 raw stt data, 지원자 답변 rewritten data, 지원자 총점 
#     # 위의 항목들을 칼럼으로 하는 excel 파일 생성
#     # 파일 이름은 지원자 아이디_report_YYYYMMDDHHMMSS.xlsx 형식으로 생성
#     # 파일 경로는 ./results 폴더에 생성
    
#     state.setdefault("report", {})["excel"] = {
#         "generated": False,
#         "path": None
#     }
#     return state



# ──────────────── LangGraph 정의 ────────────────

interview_builder = StateGraph(InterviewState)
interview_builder.add_node("stt_node", stt_node)
interview_builder.add_node("rewrite_agent", rewrite_agent)  # async여도 그냥 등록
interview_builder.add_node("rewrite_judge_agent", rewrite_judge_agent)  # async여도 그냥 등록
interview_builder.set_entry_point("stt_node")
interview_builder.add_edge("stt_node", "rewrite_agent")
interview_builder.add_edge("rewrite_agent", "rewrite_judge_agent")
interview_builder.add_conditional_edges(
    "rewrite_judge_agent",
    should_retry_rewrite,
    {
        "retry": "rewrite_agent",
        "done": "__end__"
    }
)
interview_flow_executor = interview_builder.compile()

# 📄 면접 종료: 전체 평가 및 리포트 생성
final_builder = StateGraph(InterviewState)
final_builder.add_node("nonverbal_eval", nonverbal_evaluation_agent)
final_builder.add_node("evaluation_agent", evaluation_agent)
final_builder.add_node("evaluation_judge_agent", evaluation_judge_agent)
final_builder.add_node("pdf_node", pdf_node)
final_builder.set_entry_point("nonverbal_eval")
final_builder.add_edge("nonverbal_eval", "evaluation_agent")
final_builder.add_edge("evaluation_agent", "evaluation_judge_agent")

# ───────── decision_log 채널 재설정 ─────────
# (A) 최근 1건만 남기기
final_builder.set_channel(
    "decision_log",
    LastValue()
)

# 또는

# (B) 마지막 20건만 유지하기
def reducer(old: list, new: dict) -> list:
    return (old + [new])[-20:]

final_builder.set_channel(
    "decision_log",
    BinaryOperatorAggregate(list, reducer)
)
# ──────────────────────────────────────────

# conditional 분기만 남기고 direct edge 제거
final_builder.add_conditional_edges(
    "evaluation_judge_agent",
    should_retry_evaluation,
    {"retry": "evaluation_agent", "continue": "pdf_node"}
)

final_report_flow_executor = final_builder.compile()