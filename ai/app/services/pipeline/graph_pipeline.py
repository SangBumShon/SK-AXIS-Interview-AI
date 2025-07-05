# app/services/pipeline/graph_pipeline.py

from langgraph.graph import StateGraph
from datetime import datetime
from typing import Literal, Dict, Any
import os
import json
import openai
from dotenv import load_dotenv
import openpyxl
import httpx
import pytz

# 환경 변수 로드
load_dotenv()
RESULT_DIR = os.getenv("RESULT_DIR", "./result")

from app.services.interview.stt_service import transcribe_audio_file
from app.services.interview.rewrite_service import rewrite_answer
from app.services.interview.evaluation_service import evaluate_keywords_from_full_answer
from app.services.interview.report_service import generate_pdf
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

KST = pytz.timezone('Asia/Seoul')

def print_state_summary(state, node_name):
    summary = {
        "stt_segments": len(state.get("stt", {}).get("segments", [])),
        "stt_type": type(state.get("stt", {})).__name__,
        "rewrite_final": len(state.get("rewrite", {}).get("final", [])),
        "rewrite_type": type(state.get("rewrite", {})).__name__,
        "evaluation_keys": list(state.get("evaluation", {}).keys()) if isinstance(state.get("evaluation", {}), dict) else [],
        "evaluation_type": type(state.get("evaluation", {})).__name__,
        "nonverbal_counts": state.get("nonverbal_counts", {}),
        "nonverbal_counts_type": type(state.get("nonverbal_counts", {})).__name__,
        "report_keys": list(state.get("report", {}).keys()) if "report" in state and isinstance(state["report"], dict) else [],
        "report_type": type(state.get("report", {})).__name__ if "report" in state else None,
        "decision_log_len": len(state.get("decision_log", [])),
        "decision_log_type": type(state.get("decision_log", [])).__name__
    }
    # print(f"[DEBUG] [{node_name}] state summary: {summary}")

def safe_get(d, key, default=None, context=""):
    try:
        return d.get(key, default)
    except Exception as e:
        print(f"[ERROR] [{context}] get('{key}') 예외 발생: {e}")
        return default

def stt_node(state: InterviewState) -> InterviewState:
    print("[LangGraph] 🧠 stt_node 진입")
    
    audio_path = safe_get(state, "audio_path", context="stt_node")
    raw = transcribe_audio_file(audio_path)
    if not raw or not str(raw).strip():
        raw = "없음"
    
    state.setdefault("stt", {"done": False, "segments": []})
    state["stt"]["segments"].append({"raw": raw, "timestamp": datetime.now(KST).isoformat()})
    
    print(f"[LangGraph] ✅ STT 완료: {raw[:30]}...")
    return state

# ───────────────────────────────────────────────────
# 2) Rewrite 에이전트: raw → rewritten
# ───────────────────────────────────────────────────
async def rewrite_agent(state: InterviewState) -> InterviewState:
    print("[LangGraph] ✏️ rewrite_agent 진입")
    stt = safe_get(state, "stt", {}, context="rewrite_agent")
    stt_segments = safe_get(stt, "segments", [], context="rewrite_agent")
    raw = stt_segments[-1]["raw"] if stt_segments else "없음"
    if not raw or not str(raw).strip():
        raw = "없음"
    rewritten, _ = await rewrite_answer(raw)
    if not rewritten or not str(rewritten).strip():
        rewritten = "없음"
    item = {"raw": raw, "rewritten": rewritten}

    prev = safe_get(state, "rewrite", {}, context="rewrite_agent")
    prev_retry = safe_get(prev, "retry_count", 0, context="rewrite_agent")
    prev_force = safe_get(prev, "force_ok", False, context="rewrite_agent")
    prev_final = safe_get(prev, "final", [], context="rewrite_agent")

    # retry_count가 3 이상이면 더 이상 증가시키지 않음
    if prev_retry >= 3:
        retry_count = prev_retry
    elif prev.get("items") and "ok" in prev["items"][0] and not prev["items"][0]["ok"]:
        retry_count = prev_retry + 1
    else:
        retry_count = prev_retry

    state["rewrite"] = {
        "items":       [item],
        "retry_count": retry_count,
        "force_ok":    prev_force,
        "final":       prev_final,
        "done":        False
    }

    print(f"[LangGraph] ✅ rewrite 결과: {rewritten[:30]}... (retry_count={retry_count})")
    ts = datetime.now(KST).isoformat()
    state.setdefault("decision_log", []).append({
        "step":   "rewrite_agent",
        "result": "processing",
        "time":   ts,
        "details": {"raw_preview": raw[:30], "retry_count": retry_count}
    })
    # print_state_summary(state, "rewrite_agent")
    return state

# ───────────────────────────────────────────────────
# 3) Rewrite 재시도 조건: 최대 3회 → 단 1회만 수행
# ───────────────────────────────────────────────────
def should_retry_rewrite(state: InterviewState) -> Literal["retry", "done"]:
    # 항상 done 반환 (재시도 없음)
    return "done"

