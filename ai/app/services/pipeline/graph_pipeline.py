# app/services/pipeline/graph_pipeline.py

from langgraph.graph import StateGraph
from datetime import datetime
from typing import Literal, Dict, Any
import os
import json
import openai

from app.services.interview.stt_service import transcribe_audio_file
from app.services.interview.rewrite_service import rewrite_answer
from app.services.interview.evaluation_service import evaluate_keywords_from_full_answer
from app.services.interview.report_service import create_radar_chart, generate_pdf
from app.schemas.nonverbal import Posture, FacialExpression, NonverbalData
from app.services.interview.nonverbal_service import evaluate
from app.schemas.state import InterviewState
from langgraph.channels import LastValue, BinaryOperatorAggregate
from app.constants.evaluation_constants_full_all import (
    EVAL_CRITERIA_WITH_ALL_SCORES,
    TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,
    DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES
)

# 리라이팅 검증용 프롬프트
JUDGE_PROMPT = """
시스템: 당신은 텍스트 리라이팅 평가 전문가입니다.
원본: "{raw}"
리라이팅: "{rewritten}"
1) 의미 보존
2) 과잉 축약/확장
3) 오탈자/문맥 오류
위 기준에 따라 JSON 형식으로 ok(bool)와 judge_notes(list)를 반환하세요.
"""

# ───────────────────────────────────────────────────
# 1) STT 노드: audio_path → raw text
# ───────────────────────────────────────────────────
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
        "details": {"segment_preview": raw[:30]}
    })
    return state

# ───────────────────────────────────────────────────
# 2) Rewrite 에이전트: raw → rewritten
# ───────────────────────────────────────────────────
async def rewrite_agent(state: InterviewState) -> InterviewState:
    raw = state["stt"]["segments"][-1]["raw"]
    rewritten, _ = await rewrite_answer(raw)
    item = {"raw": raw, "rewritten": rewritten}

    state.setdefault("rewrite", {"done": False, "items": []})
    state["rewrite"]["items"].append(item)

    ts = datetime.now().isoformat()
    state.setdefault("decision_log", []).append({
        "step": "rewrite_agent",
        "result": "processing",
        "time": ts,
        "details": {"raw_preview": raw[:30]}
    })
    return state

# ───────────────────────────────────────────────────
# 3) Rewrite 재시도 조건: 최대 3회
# ───────────────────────────────────────────────────
def should_retry_rewrite(state: InterviewState) -> Literal["retry", "done"]:
    items = state.get("rewrite", {}).get("items", [])
    all_passed = all(item.get("ok", False) for item in items)
    retry_count = state.get("rewrite", {}).get("retry_count", 0)

    if not all_passed and retry_count < 3:
        state["rewrite"]["retry_count"] = retry_count + 1
        return "retry"
    return "done"

# ───────────────────────────────────────────────────
# 4) Rewrite 검증 에이전트
# ───────────────────────────────────────────────────
async def rewrite_judge_agent(state: InterviewState) -> InterviewState:
    if not state.get("rewrite", {}).get("items"):
        state.setdefault("decision_log", []).append({
            "step": "rewrite_judge_agent",
            "result": "error",
            "time": datetime.now().isoformat(),
            "details": {"error": "No rewrite items found"}
        })
        return state

    for item in state["rewrite"]["items"]:
        if "ok" in item:
            continue

        raw = item["raw"]
        rewritten = item["rewritten"]
        prompt = JUDGE_PROMPT.format(raw=raw, rewritten=rewritten)

        try:
            start = datetime.now().timestamp()
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=512
            )
            elapsed = datetime.now().timestamp() - start
            result = json.loads(response.choices[0].message.content.strip())

            item["ok"] = result.get("ok", False)
            item["judge_notes"] = result.get("judge_notes", [])

            if item["ok"]:
                state.setdefault("rewrite", {}).setdefault("final", []).append({
                    "raw": raw,
                    "rewritten": rewritten,
                    "timestamp": datetime.now().isoformat()
                })

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
            item["ok"] = False
            item["judge_notes"] = [f"judge error: {e}"]
            state.setdefault("decision_log", []).append({
                "step": "rewrite_judge_agent",
                "result": "error",
                "time": datetime.now().isoformat(),
                "details": {"error": str(e)}
            })

    if all("ok" in item for item in state["rewrite"]["items"]):
        state["rewrite"]["done"] = True

    return state