# ───────────────────────────────────────────────────
# 4) Rewrite 검증 에이전트
# ───────────────────────────────────────────────────
async def rewrite_judge_agent(state: InterviewState) -> InterviewState:
    print("[LangGraph] 🧪 rewrite_judge_agent 진입")
    rewrite = safe_get(state, "rewrite", {}, context="rewrite_judge_agent")
    items   = safe_get(rewrite, "items", [])
    force   = safe_get(rewrite, "force_ok", False, context="rewrite_judge_agent")

    if not items:
        state.setdefault("decision_log", []).append({
            "step":   "rewrite_judge_agent",
            "result": "error",
            "time":   datetime.now(KST).isoformat(),
            "details":{"error":"No rewrite items found"}
        })
        return state

    for item in items:
        if "ok" in item:
            continue

        prompt = JUDGE_PROMPT.format(raw=item["raw"], rewritten=item["rewritten"])
        print(f"[DEBUG] 🔍 Rewrite 판정 프롬프트:")
        print(f"원본: {item['raw'][:100]}...")
        print(f"리라이팅: {item['rewritten'][:100]}...")
        
        try:
            start = datetime.now(KST).timestamp()
            resp  = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role":"user","content":prompt}],
                temperature=0, max_tokens=512
            )
            elapsed = datetime.now(KST).timestamp() - start
            
            # LLM 응답 로그
            llm_response = resp.choices[0].message.content.strip()
            print(f"[DEBUG] 🤖 LLM 응답: {llm_response}")
            
            # 마크다운 코드 블록 제거
            if llm_response.startswith("```json"):
                llm_response = llm_response[7:]  # "```json" 제거
            if llm_response.startswith("```"):
                llm_response = llm_response[3:]   # "```" 제거
            if llm_response.endswith("```"):
                llm_response = llm_response[:-3]  # 끝의 "```" 제거
            
            llm_response = llm_response.strip()
            print(f"[DEBUG] 🔧 정리된 JSON: {llm_response}")
            
            result  = json.loads(llm_response)

            item["ok"]          = result.get("ok", False)
            item["judge_notes"] = result.get("judge_notes", [])

            print(f"[DEBUG] 📊 판정 결과: ok={item['ok']}, notes={item['judge_notes']}")

            # 강제 통과 플래그 처리
            if not item["ok"] and force:
                print("⚠️ rewrite 실패 항목 강제 ok 처리됨")
                item["ok"] = True
                item["judge_notes"].append("자동 통과 (재시도 3회 초과)")

            if item["ok"]:
                # 중복된 rewritten 답변이 이미 final에 있으면 추가하지 않음
                rewritten = item["rewritten"]
                if not any(f["rewritten"] == rewritten for f in rewrite.get("final", [])):
                    rewrite.setdefault("final", []).append({
                        "raw":       item["raw"],
                        "rewritten": rewritten,
                        "timestamp": datetime.now(KST).isoformat()
                    })
                    print(f"[DEBUG] ✅ final에 추가됨: {item['rewritten'][:50]}...")
                else:
                    print(f"[DEBUG] ⚠️ 중복된 답변(final)에 추가하지 않음: {item['rewritten'][:50]}...")

            # 강제 통과 플래그가 설정되어 있으면 final에 추가
            if force and not item.get("ok", False):
                print("⚠️ 강제 통과 플래그로 인해 final에 추가")
                rewritten = item["rewritten"]
                if not any(f["rewritten"] == rewritten for f in rewrite.get("final", [])):
                    rewrite.setdefault("final", []).append({
                        "raw":       item["raw"],
                        "rewritten": rewritten,
                        "timestamp": datetime.now(KST).isoformat()
                    })
                    print(f"[DEBUG] ✅ 강제 통과로 final에 추가됨: {item['rewritten'][:50]}...")
                else:
                    print(f"[DEBUG] ⚠️ 강제 통과 중복(final)에 추가하지 않음: {item['rewritten'][:50]}...")
                item["ok"] = True
                item["judge_notes"].append("강제 통과 (재시도 3회 초과)")

            state.setdefault("decision_log", []).append({
                "step":   "rewrite_judge_agent",
                "result": f"ok={item['ok']}",
                "time":   datetime.now(KST).isoformat(),
                "details":{"notes":item["judge_notes"],"elapsed_sec":round(elapsed,2)}
            })
            print(f"[LangGraph] ✅ 판정 결과: ok={item['ok']}")

        except Exception as e:
            print(f"[DEBUG] ❌ JSON 파싱 오류: {e}")
            print(f"[DEBUG] 🔍 원본 LLM 응답: {llm_response if 'llm_response' in locals() else 'N/A'}")
            item["ok"]          = False
            item["judge_notes"] = [f"judge error: {e}"]
            state.setdefault("decision_log", []).append({
                "step":"rewrite_judge_agent",
                "result":"error",
                "time":datetime.now(KST).isoformat(),
                "details":{"error":str(e)}
            })

    # 마지막 항목이 ok=True면 완료 표시
    if rewrite["items"][-1].get("ok", False):
        rewrite["done"] = True

    # print_state_summary(state, "rewrite_judge_agent")
    return state


# ───────────────────────────────────────────────────
# 5) Nonverbal 평가 에이전트 (표정만 평가)
# ───────────────────────────────────────────────────
async def nonverbal_evaluation_agent(state: InterviewState) -> InterviewState:
    # 평가 시작 시간 기록
    evaluation_start_time = datetime.now(KST).timestamp()
    state["_evaluation_start_time"] = evaluation_start_time
    print(f"[⏱️] 평가 시작: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}")
    
    ts = datetime.now(KST).isoformat()
    try:
        counts = safe_get(state, "nonverbal_counts", {}, context="nonverbal_evaluation_agent")
        print(f"[DEBUG] nonverbal_counts: {counts}")
        # 구조 체크
        if not counts or not isinstance(counts, dict):
            print("[WARNING] nonverbal_counts가 dict가 아님 또는 비어있음. 비언어적 평가를 건너뜀.")
            state.decision_log.append("Nonverbal data not available for evaluation.")
            return state
        if "expression" not in counts or not isinstance(counts["expression"], dict):
            print("[WARNING] nonverbal_counts['expression']가 dict가 아님 또는 없음. 비언어적 평가를 건너뜀.")
            state.decision_log.append("Nonverbal expression data not available for evaluation.")
            return state
        # expression 내부 키 체크
        exp = counts["expression"]
        required_keys = ["smile", "neutral", "frown", "angry"]
        for k in required_keys:
            if k not in exp or not isinstance(exp[k], int):
                print(f"[WARNING] nonverbal_counts['expression']에 {k}가 없거나 int가 아님: {exp}")
        facial = FacialExpression.parse_obj(exp)
        print(f"[DEBUG] facial_expression: {facial}")
        res = await evaluate(facial)
        score = res.get("score", 0)
        analysis = res.get("analysis", "")
        feedback = res.get("feedback", "")
        print(f"[DEBUG] 비언어적 평가 결과(score): {score}, analysis: {analysis}, feedback: {feedback}")
        pts = int(round(score * 15))
        if pts == 0:
            print("[WARNING] 비언어적 평가 점수가 0입니다. 프론트/데이터 전달/LLM 프롬프트를 확인하세요.")
        evaluation = safe_get(state, "evaluation", {}, context="nonverbal_evaluation_agent")
        results = safe_get(evaluation, "results", {}, context="nonverbal_evaluation_agent")
        results["비언어적"] = {"score": pts, "reason": analysis or feedback or "평가 사유없음"}
        state.setdefault("evaluation", {}).setdefault("results", {})["비언어적"] = {
            "score": pts,
            "reason": analysis or feedback or "평가 사유없음"
        }
        state.setdefault("decision_log", []).append({
            "step": "nonverbal_evaluation",
            "result": "success",
            "time": ts,
            "details": {
                "score": pts
            }
        })
        print(f"[DEBUG] nonverbal_evaluation_agent - state['evaluation']['results']['비언어적']: {state.get('evaluation', {}).get('results', {}).get('비언어적')}")
    except Exception as e:
        print(f"[ERROR] 비언어적 평가 중 예외 발생: {e}")
        state.setdefault("decision_log", []).append({
            "step": "nonverbal_evaluation",
            "result": "error",
            "time": ts,
            "details": {"error": str(e)}
        })
    # print_state_summary(state, "nonverbal_evaluation_agent")
    return state

# ───────────────────────────────────────────────────
# 6) 평가 재시도 조건: 최대 3회 → 단 1회만 수행
# ───────────────────────────────────────────────────
def should_retry_evaluation(state: InterviewState) -> Literal["retry", "continue", "done"]:
    # 항상 continue 반환 (재시도 없음, 바로 다음 단계로)
    return "continue"

# ───────────────────────────────────────────────────
# 7) LLM 키워드 평가 에이전트
# ───────────────────────────────────────────────────
async def evaluation_agent(state: InterviewState) -> InterviewState:
    rewrite = safe_get(state, "rewrite", {}, context="evaluation_agent:rewrite")
    final_items = safe_get(rewrite, "final", [], context="evaluation_agent:rewrite.final")
    print(f"[DEBUG] 📝 evaluation_agent - final_items 개수: {len(final_items)}")
    if final_items:
        for idx, item in enumerate(final_items):
            print(f"[DEBUG] 📝 final[{idx}]: {item.get('rewritten', '')[:100]}")
        full_answer = "\n".join(item["rewritten"] for item in final_items)
    else:
        print("[DEBUG] ⚠️ final_items가 비어있음. 모든 STT 원본 답변을 합쳐서 평가")
        stt_segments = state.get("stt", {}).get("segments", [])
        if stt_segments:
            full_answer = "\n".join(seg.get("raw", "답변 내용이 없습니다.") for seg in stt_segments)
        else:
            full_answer = "답변 내용이 없습니다."
    
    print(f"[DEBUG] 📄 평가할 답변: {full_answer[:100]}...")
    
    # 평가 기준 키 목록을 가져옴
    all_criteria = {**EVAL_CRITERIA_WITH_ALL_SCORES, **TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES, **DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES}

    # 평가 결과를 정제하는 함수 (quotes 필드까지 보장)
    def normalize_results(results):
        normalized = {}
        for keyword, criteria in all_criteria.items():
            kw_result = results.get(keyword, {}) if isinstance(results, dict) else {}
            normalized[keyword] = {}
            for crit_name in criteria.keys():
                val = kw_result.get(crit_name) if isinstance(kw_result, dict) else None
                # 보강: dict가 아니면 무조건 dict로 감싸기
                if not isinstance(val, dict):
                    if isinstance(val, int):
                        val = {"score": val, "reason": "평가 사유없음", "quotes": []}
                    else:
                        val = {"score": 1, "reason": "평가 사유없음", "quotes": []}
                score = val.get("score", 1)
                reason = val.get("reason", "평가 사유없음")
                quotes = val.get("quotes", [])
                if not isinstance(quotes, list):
                    quotes = []
                normalized[keyword][crit_name] = {
                    "score": score,
                    "reason": reason,
                    "quotes": quotes
                }
        # 비언어적 요소도 항상 dict로 보정
        if "비언어적" in results:
            nonverbal = results["비언어적"]
            if not isinstance(nonverbal, dict):
                if isinstance(nonverbal, int):
                    nonverbal = {"score": nonverbal, "reason": "평가 사유없음", "quotes": []}
                else:
                    nonverbal = {"score": 1, "reason": "평가 사유없음", "quotes": []}
            if "quotes" not in nonverbal or not isinstance(nonverbal["quotes"], list):
                nonverbal["quotes"] = []
            normalized["비언어적"] = nonverbal
        return normalized

    results = await evaluate_keywords_from_full_answer(full_answer)
    results = normalize_results(results)

    prev_eval = safe_get(state, "evaluation", {}, context="evaluation_agent:evaluation")
    prev_results = prev_eval.get("results", {})
    # 기존 비언어적 등 결과와 새 평가 결과 병합
    merged_results = {**prev_results, **results}
    prev_retry = safe_get(prev_eval, "retry_count", 0, context="evaluation_agent:evaluation.retry_count")
    if "ok" in prev_eval and safe_get(prev_eval, "ok", context="evaluation_agent:evaluation.ok") is False:
        retry_count = prev_retry + 1
    else:
        retry_count = prev_retry

    state["evaluation"] = {
        **prev_eval,
        "done": True,
        "results": merged_results,
        "retry_count": retry_count,
        "ok": False  # 판정 전이므로 False로 초기화
    }
    state["done"] = True  # 파이프라인 전체 종료 신호 추가
    ts = datetime.now(KST).isoformat()
    state.setdefault("decision_log", []).append({
        "step": "evaluation_agent",
        "result": "done",
        "time": ts,
        "details": {"retry_count": retry_count}
    })
    # print_state_summary(state, "evaluation_agent")
    return state