# ───────────────────────────────────────────────────
# 5) Nonverbal 평가 에이전트
# ───────────────────────────────────────────────────
async def nonverbal_evaluation_agent(state: InterviewState) -> InterviewState:
    ts = datetime.now().isoformat()
    try:
        counts = state.get("nonverbal_counts", {})
        if not counts:
            state.decision_log.append("Nonverbal data not available for evaluation.")
            return state

        posture = Posture.parse_obj(counts["posture"])
        facial  = FacialExpression.parse_obj(counts["facial_expression"])
        gaze    = counts.get("gaze", 0)
        gesture = counts.get("gesture", 0)

        nv = NonverbalData(
            interviewee_id=state["interviewee_id"],
            posture=posture,
            facial_expression=facial,
            gaze=gaze,
            gesture=gesture
        )
        nv_score = await evaluate(nv)

        pts = int(round(nv_score.overall_score * 15))
        reason = nv_score.detailed_analysis or nv_score.feedback.get("종합", "")

        state.setdefault("evaluation", {}).setdefault("results", {})["비언어적"] = {
            "score": pts,
            "reason": reason
        }
        state.setdefault("decision_log", []).append({
            "step": "nonverbal_evaluation",
            "result": "success",
            "time": ts,
            "details": {
                "score": pts,
                "feedback": nv_score.feedback,
                "analysis": nv_score.detailed_analysis,
                "raw_llm_responses": {
                    "posture": nv_score.posture_raw_llm_response,
                    "facial": nv_score.facial_raw_llm_response,
                    "overall": nv_score.overall_raw_llm_response
                }
            }
        })

    except Exception as e:
        state.setdefault("decision_log", []).append({
            "step": "nonverbal_evaluation",
            "result": "error",
            "time": ts,
            "details": {"error": str(e)}
        })
    return state

# ───────────────────────────────────────────────────
# 6) 평가 재시도 조건: 최대 3회
# ───────────────────────────────────────────────────
def should_retry_evaluation(state: InterviewState) -> Literal["retry", "continue"]:
    eval_info = state.get("evaluation", {})
    if not eval_info.get("ok", False):
        retry = eval_info.get("retry_count", 0)
        print(f"[should_retry_evaluation] retry={retry}, ok={eval_info.get('ok', False)}")
        if retry < 3:
            state["evaluation"]["retry_count"] = retry + 1
            print("[should_retry_evaluation] Will retry evaluation.")
            return "retry"
    print("[should_retry_evaluation] Continue to next step.")
    return "continue"

# ───────────────────────────────────────────────────
# 7) LLM 키워드 평가 에이전트
# ───────────────────────────────────────────────────
async def evaluation_agent(state: InterviewState) -> InterviewState:
    rewritten_items = state.get("rewrite", {}).get("items", [])
    full_answer = "\n".join(item["rewritten"] for item in rewritten_items)
    results = await evaluate_keywords_from_full_answer(full_answer)

    state["evaluation"] = {"done": True, "results": results}
    ts = datetime.now().isoformat()
    state.setdefault("decision_log", []).append({
        "step": "evaluation_agent",
        "result": "done",
        "time": ts,
        "details": {}
    })
    return state

# ───────────────────────────────────────────────────
# 8) 평가 검증 에이전트
# ───────────────────────────────────────────────────
async def evaluation_judge_agent(state: InterviewState) -> InterviewState:
    results = state.get("evaluation", {}).get("results", {})
    if not results:
        state.setdefault("decision_log", []).append({
            "step": "evaluation_judge_agent",
            "result": "error",
            "time": datetime.now().isoformat(),
            "details": {"error": "No evaluation results found"}
        })
        print("[judge] No evaluation results found, will retry.")
        return state

    judge_notes = []
    is_valid = True

    # 항목 수 검증 (각 키워드에 3개)
    for kw, criteria in results.items():
        if len(criteria) != 3:
            judge_notes.append(f"Keyword '{kw}' has {len(criteria)} criteria (expected 3)")
            is_valid = False

    # 점수 범위 검증 (1~5)
    for criteria in results.values():
        for data in criteria.values():
            s = data.get("score", 0)
            if not (1 <= s <= 5):
                judge_notes.append(f"Invalid score {s}")
                is_valid = False

    # 총점 검증
    total = sum(sum(c.get("score", 0) for c in crit.values()) for crit in results.values())
    max_score = len(results) * 3 * 5
    if total > max_score:
        judge_notes.append(f"Total {total} exceeds max {max_score}")
        is_valid = False

    print(f"[judge] is_valid={is_valid}, judge_notes={judge_notes}, total={total}, max_score={max_score}")
    state["evaluation"]["judge"] = {
        "ok": is_valid,
        "judge_notes": judge_notes,
        "total_score": total,
        "max_score": max_score
    }
    state["evaluation"]["ok"] = is_valid

    ts = datetime.now().isoformat()
    state.setdefault("decision_log", []).append({
        "step": "evaluation_judge_agent",
        "result": f"ok={is_valid}",
        "time": ts,
        "details": {
            "total_score": total,
            "max_score": max_score,
            "notes": judge_notes
        }
    })
    return state