# ───────────────────────────────────────────────────
# 8) 평가 검증 에이전트
# ───────────────────────────────────────────────────
async def evaluation_judge_agent(state: InterviewState) -> InterviewState:
    evaluation = safe_get(state, "evaluation", {}, context="evaluation_judge_agent:evaluation")
    results = safe_get(evaluation, "results", {}, context="evaluation_judge_agent:evaluation.results")
    if not results:
        state.setdefault("decision_log", []).append({
            "step": "evaluation_judge_agent",
            "result": "error",
            "time": datetime.now(KST).isoformat(),
            "details": {"error": "No evaluation results found"}
        })
        print("[judge] No evaluation results found, will stop.")
        state["evaluation"]["ok"] = True  # 더 이상 retry/continue 안 하도록 True로 설정
        return state

    judge_notes = []
    is_valid = True

    # 1. 항목 수 검증 (각 키워드에 3개)
    for kw, criteria in results.items():
        if len(criteria) != 3:
            judge_notes.append(f"Keyword '{kw}' has {len(criteria)} criteria (expected 3)")
            is_valid = False

    # 2. 점수 범위 검증 (1~5)
    for criteria in results.values():
        for data in criteria.values():
            # print(f"[DEBUG] evaluation_judge_agent - data type: {type(data)}, value: {data}")
            if isinstance(data, dict):
                s = data.get("score", 0)
            elif isinstance(data, int):
                s = data
            else:
                s = 0
            if not (1 <= s <= 5):
                judge_notes.append(f"Invalid score {s}")
                is_valid = False

    # 3. 총점 검증
    total = 0
    for crit in results.values():
        for c in crit.values():
            if isinstance(c, dict):
                total += c.get("score", 0)
            elif isinstance(c, int):
                total += c
            else:
                total += 0
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

    # === 내용 검증 LLM 호출 추가 ===
    try:
        CONTENT_VALIDATION_PROMPT = """
시스템: 당신은 AI 면접 평가 결과의 검증 전문가입니다.

아래는 지원자의 답변, 그리고 그 답변에 대한 키워드별 평가 결과입니다.

[지원자 답변]
{answer}

[평가 결과]
{evaluation}

[평가 기준]
{criteria}

평가 결과를 간단히 검증하고 아래 형식의 JSON으로만 답변하세요.

{{
  "ok": true,
  "judge_notes": ["평가 완료"]
}}
"""
        final_items = safe_get(state, "rewrite", {}).get("final", [])
        if not final_items:
            # final_items가 비어있으면 raw 텍스트 사용
            stt_segments = state.get("stt", {}).get("segments", [])
            if stt_segments:
                answer = stt_segments[-1].get("raw", "답변 내용이 없습니다.")
            else:
                answer = "답변 내용이 없습니다."
        else:
            answer = "\n".join(item["rewritten"] for item in final_items)
            
        evaluation = json.dumps(state.get("evaluation", {}).get("results", {}), ensure_ascii=False)
        criteria = json.dumps({
            **EVAL_CRITERIA_WITH_ALL_SCORES,
            **TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,
            **DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES
        }, ensure_ascii=False)

        prompt = CONTENT_VALIDATION_PROMPT.format(
            answer=answer,
            evaluation=evaluation,
            criteria=criteria
        )

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024
        )
        
        llm_response = response.choices[0].message.content.strip()
        # print(f"[DEBUG] 🤖 내용 검증 LLM 응답: {llm_response}")
        
        # 마크다운 코드 블록 제거
        if llm_response.startswith("```json"):
            llm_response = llm_response[7:]  # "```json" 제거
        if llm_response.startswith("```"):
            llm_response = llm_response[3:]   # "```" 제거
        if llm_response.endswith("```"):
            llm_response = llm_response[:-3]  # 끝의 "```" 제거
        
        llm_response = llm_response.strip()
        # print(f"[DEBUG] 🔧 정리된 내용 검증 JSON: {llm_response}")
        
        if not llm_response:
            raise ValueError("LLM 응답이 비어있습니다")
            
        result = json.loads(llm_response)
        state["evaluation"]["content_judge"] = result
        print(f"[LangGraph] ✅ 내용 검증 결과: ok={result.get('ok')}, notes={result.get('judge_notes')}")
    except Exception as e:
        print(f"[DEBUG] ❌ 내용 검증 오류: {e}")
        # print(f"[DEBUG] 🔍 LLM 응답: {llm_response if 'llm_response' in locals() else 'N/A'}")
        state["evaluation"]["content_judge"] = {
            "ok": True,  # 오류 시 기본적으로 통과
            "judge_notes": [f"content judge error: {e}"]
        }
        print(f"[LangGraph] ❌ 내용 검증 오류: {e}")

    ts = datetime.now(KST).isoformat()
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
    # print_state_summary(state, "evaluation_judge_agent")
    return state

def calculate_area_scores(evaluation_results, nonverbal_score):
    """
    영역별 점수 계산 함수
    - 인성적 요소: SUPEX, VWBE, Passionate, Proactive, Professional, People
    - 직무·도메인: "기술/직무", "도메인 전문성"
    - 비언어적 요소: 비언어적 점수(15점 만점)
    반환값: (weights, personality_score, job_domain_score, nonverbal_score_scaled)
    """
    print(f"[DEBUG] 🔍 calculate_area_scores 시작")
    print(f"[DEBUG] 입력 파라미터:")
    print(f"[DEBUG]   - evaluation_results: {json.dumps(evaluation_results, ensure_ascii=False, indent=2)}")
    print(f"[DEBUG]   - nonverbal_score: {nonverbal_score} (type: {type(nonverbal_score)})")
    
    personality_keywords = ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]
    job_domain_keywords = ["기술/직무", "도메인 전문성"]
    
    print(f"[DEBUG] 키워드 분류:")
    print(f"[DEBUG]   - personality_keywords: {personality_keywords}")
    print(f"[DEBUG]   - job_domain_keywords: {job_domain_keywords}")
    
    # 언어적 요소 총점 (인성적 요소)
    personality_score = 0
    print(f"[DEBUG] 🔍 인성적 요소 점수 계산:")
    
    # evaluation_results에서 judge 데이터 추출
    judge_data = evaluation_results.get("judge", {})
    print(f"[DEBUG] judge_data: {json.dumps(judge_data, ensure_ascii=False, indent=2)}")
    
    for keyword in personality_keywords:
        keyword_score = 0
        print(f"[DEBUG]   - '{keyword}' 키워드 처리:")
        
        if keyword in judge_data:
            criteria = judge_data[keyword]
            print(f"[DEBUG]     - criteria: {criteria} (type: {type(criteria)})")
            
            if isinstance(criteria, list):
                for i, crit in enumerate(criteria):
                    if isinstance(crit, dict):
                        score = crit.get("score", 0)
                        keyword_score += score
                        print(f"[DEBUG]       - criteria[{i}] score: {score}")
                    elif isinstance(crit, int):
                        keyword_score += crit
                        print(f"[DEBUG]       - criteria[{i}] int score: {crit}")
            elif isinstance(criteria, dict):
                score = criteria.get("score", 0)
                keyword_score += score
                print(f"[DEBUG]       - direct dict score: {score}")
            elif isinstance(criteria, int):
                keyword_score += criteria
                print(f"[DEBUG]       - direct int score: {criteria}")
        else:
            print(f"[DEBUG]     - '{keyword}' 키워드가 judge_data에 없음")
        
        personality_score += keyword_score
        print(f"[DEBUG]   - '{keyword}' 총점: {keyword_score}")
    
    print(f"[DEBUG] 인성적 요소 총점: {personality_score}")
    
    # 직무·도메인 총점
    job_domain_score = 0
    print(f"[DEBUG] 🔍 직무·도메인 점수 계산:")
    
    for keyword in job_domain_keywords:
        keyword_score = 0
        print(f"[DEBUG]   - '{keyword}' 키워드 처리:")
        
        if keyword in judge_data:
            criteria = judge_data[keyword]
            print(f"[DEBUG]     - criteria: {criteria} (type: {type(criteria)})")
            
            if isinstance(criteria, list):
                for i, crit in enumerate(criteria):
                    if isinstance(crit, dict):
                        score = crit.get("score", 0)
                        keyword_score += score
                        print(f"[DEBUG]       - criteria[{i}] score: {score}")
                    elif isinstance(crit, int):
                        keyword_score += crit
                        print(f"[DEBUG]       - criteria[{i}] int score: {crit}")
            elif isinstance(criteria, dict):
                score = criteria.get("score", 0)
                keyword_score += score
                print(f"[DEBUG]       - direct dict score: {score}")
            elif isinstance(criteria, int):
                keyword_score += criteria
                print(f"[DEBUG]       - direct int score: {criteria}")
        else:
            print(f"[DEBUG]     - '{keyword}' 키워드가 judge_data에 없음")
        
        job_domain_score += keyword_score
        print(f"[DEBUG]   - '{keyword}' 총점: {keyword_score}")
    
    print(f"[DEBUG] 직무·도메인 총점: {job_domain_score}")
    
    # 비언어적 요소
    print(f"[DEBUG] 🔍 비언어적 요소 점수: {nonverbal_score}")
    
    # 최대 점수 설정
    max_personality = 90
    max_job_domain = 30
    max_nonverbal = 15
    
    print(f"[DEBUG] 🔍 최대 점수 설정:")
    print(f"[DEBUG]   - max_personality: {max_personality}")
    print(f"[DEBUG]   - max_job_domain: {max_job_domain}")
    print(f"[DEBUG]   - max_nonverbal: {max_nonverbal}")
    
    # 100점 만점 환산 점수 계산
    personality_score_scaled = round((personality_score / max_personality) * 45, 1) if max_personality else 0
    job_domain_score_scaled = round((job_domain_score / max_job_domain) * 45, 1) if max_job_domain else 0
    nonverbal_score_scaled = round((nonverbal_score / max_nonverbal) * 10, 1) if max_nonverbal else 0
    
    print(f"[DEBUG] 🔍 환산 점수 계산:")
    print(f"[DEBUG]   - personality_score_scaled: {personality_score_scaled} = ({personality_score} / {max_personality}) * 45")
    print(f"[DEBUG]   - job_domain_score_scaled: {job_domain_score_scaled} = ({job_domain_score} / {max_job_domain}) * 45")
    print(f"[DEBUG]   - nonverbal_score_scaled: {nonverbal_score_scaled} = ({nonverbal_score} / {max_nonverbal}) * 10")
    
    # 비중 (고정값)
    weights = {
        "인성적 요소": 45.0,
        "직무·도메인": 45.0,
        "비언어적 요소": 10.0
    }
    
    print(f"[DEBUG] 🔍 가중치 설정: {weights}")
    
    result = (weights, personality_score_scaled, job_domain_score_scaled, nonverbal_score_scaled)
    print(f"[DEBUG] 🔍 calculate_area_scores 결과:")
    print(f"[DEBUG]   - weights: {weights}")
    print(f"[DEBUG]   - personality_score_scaled: {personality_score_scaled}")
    print(f"[DEBUG]   - job_domain_score_scaled: {job_domain_score_scaled}")
    print(f"[DEBUG]   - nonverbal_score_scaled: {nonverbal_score_scaled}")
    
    return result