# ───────────────────────────────────────────────────
# 9) PDF 생성 노드
# ───────────────────────────────────────────────────
async def pdf_node(state: InterviewState) -> InterviewState:
    """
    최종 리포트 노드:
    - 언어45% + 도메인·직무45% + 비언어10% 가중치로
    - 총점 100점 기준 계산 후 PDF 생성
    """
    from app.services.interview.report_service import create_radar_chart, generate_pdf
    from datetime import datetime

    # rewrite된 답변
    answers = [i["rewritten"] for i in state["rewrite"]["items"]]
    # 평가 결과
    eval_res = state["evaluation"]["results"]
    # 비언어 분리
    nv = eval_res.pop("비언어적", {"score":0, "reason":""})
    nv_score  = nv["score"]
    nv_reason = nv["reason"]

    # 키워드별 원점수·사유 집계
    keyword_results = {
        kw: {
            "score": sum(x.get("score",0) for x in crit.values()),
            "reasons": "\n".join(x.get("reason","") for x in crit.values())
        }
        for kw, crit in eval_res.items()
    }

    # 일반키워드 vs 도메인·직무 분리
<<<<<<< HEAD
    general_categories_list = ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]
=======
    general_categories_list = ["SUPEX", "V", "WBE", "Passionate", "Proactive", "Professional", "People"]
>>>>>>> origin/front-ai-face
    job_domain_categories_list = ["기술/직무", "도메인 전문성"]

    sum_gen = 0
    for cat in general_categories_list:
        if cat in keyword_results:
            sum_gen += keyword_results[cat]["score"]

    sum_jd = 0
    for cat in job_domain_categories_list:
        if cat in keyword_results:
            sum_jd += keyword_results[cat]["score"]

    # 영역별 100점 스케일
    # 최대 점수
    max_gen_score = len(general_categories_list) * 3 * 5  # 7 categories * 3 criteria/cat * 5 points/criteria = 105
    max_jd_score = len(job_domain_categories_list) * 3 * 5   # 2 categories * 3 criteria/cat * 5 points/criteria = 30
    max_nv_score = 15 # 비언어적 요소의 최대 점수는 15점으로 가정

    area_scores = {
        "언어적 요소": round(sum_gen / max_gen_score * 100),
        "직무·도메인":    round(sum_jd  / max_jd_score * 100),
        "비언어적 요소": round(nv_score / max_nv_score * 100),
    }
    weights = {"언어적 요소":"45%", "직무·도메인":"45%", "비언어적 요소":"10%"}

    # 최종 100점 환산
    total_score = round(
        area_scores["언어적 요소"]   * 0.45 +
        area_scores["직무·도메인"]    * 0.45 +
        area_scores["비언어적 요소"]  * 0.10
    )

    # 경로 준비
    cid = state["interviewee_id"]
    ts  = datetime.now().strftime("%Y%m%d%H%M%S")
    out = "./results"; os.makedirs(out, exist_ok=True)
    chart = f"{out}/{cid}_chart_{ts}.png"
    pdfp  = f"{out}/{cid}_report_{ts}.pdf"

    try:
        create_radar_chart(keyword_results, chart)
        generate_pdf(
            keyword_results=keyword_results,
            chart_path=chart,
            output_path=pdfp,
            interviewee_id=cid,
            answers=answers,
            nonverbal_score=nv_score,
            nonverbal_reason=nv_reason,
            total_score=total_score,
            area_scores=area_scores,
            weights=weights
        )
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = True
        state["report"]["pdf"]["path"]  = pdfp
        state["report"]["pdf"]["score"] = total_score
        state.setdefault("decision_log", []).append({
            "step":"pdf_node","result":"generated",
            "time": datetime.now().isoformat(),
            "details":{"path":pdfp,"score":total_score}
        })
    except Exception as e:
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = False
        state["report"]["pdf"]["error"] = str(e)
        state.setdefault("decision_log", []).append({
            "step":"pdf_node","result":"error",
            "time": datetime.now().isoformat(),
            "details":{"error":str(e)}
        })

    return state


# LangGraph 빌더
interview_builder = StateGraph(InterviewState)
interview_builder.add_node("stt_node", stt_node)
interview_builder.add_node("rewrite_agent", rewrite_agent)
interview_builder.add_node("rewrite_judge_agent", rewrite_judge_agent)
interview_builder.set_entry_point("stt_node")
interview_builder.add_edge("stt_node", "rewrite_agent")
interview_builder.add_edge("rewrite_agent", "rewrite_judge_agent")
interview_builder.add_conditional_edges(
    "rewrite_judge_agent", should_retry_rewrite,
    {"retry":"rewrite_agent", "done":"__end__"}
)
interview_flow_executor = interview_builder.compile()

final_builder = StateGraph(InterviewState)
final_builder.add_node("nonverbal_eval", nonverbal_evaluation_agent)
final_builder.add_node("evaluation_agent", evaluation_agent)
final_builder.add_node("evaluation_judge_agent", evaluation_judge_agent)
final_builder.add_node("pdf_node", pdf_node)
final_builder.set_entry_point("nonverbal_eval")
final_builder.add_edge("nonverbal_eval", "evaluation_agent")
final_builder.add_edge("evaluation_agent", "evaluation_judge_agent")
final_builder.add_conditional_edges(
    "evaluation_judge_agent", should_retry_evaluation,
    {"retry":"evaluation_agent", "continue":"pdf_node"}
)
# final_builder.add_channel("decision_log", LastValue())
final_report_flow_executor = final_builder.compile()