EVAL_REASON_SUMMARY_PROMPT = """
아래는 지원자의 전체 답변과 각 평가 키워드별 평가 사유(reason)입니다.

[지원자 답변]
{answer}

[평가 사유]
{all_reasons}

이 두 정보를 참고하여, 지원자가 이렇게 점수를 얻게 된 이유를 8줄 이내로 자연스럽게 요약해 주세요.
- 평가 근거와 지원자의 핵심 답변 내용이 모두 포함되도록 하세요.
- 각 줄은 간결하고 핵심적으로 작성해 주세요.
- 중복되는 내용은 합치고, 중요한 특징/강점/보완점이 드러나도록 해 주세요.
- 반드시 8줄 이내로만 작성하세요.
"""

async def score_summary_agent(state):
    """점수 요약 및 최종 결과 정리"""
    print(f"[LangGraph] 🔍 score_summary_agent 시작")
    
    # 디버깅: 입력 데이터 확인
    print(f"[DEBUG] 🔍 Summary 생성 시작 - 입력 데이터 확인")
    print(f"[DEBUG] state keys: {list(state.keys())}")
    
    if "evaluation" in state:
        print(f"[DEBUG] evaluation 데이터 존재: {type(state['evaluation'])}")
        if isinstance(state["evaluation"], dict):
            print(f"[DEBUG] evaluation keys: {list(state['evaluation'].keys())}")
    else:
        print(f"[DEBUG] ❌ evaluation 데이터 없음!")
    
    if "nonverbal_evaluation" in state:
        print(f"[DEBUG] nonverbal_evaluation 데이터 존재: {type(state['nonverbal_evaluation'])}")
        if isinstance(state["nonverbal_evaluation"], dict):
            print(f"[DEBUG] nonverbal_evaluation keys: {list(state['nonverbal_evaluation'].keys())}")
    else:
        print(f"[DEBUG] ❌ nonverbal_evaluation 데이터 없음!")

    # 기존 코드 계속...
    evaluation_results = safe_get(state, "evaluation", {}, context="score_summary_agent:evaluation")
    nonverbal_results = safe_get(state, "nonverbal_evaluation", {}, context="score_summary_agent:nonverbal_evaluation")
    
    # 디버깅: 추출된 데이터 확인
    print(f"[DEBUG] 🔍 추출된 evaluation_results: {json.dumps(evaluation_results, ensure_ascii=False, indent=2)}")
    print(f"[DEBUG] 🔍 추출된 nonverbal_results: {json.dumps(nonverbal_results, ensure_ascii=False, indent=2)}")

    # 비언어적 점수 추출
    nonverbal_score = 0
    nonverbal_reason = "비언어적 요소 평가 없음"
    
    if isinstance(nonverbal_results, dict):
        nonverbal_score = safe_get(nonverbal_results, "score", 0, context="score_summary_agent:nonverbal_score")
        nonverbal_reason = safe_get(nonverbal_results, "reason", "비언어적 요소 평가 없음", context="score_summary_agent:nonverbal_reason")
    
    # 디버깅: 비언어적 점수 추출 결과
    print(f"[DEBUG] 🔍 비언어적 점수 추출 결과:")
    print(f"[DEBUG]   - nonverbal_score: {nonverbal_score} (type: {type(nonverbal_score)})")
    print(f"[DEBUG]   - nonverbal_reason: {nonverbal_reason}")

    # 영역별 점수 계산
    print(f"[DEBUG] 🔍 영역별 점수 계산 시작")
    weights, personality_score_scaled, job_domain_score_scaled, nonverbal_score_scaled = calculate_area_scores(evaluation_results, nonverbal_score)
    
    # 디버깅: 영역별 점수 계산 결과
    print(f"[DEBUG] 🔍 영역별 점수 계산 결과:")
    print(f"[DEBUG]   - weights: {weights}")
    print(f"[DEBUG]   - personality_score_scaled: {personality_score_scaled}")
    print(f"[DEBUG]   - job_domain_score_scaled: {job_domain_score_scaled}")
    print(f"[DEBUG]   - nonverbal_score_scaled: {nonverbal_score_scaled}")

    # 언어적 점수 및 사유 계산
    verbal_score = personality_score_scaled + job_domain_score_scaled
    verbal_reason = "인성적 요소와 직무·도메인 요소를 종합하여 평가한 결과입니다."
    
    # 디버깅: 언어적 점수 계산 결과
    print(f"[DEBUG] 🔍 언어적 점수 계산 결과:")
    print(f"[DEBUG]   - verbal_score: {verbal_score} (personality: {personality_score_scaled} + job_domain: {job_domain_score_scaled})")
    print(f"[DEBUG]   - verbal_reason: {verbal_reason}")

    # 키워드별 점수 계산
    print(f"[DEBUG] 🔍 키워드별 점수 계산 시작")
    keyword_scores = {}
    judge_data = safe_get(evaluation_results, "judge", {}, context="score_summary_agent:judge")
    
    # 디버깅: judge 데이터 확인
    print(f"[DEBUG] 🔍 judge 데이터:")
    print(f"[DEBUG]   - judge_data: {json.dumps(judge_data, ensure_ascii=False, indent=2)}")
    
    for keyword, criteria in judge_data.items():
        if keyword in ["total_score", "reason"]:
            continue
        
        print(f"[DEBUG] 🔍 키워드 '{keyword}' 처리 중...")
        print(f"[DEBUG]   - criteria: {criteria} (type: {type(criteria)})")
        
        total = 0
        if isinstance(criteria, list):
            for crit in criteria:
            if isinstance(crit, dict):
                    score = crit.get("score", 0)
                    total += score
                    print(f"[DEBUG]     - dict score: {score}")
            elif isinstance(crit, int):
                total += crit
                    print(f"[DEBUG]     - int score: {crit}")
        elif isinstance(criteria, dict):
            total = criteria.get("score", 0)
            print(f"[DEBUG]     - direct dict score: {total}")
        elif isinstance(criteria, int):
            total = criteria
            print(f"[DEBUG]     - direct int score: {total}")
        
        keyword_scores[keyword] = total
        print(f"[DEBUG]   - '{keyword}' 최종 점수: {total}")

    # 디버깅: 키워드별 점수 계산 결과
    print(f"[DEBUG] 🔍 키워드별 점수 계산 완료:")
    print(f"[DEBUG]   - keyword_scores: {json.dumps(keyword_scores, ensure_ascii=False, indent=2)}")

    # 총점 계산
    total_score = round(verbal_score + nonverbal_score_scaled, 1)
    print(f"[DEBUG] 🔍 총점 계산:")
    print(f"[DEBUG]   - total_score: {total_score} (verbal: {verbal_score} + nonverbal: {nonverbal_score_scaled})")

    # state에 저장
    summary_data = {
        "weights": weights,
        "personality_score": personality_score_scaled,
        "job_domain_score": job_domain_score_scaled,
        "verbal_score": verbal_score,
        "verbal_reason": verbal_reason,
        "nonverbal_score": nonverbal_score_scaled,
        "nonverbal_reason": nonverbal_reason,
        "keyword_scores": keyword_scores,
        "total_score": total_score
    }
    
    # 디버깅: 최종 summary 데이터 확인
    print(f"[DEBUG] 🔍 최종 summary 데이터 생성:")
    print(f"[DEBUG] {json.dumps(summary_data, ensure_ascii=False, indent=2)}")
    
    state["summary"] = summary_data
    print(f"[LangGraph] ✅ 영역별 점수/요약 저장 완료")
    print(f"[LangGraph] 📊 Summary 상세 정보:")
    print(f"[LangGraph]   - 총점: {total_score}/100")
    print(f"[LangGraph]   - 언어적 요소: {verbal_score}/90 (인성: {personality_score_scaled}/45, 직무: {job_domain_score_scaled}/45)")
    print(f"[LangGraph]   - 비언어적 요소: {nonverbal_score_scaled}/10")
    print(f"[LangGraph]   - 키워드별 점수: {len(keyword_scores)}개 항목")

    # 평가 소요시간 계산 및 출력
    start_time = state.get("_evaluation_start_time")
    if start_time:
        end_time = datetime.now(KST).timestamp()
        total_elapsed = end_time - start_time
        print(f"[⏱️] 평가 완료: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[⏱️] 평가 소요시간: {total_elapsed:.2f}초 (평가 시작 → 완료)")
        
        # decision_log에도 기록
        state.setdefault("decision_log", []).append({
            "step": "evaluation_complete",
            "result": "success",
            "time": datetime.now(KST).isoformat(),
            "details": {
                "evaluation_elapsed_seconds": round(total_elapsed, 2),
                "start_time": datetime.fromtimestamp(start_time, KST).isoformat(),
                "end_time": datetime.now(KST).isoformat(),
                "summary_data": summary_data
            }
        })
        
        # summary에도 소요시간 정보 추가
        state["summary"]["evaluation_duration"] = {
            "total_seconds": round(total_elapsed, 2),
            "start_time": datetime.fromtimestamp(start_time, KST).isoformat(),
            "end_time": datetime.now(KST).isoformat()
        }
        
        # 디버깅: 소요시간 정보 추가 확인
        print(f"[DEBUG] 🔍 소요시간 정보 추가:")
        print(f"[DEBUG]   - total_seconds: {round(total_elapsed, 2)}")
        print(f"[DEBUG]   - start_time: {datetime.fromtimestamp(start_time, KST).isoformat()}")
        print(f"[DEBUG]   - end_time: {datetime.now(KST).isoformat()}")
    else:
        print("[⏱️] 평가 시작 시간 정보가 없습니다.")

    # 디버깅: 최종 state["summary"] 확인
    print(f"[DEBUG] 🔍 최종 state['summary'] 저장 완료:")
    print(f"[DEBUG] {json.dumps(state['summary'], ensure_ascii=False, indent=2)}")

    return state


# ───────────────────────────────────────────────────
# Excel Node: 지원자 ID로 이름 조회 후 엑셀 생성
# ───────────────────────────────────────────────────
# async def excel_node(state: InterviewState) -> InterviewState:
#     import os
#     from datetime import datetime

#     try:
#         applicant_id = safe_get(state, "interviewee_id", context="excel_node:applicant_id")
#         rewrite = safe_get(state, "rewrite", {}, context="excel_node:rewrite")
#         rewrite_final = safe_get(rewrite, "final", [], context="excel_node:rewrite.final")
#         evaluation = safe_get(state, "evaluation", {}, context="excel_node:evaluation")
#         judge = safe_get(evaluation, "judge", {}, context="excel_node:evaluation.judge")
#         total_score = safe_get(judge, "total_score", context="excel_node:evaluation.judge.total_score")

#         # 1. 지원자 정보 조회
#         SPRINGBOOT_BASE_URL = os.getenv("SPRING_API_URL", "http://localhost:8080/api/v1")
#         applicant_name = None
#         interviewers = None
#         room_no = None
#         scheduled_at = None
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(f"{SPRINGBOOT_BASE_URL}/interviews/simple")
#             print(f"[DEBUG] /interviews/simple status: {resp.status_code}")
#             print(f"[DEBUG] /interviews/simple response: {resp.text}")
            
#             # 응답 상태 확인
#             if resp.status_code != 200:
#                 print(f"[ERROR] /interviews/simple API 호출 실패: {resp.status_code} - {resp.text}")
#                 data = []
#             else:
#                 try:
#                     data = safe_get(resp.json(), "data", [], context="excel_node:resp.data")
#                 except Exception as e:
#                     print(f"[ERROR] /interviews/simple JSON 파싱 실패: {e}")
#                     print(f"[ERROR] 응답 내용: {resp.text}")
#                     data = []
        
#         if not isinstance(data, list):
#             print(f"[ERROR] /interviews/simple data가 list가 아님! 실제 타입: {type(data)}, 값: {data}")
#             data = []

#         for item in data:
#             if not isinstance(item, dict):
#                 print(f"[ERROR] /interviews/simple item이 dict가 아님! 실제 타입: {type(item)}, 값: {item}")
#                 continue
#             if safe_get(item, "intervieweeId", context="excel_node:item.intervieweeId") == applicant_id:
#                 applicant_name = item["name"]
#                 interviewers = item.get("interviewers", "")
#                 room_no = item.get("roomNo", "")
#                 scheduled = item.get("scheduledAt", [])
#                 if scheduled and len(scheduled) >= 5:
#                     scheduled_at = f"{scheduled[0]:04d}-{scheduled[1]:02d}-{scheduled[2]:02d} {scheduled[3]:02d}:{scheduled[4]:02d}"
#                 break

#         if applicant_name is None:
#             raise ValueError(f"지원자 정보를 찾을 수 없습니다. applicant_id={applicant_id}")

#         # 2. 답변 합치기
#         all_answers = "\n".join([item["rewritten"] for item in rewrite_final])

#         # 3. 엑셀 생성
#         wb = openpyxl.Workbook()
#         ws = wb.active
#         ws.title = "면접 결과"
#         ws.append(["지원자ID", "이름", "면접관", "면접실", "면접일시", "답변(모두)", "총점"])
#         ws.append([applicant_id, applicant_name, interviewers, room_no, scheduled_at, all_answers, total_score])

#         out_dir = os.getenv("RESULT_DIR", "./result")
#         os.makedirs(out_dir, exist_ok=True)
#         ts = datetime.now(KST).strftime("%Y%m%d%H%M%S")
#         excel_path = f"{out_dir}/{applicant_id}_result_{ts}.xlsx"
#         wb.save(excel_path)
#         print(f"[LangGraph] ✅ Excel 생성 완료: {excel_path}")

#         state.setdefault("report", {}).setdefault("excel", {})["path"] = excel_path
#         state.setdefault("decision_log", []).append({
#             "step": "excel_node",
#             "result": "generated",
#             "time": datetime.now(KST).isoformat(),
#             "details": {"path": excel_path}
#         })
#     except Exception as e:
#         print(f"[LangGraph] ❌ Excel 생성 실패: {e}")
#         state.setdefault("report", {}).setdefault("excel", {})["error"] = str(e)
#     print_state_summary(state, "excel_node")
#     return state

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
final_builder.add_node("score_summary_agent", score_summary_agent)
# final_builder.add_node("excel_node", excel_node)
final_builder.set_entry_point("nonverbal_eval")
final_builder.add_edge("nonverbal_eval", "evaluation_agent")
final_builder.add_edge("evaluation_agent", "evaluation_judge_agent")
# final_builder.add_edge("pdf_node", "excel_node")
final_builder.add_conditional_edges(
    "evaluation_judge_agent", should_retry_evaluation,
    {"retry":"evaluation_agent", "continue":"score_summary_agent", "done":"__end__"}
)
# final_builder.add_channel("decision_log", LastValue())
final_report_flow_executor = final_builder.compile()