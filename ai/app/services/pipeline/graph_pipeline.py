# app/services/pipeline/graph_pipeline.py

from langgraph.graph import StateGraph
from datetime import datetime
import os
import asyncio

# 서비스 함수 임포트
from app.services.interview.stt_service import transcribe_audio_file
from app.services.interview.rewrite_service import rewrite_answer
from app.services.interview.evaluation_service import evaluate_keywords_from_full_answer
from app.services.interview.report_service import create_radar_chart, generate_pdf


# ──────────────── 상태(state) 구조 ────────────────
# 각 에이전트/노드 호출 시 인자로 전달됩니다.
# 지원자 단위로 독립 실행 가능하도록 설계되었습니다.
#
# state = {
#     "interviewee_id": str,                      # 지원자 ID
#     "interview_ended": bool,                    # 면접 종료 여부
#     "questions": List[str],                     # StartInterview 시 주입

#     "stt": {
#         "segments": [                           # 누적된 STT 결과 목록
#             {
#                 "raw": str,                     # 원문 전사 텍스트
#                 "timestamp": str                # 발화 시점 (선택사항: "00:01:23")
#               }
#         ]
#     },

#     "rewrite": {
#         "done": bool,                           # 전체 리라이팅 종료 여부
#         "items": [                              # 각 STT segment에 대한 rewrite 결과
#             {
#                 "raw": str,                     # 원본 STT 텍스트
#                 "rewritten": str,               # 의미 보존한 정제 텍스트
#                 "ok": bool | None,              # 의미 유지 평가 결과 (None → 평가 전)
#                 "judge_notes": List[str]        # 판단 근거 (문장 누락 등)
#             }
#         ],
#         "final": [                              # ok=True인 항목만 누적 (평가/리포트 대상)
#             {
#                 "raw": str,
#                 "rewritten": str,
#                 "timestamp": str                # (옵션) 해당 발화 시점
#             }
#         ]
#     },

#     "decision_log": [                           # 모든 처리 이력
#         {
#             "step": str,                        # 예: "rewrite_agent", "pdf_node"
#             "result": str,                      # 예: "done", "ok=False"
#             "time": str,                        # ISO timestamp
#             "details": dict                     # 단계별 메타데이터
#         }
#     ],

#     "evaluation": {
#         "done": bool,                           # 평가 완료 여부
#         "results": dict | None,                 # 각 역량 키워드별 점수
#         "ok": bool | None,                      # 평가 스코어 형식/범위 유효 여부
#         "judge_notes": List[str]                # 문제 발생 시 근거
#     },

#     "report": {
#         "pdf": {
#             "generated": bool,
#             "path": str | None                  # 생성된 PDF 파일 경로
#         },
#         "excel": {
#             "generated": bool,
#             "path": str | None                  # 생성된 Excel 파일 경로 (확장 예정)
#         }
#     },

#     # (옵션) 음성 파일 경로 (WebSocket 종료 시점에서 일시적으로 사용됨)
#     "audio_path": str | None
# }

# ──────────────── 노드 및 에이전트 정의 ────────────────

#  Available Nodes & Agents
# Nodes  : stt_node, append_node, pdf_node, excel_node
# Agents : rewrite_agent, judge_rewrite, evaluation_agent, judge_evaluation

def stt_node(state: dict) -> dict:
    audio_path = state.get("audio_path")
    interviewee_id = state["interviewee_id"]
    raw = transcribe_audio_file(audio_path)
    ts = datetime.now().isoformat()
    state.setdefault("stt", {"done": False, "segments": []})
    state["stt"]["segments"].append({"raw": raw, "timestamp": ts})
    state["decision_log"].append({
        "step": "stt_node",
        "result": "success",
        "time": ts,
        "details": {"segment": raw[:30]}
    })
    return state

async def rewrite_agent(state: dict) -> dict:
    """
    1) 가장 최근 STT segment 원문을 **의미 변화나 요약 없이** 정제(rewrite)
       - 문법 오류, 오탈자, 공백만 수정
    2) state['rewrite']['items']에 raw, rewritten, ok=None, judge_notes=[] 추가
    """
    raw = state["stt"]["segments"][-1]["raw"]
    rewritten, _ = await rewrite_answer(raw)
    item = {"raw": raw, "rewritten": rewritten, "ok": None, "judge_notes": []}
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

# rewrite judge agent
async def judge_rewrite(state: dict) -> dict:
    """
    1) raw vs rewritten 비교하여 ok/false 결정
    2) 마지막 rewrite item에 ok 및 judge_notes 업데이트
    """
    import json
    import openai
    item = state["rewrite"]["items"][-1]
    raw = item["raw"]
    rewritten = item["rewritten"]
    notes = []
    ok = True
    ratio = len(rewritten) / len(raw) if raw else 1.0
    if ratio < 0.8 or ratio > 1.2:
        ok = False
        notes.append(f"Length ratio {ratio:.2f} out of bounds (0.8~1.2)")
    if ok:
        prompt = f"""
시스템: 당신은 텍스트 리라이팅 평가 전문가입니다.
원본: \"{raw}\"
리라이팅: \"{rewritten}\"
1) 의미 보존
2) 과잉 축약/확장
3) 오탈자/문맥 오류
위 기준에 따라 JSON 형식으로 ok(bool)와 notes(list)를 반환하세요.
"""
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        try:
            data = json.loads(resp.choices[0].message.content)
            ok = data.get("ok", ok)
            notes.extend(data.get("notes", []))
        except json.JSONDecodeError:
            notes.append("GPT validation parse error")
    item["ok"] = ok
    item["judge_notes"] = notes
    ts = datetime.now().isoformat()
    state["decision_log"].append({
        "step": "judge_rewrite",
        "result": "pass" if ok else "fail",
        "time": ts,
        "details": {"notes": notes}
    })
    return state

# rewrite 결과물 추가 node
def append_node(state: dict) -> dict:
    state.setdefault("rewrite", {}).setdefault("items", [])
    state["rewrite"].setdefault("final", [])
    ts = datetime.now().isoformat()
    if not state["rewrite"]["items"]:
        state["decision_log"].append({"step": "append_node", "result": "skipped (no items)", "time": ts, "details": {}})
        return state
    latest_item = state["rewrite"]["items"][-1]
    if latest_item.get("ok") is True:
        state["rewrite"]["final"].append(latest_item)
        state["decision_log"].append({"step": "append_node", "result": "appended", "time": ts, "details": {"rewritten_preview": latest_item["rewritten"][:30]}})
    else:
        state["decision_log"].append({"step": "append_node", "result": "skipped (not ok)", "time": ts, "details": {}})
    return state


# 평가 agent
async def evaluation_agent(state: dict) -> dict:
    """
    평가 결과 생성
    """
    import json
    import openai
    from datetime import datetime
    import re

    # 평가할 텍스트 준비
    rewritten_items = state.get("rewrite", {}).get("final", [])
    if not rewritten_items:
        state.setdefault("evaluation", {})["done"] = False
        state.setdefault("evaluation", {})["error"] = "평가할 텍스트가 없습니다."
        return state

    # 평가할 텍스트를 하나의 문자열로 결합
    text_to_evaluate = "\n".join([item.get("rewritten", "") for item in rewritten_items])
    
    # 평가 프롬프트 생성
    prompt = f"""
시스템: 당신은 면접 평가 전문가입니다.
다음 면접 답변을 평가해주세요:

{text_to_evaluate}

다음 기준으로 평가해주세요:
1. 전문성 (0-5점)
2. 논리성 (0-5점)
3. 의사소통능력 (0-5점)
4. 문제해결능력 (0-5점)
5. 적극성 (0-5점)

JSON 형식으로만 반환해주세요 (마크다운이나 다른 형식 없이):
{{
    "전문성": {{"score": 점수, "reason": "평가 이유"}},
    "논리성": {{"score": 점수, "reason": "평가 이유"}},
    "의사소통능력": {{"score": 점수, "reason": "평가 이유"}},
    "문제해결능력": {{"score": 점수, "reason": "평가 이유"}},
    "적극성": {{"score": 점수, "reason": "평가 이유"}}
}}
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result_text = response.choices[0].message.content.strip()
        
        # 마크다운 코드 블록 제거
        result_text = re.sub(r'```json\s*|\s*```', '', result_text)
        
        # JSON 파싱 시도
        try:
            results = json.loads(result_text)
            # 점수 범위 검증
            for key, value in results.items():
                score = value.get("score", 0)
                if not isinstance(score, (int, float)) or score < 0 or score > 5:
                    value["score"] = max(0, min(5, float(score)))
                if not value.get("reason"):
                    value["reason"] = "평가 이유 없음"
            
            state.setdefault("evaluation", {})["results"] = results
            state["evaluation"]["done"] = True
            ts = datetime.now().isoformat()
            state.setdefault("decision_log", []).append({
                "step": "evaluation_agent",
                "result": "done",
                "time": ts,
                "details": {}
            })
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 오류: {str(e)}")
            print(f"원본 텍스트: {result_text}")
            # 기본 평가 결과 생성
            default_results = {
                "전문성": {"score": 3, "reason": "기본 점수 부여"},
                "논리성": {"score": 3, "reason": "기본 점수 부여"},
                "의사소통능력": {"score": 3, "reason": "기본 점수 부여"},
                "문제해결능력": {"score": 3, "reason": "기본 점수 부여"},
                "적극성": {"score": 3, "reason": "기본 점수 부여"}
            }
            state.setdefault("evaluation", {})["results"] = default_results
            state["evaluation"]["done"] = True
            state["evaluation"]["error"] = f"JSON 파싱 오류: {str(e)}"
            ts = datetime.now().isoformat()
            state.setdefault("decision_log", []).append({
                "step": "evaluation_agent",
                "result": "error",
                "time": ts,
                "details": {"error": str(e)}
            })
    except Exception as e:
        state.setdefault("evaluation", {})["done"] = False
        state["evaluation"]["error"] = str(e)
        ts = datetime.now().isoformat()
        state.setdefault("decision_log", []).append({
            "step": "evaluation_agent",
            "result": "error",
            "time": ts,
            "details": {"error": str(e)}
        })
    return state

# 평가 judge agent
async def judge_evaluation(state: dict) -> dict:
    """
    평가 결과 검증
    """
    import json
    import openai
    from jsonschema import validate, ValidationError
    from datetime import datetime

    results = state.get("evaluation", {}).get("results", {})
    if not results:
        state.setdefault("evaluation", {})["ok"] = False
        state.setdefault("evaluation", {})["judge_notes"] = ["평가 결과가 비어있습니다."]
        ts = datetime.now().isoformat()
        state.setdefault("decision_log", []).append({
            "step": "judge_evaluation",
            "result": "fail",
            "time": ts,
            "details": {"notes": ["평가 결과가 비어있습니다."]}
        })
        return state

    notes, ok = [], True
    schema = {
        "type": "object",
        "properties": {
            "전문성": {"type": "object", "required": ["score", "reason"]},
            "논리성": {"type": "object", "required": ["score", "reason"]},
            "의사소통능력": {"type": "object", "required": ["score", "reason"]},
            "문제해결능력": {"type": "object", "required": ["score", "reason"]},
            "적극성": {"type": "object", "required": ["score", "reason"]}
        },
        "required": ["전문성", "논리성", "의사소통능력", "문제해결능력", "적극성"]
    }

    try:
        validate(results, schema)
    except ValidationError as e:
        ok = False
        notes.append(f"스키마 오류: {e.message}")

    total = 0
    for comp, detail in results.items():
        score = detail.get("score", 0)
        if not isinstance(score, (int, float)) or score < 0 or score > 5:
            ok = False
            notes.append(f"{comp} 점수가 유효하지 않습니다: {score}")
        total += score

    if total < 0 or total > 25:
        ok = False
        notes.append(f"총점이 범위를 벗어났습니다: {total}")

    if ok:
        prompt = f"""
시스템: 당신은 면접 평가 검증 전문가입니다.
평가 결과:
{json.dumps(results, ensure_ascii=False, indent=2)}

이 평가가 적절한지 검증해주세요.
JSON 형식으로만 반환해주세요 (마크다운이나 다른 형식 없이):
{{
    "ok": true/false,
    "notes": ["검증 메시지"]
}}
"""
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            judge_result = json.loads(response.choices[0].message.content.strip())
            ok = judge_result.get("ok", False)
            notes.extend(judge_result.get("notes", []))
        except Exception as e:
            ok = False
            notes.append(f"검증 중 오류 발생: {str(e)}")

    state.setdefault("evaluation", {})["ok"] = ok
    state["evaluation"]["judge_notes"] = notes
    ts = datetime.now().isoformat()
    state.setdefault("decision_log", []).append({
        "step": "judge_evaluation",
        "result": "ok" if ok else "fail",
        "time": ts,
        "details": {"notes": notes}
    })
    return state

# 최종 레포트 pdf node
async def pdf_node(state: dict) -> dict:
    questions = state.get("questions", [])
    answers = [item["rewritten"] for item in state.get("rewrite", {}).get("final", [])]
    
    # 1) 평가 결과 keyword_results 변환
    evaluation_results = state.get("evaluation", {}).get("results", {})
    if not evaluation_results:
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = False
        state["report"]["pdf"]["error"] = "평가 결과가 없습니다."
        return state

    keyword_results = {
        kw: {
            "score": detail.get("score", 0),
            "reasons": detail.get("reason", "평가 이유 없음")
        }
        for kw, detail in evaluation_results.items()
    }

    # 2) QA 블록 텍스트 생성 (GPT 호출 포함)
    qa_blocks_text = await reconstruct_qa_blocks(questions, answers)
    
    cid = state.get("interviewee_id")
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    out_dir = './results'
    os.makedirs(out_dir, exist_ok=True)
    chart_path = os.path.join(out_dir, f"{cid}_chart_{ts}.png")
    pdf_path = os.path.join(out_dir, f"{cid}_report_{ts}.pdf")
    
    # 3) 차트 생성 및 PDF 생성
    try:
        create_radar_chart(keyword_results, chart_path)
        generate_pdf(
            keyword_results=keyword_results,
            chart_path=chart_path,
            output_path=pdf_path,
            interviewee_id=cid,
            qa_blocks_text=qa_blocks_text,
            total_score=sum(item.get("score", 0) for item in keyword_results.values())
        )
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = True
        state["report"]["pdf"]["path"] = pdf_path
        ts2 = datetime.now().isoformat()
        state.setdefault("decision_log", []).append({
            "step": "pdf_node", 
            "result": "generated", 
            "time": ts2, 
            "details": {"path": pdf_path}
        })
    except Exception as e:
        state.setdefault("report", {}).setdefault("pdf", {})["generated"] = False
        state["report"]["pdf"]["error"] = str(e)
        ts2 = datetime.now().isoformat()
        state.setdefault("decision_log", []).append({
            "step": "pdf_node", 
            "result": "error", 
            "time": ts2, 
            "details": {"error": str(e)}
        })
    return state

#  엑셀 node도 비동기로 변경
async def excel_node(state: dict) -> dict:
    state.setdefault("report", {})["excel"] = {"generated": False, "path": None}
    return state



# ──────────────── Flush 유틸리티: 평가 전 STT/Rewrite 잔여 처리 ────────────────
async def flush_pending_segments(state: dict) -> dict:
    """
    마지막 STT 항목이 아직 rewrite되지 않았다면 rewrite 처리 → 평가 전에 반드시 실행해야 함.
    """
    segments = state.get("stt", {}).get("segments", [])
    items = state.get("rewrite", {}).get("items", [])
    if len(segments) > len(items):
        state = await rewrite_agent(state)
        state = await judge_rewrite(state)
        state = append_node(state)
    if state.get("rewrite", {}).get("items"):
        last_item = state["rewrite"]["items"][-1]
        if last_item.get("ok") is True:
            state["rewrite"]["done"] = True
    return state


# ────────────────────────────────────────────────────────────────
# LangGraph 파이프라인 정의 (interview_flow / final_report_flow)
# ────────────────────────────────────────────────────────────────

"""
🎙️ 한 발화 종료 시 호출되는 처리 흐름입니다.

    [실행 순서]

    1. STT Node
       - state['audio_path']에 해당하는 음성을 Whisper로 전사
       - 결과는 state['stt']['segments']에 누적 저장

    2. Rewrite Agent
       - 가장 최근 STT segment를 문법적으로 정제 (의미 변화 없이)
       - 정제 결과는 state['rewrite']['items']에 추가됨

    3. Judge Rewrite Agent
       - 정제된 문장이 원문 의미를 유지하는지 평가
       - 평가 결과 (ok 여부 및 근거)는 state['rewrite']['items'][-1]에 기록됨

    4. (선택적) Retry Logic
       - 만약 ok=False일 경우, Rewrite → Judge를 최대 N회 재실행

    5. Append Node
       - ok=True인 segment만 state['rewrite']['final']에 최종 누적

    [구현 가이드]
    - 각 단계는 아래 방식으로 호출합니다:
        state = graph.run_node("stt_node", state)
        state = await graph.run_agent("rewrite_agent", state)
        ...
    """

# interview_flow_executor
interview_builder = StateGraph(dict)
interview_builder.add_node("stt_node", stt_node)
interview_builder.add_node("rewrite_agent", rewrite_agent)
interview_builder.add_node("judge_rewrite", judge_rewrite)
interview_builder.add_node("append_node", append_node)
interview_builder.set_entry_point("stt_node")
interview_builder.add_edge("stt_node", "rewrite_agent")
interview_builder.add_edge("rewrite_agent", "judge_rewrite")
interview_builder.add_edge("judge_rewrite", "append_node")
interview_flow_executor = interview_builder.compile()





# final_report_flow_executor
"""
    📄 면접 종료 시 실행되는 전체 평가 및 보고서 생성 흐름입니다.

    [실행 순서]

    0. flush_pending_segments
       - 아직 append되지 않은 rewrite 후보가 있다면 처리
       - state['rewrite']['final'] 최신 상태를 보장

    1. Evaluation Agent
       - state['rewrite']['final'] 기준으로 GPT 평가 수행
       - 결과는 state['evaluation']['results']에 저장

    2. Judge Evaluation Agent
       - 평가 점수 형식 및 범위를 검증
       - 문제가 있다면 state['evaluation']['ok'] = False
       - 평가 사유는 state['evaluation']['judge_notes']에 기록

    3. (선택적) Retry Logic
       - ok=False일 경우, Evaluation → Judge를 최대 N회 반복

    4. PDF Node
       - Radar Chart + 평가 사유를 포함한 PDF 리포트 생성
       - 결과 경로는 state['report']['pdf']['path']에 저장됨

    5. Excel Node (미구현)
       - 질문, 답변, 점수, 평가 이유를 Excel로 저장 (향후 확장)

    [구현 가이드]
    - 각 단계는 아래 방식으로 호출합니다:
        state = await flush_pending_segments(state)
        state = await graph.run_agent("evaluation_agent", state)
        ...
    """
final_builder = StateGraph(dict)
final_builder.add_node("flush_node", flush_pending_segments)
final_builder.add_node("evaluation_agent", evaluation_agent)
final_builder.add_node("judge_evaluation", judge_evaluation)
final_builder.add_node("pdf_node", pdf_node)
final_builder.add_node("excel_node", excel_node)
final_builder.set_entry_point("flush_node")
final_builder.add_edge("flush_node", "evaluation_agent")
final_builder.add_edge("evaluation_agent", "judge_evaluation")
final_builder.add_edge("judge_evaluation", "pdf_node")
final_builder.add_edge("pdf_node", "excel_node")
final_report_flow_executor = final_builder.compile()
# app/services/pipeline/graph_pipeline.py

# from langgraph.graph import StateGraph
# from datetime import datetime
# import os
# import asyncio

# # 서비스 함수 임포트
# from app.services.interview.stt_service import transcribe_audio_file
# from app.services.interview.rewrite_service import rewrite_answer
# from app.services.interview.evaluation_service import evaluate_keywords_from_full_answer
# from app.services.interview.report_service import create_radar_chart, generate_pdf
# from app.services.interview.qa_reconstructor import reconstruct_qa_blocks

# # ──────────────── 상태(state) 구조 ────────────────
# # 각 에이전트/노드 호출 시 인자로 전달됩니다.
# # 지원자 단위로 독립 실행 가능하도록 설계되었습니다.
# #
# # state = {
# #     "interviewee_id": str,                      # 지원자 ID
# #     "interview_ended": bool,                    # 면접 종료 여부
# #     "questions": List[str],                     # StartInterview 시 주입

# #     "stt": {
# #         "segments": [                           # 누적된 STT 결과 목록
# #             {
# #                 "raw": str,                     # 원문 전사 텍스트
# #                 "timestamp": str                # 발화 시점 (선택사항: "00:01:23")
# #               }
# #         ]
# #     },

# #     "rewrite": {
# #         "done": bool,                           # 전체 리라이팅 종료 여부
# #         "items": [                              # 각 STT segment에 대한 rewrite 결과
# #             {
# #                 "raw": str,                     # 원본 STT 텍스트
# #                 "rewritten": str,               # 의미 보존한 정제 텍스트
# #                 "ok": bool | None,              # 의미 유지 평가 결과 (None → 평가 전)
# #                 "judge_notes": List[str]        # 판단 근거 (문장 누락 등)
# #             }
# #         ],
# #         "final": [                              # ok=True인 항목만 누적 (평가/리포트 대상)
# #             {
# #                 "raw": str,
# #                 "rewritten": str,
# #                 "timestamp": str                # (옵션) 해당 발화 시점
# #             }
# #         ]
# #     },

# #     "decision_log": [                           # 모든 처리 이력
# #         {
# #             "step": str,                        # 예: "rewrite_agent", "pdf_node"
# #             "result": str,                      # 예: "done", "ok=False"
# #             "time": str,                        # ISO timestamp
# #             "details": dict                     # 단계별 메타데이터
# #         }
# #     ],

# #     "evaluation": {
# #         "done": bool,                           # 평가 완료 여부
# #         "results": dict | None,                 # 각 역량 키워드별 점수
# #         "ok": bool | None,                      # 평가 스코어 형식/범위 유효 여부
# #         "judge_notes": List[str]                # 문제 발생 시 근거
# #     },

# #     "report": {
# #         "pdf": {
# #             "generated": bool,
# #             "path": str | None                  # 생성된 PDF 파일 경로
# #         },
# #         "excel": {
# #             "generated": bool,
# #             "path": str | None                  # 생성된 Excel 파일 경로 (확장 예정)
# #         }
# #     },

# #     # (옵션) 음성 파일 경로 (WebSocket 종료 시점에서 일시적으로 사용됨)
# #     "audio_path": str | None
# # }

# # ──────────────── 노드 및 에이전트 정의 ────────────────

# #  Available Nodes & Agents
# # Nodes  : stt_node, append_node, pdf_node, excel_node
# # Agents : rewrite_agent, judge_rewrite, evaluation_agent, judge_evaluation

# def stt_node(state: dict) -> dict:
#     audio_path = state.get("audio_path")
#     interviewee_id = state["interviewee_id"]
#     raw = transcribe_audio_file(audio_path)
#     ts = datetime.now().isoformat()
#     state.setdefault("stt", {"done": False, "segments": []})
#     state["stt"]["segments"].append({"raw": raw, "timestamp": ts})
#     state["decision_log"].append({
#         "step": "stt_node",
#         "result": "success",
#         "time": ts,
#         "details": {"segment": raw[:30]}
#     })
#     return state

# async def rewrite_agent(state: dict) -> dict:
#     """
#     1) 가장 최근 STT segment 원문을 **의미 변화나 요약 없이** 정제(rewrite)
#        - 문법 오류, 오탈자, 공백만 수정
#     2) state['rewrite']['items']에 raw, rewritten, ok=None, judge_notes=[] 추가
#     """
#     raw = state["stt"]["segments"][-1]["raw"]
#     rewritten, _ = await rewrite_answer(raw)
#     item = {"raw": raw, "rewritten": rewritten, "ok": None, "judge_notes": []}
#     state.setdefault("rewrite", {"done": False, "items": []})
#     state["rewrite"]["items"].append(item)
#     ts = datetime.now().isoformat()
#     state["decision_log"].append({
#         "step": "rewrite_agent",
#         "result": "processing",
#         "time": ts,
#         "details": {"raw_preview": raw[:30]}
#     })
#     return state

# # rewrite judge agent
# async def judge_rewrite(state: dict) -> dict:
#     """
#     1) raw vs rewritten 비교하여 ok/false 결정
#     2) 마지막 rewrite item에 ok 및 judge_notes 업데이트
#     """
#     import json
#     import openai
#     item = state["rewrite"]["items"][-1]
#     raw = item["raw"]
#     rewritten = item["rewritten"]
#     notes = []
#     ok = True
#     ratio = len(rewritten) / len(raw) if raw else 1.0
#     if ratio < 0.8 or ratio > 1.2:
#         ok = False
#         notes.append(f"Length ratio {ratio:.2f} out of bounds (0.8~1.2)")
#     if ok:
#         prompt = f"""
# 시스템: 당신은 텍스트 리라이팅 평가 전문가입니다.
# 원본: \"{raw}\"
# 리라이팅: \"{rewritten}\"
# 1) 의미 보존
# 2) 과잉 축약/확장
# 3) 오탈자/문맥 오류
# 위 기준에 따라 JSON 형식으로 ok(bool)와 notes(list)를 반환하세요.
# """
#         resp = await openai.ChatCompletion.acreate(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0
#         )
#         try:
#             data = json.loads(resp.choices[0].message.content)
#             ok = data.get("ok", ok)
#             notes.extend(data.get("notes", []))
#         except json.JSONDecodeError:
#             notes.append("GPT validation parse error")
#     item["ok"] = ok
#     item["judge_notes"] = notes
#     ts = datetime.now().isoformat()
#     state["decision_log"].append({
#         "step": "judge_rewrite",
#         "result": "pass" if ok else "fail",
#         "time": ts,
#         "details": {"notes": notes}
#     })
#     return state

# # rewrite 결과물 추가 node
# def append_node(state: dict) -> dict:
#     state.setdefault("rewrite", {}).setdefault("items", [])
#     state["rewrite"].setdefault("final", [])
#     ts = datetime.now().isoformat()
#     if not state["rewrite"]["items"]:
#         state["decision_log"].append({"step": "append_node", "result": "skipped (no items)", "time": ts, "details": {}})
#         return state
#     latest_item = state["rewrite"]["items"][-1]
#     if latest_item.get("ok") is True:
#         state["rewrite"]["final"].append(latest_item)
#         state["decision_log"].append({"step": "append_node", "result": "appended", "time": ts, "details": {"rewritten_preview": latest_item["rewritten"][:30]}})
#     else:
#         state["decision_log"].append({"step": "append_node", "result": "skipped (not ok)", "time": ts, "details": {}})
#     return state


# # 평가 agent
# async def evaluation_agent(state: dict) -> dict:
#     final_items = state.get("rewrite", {}).get("final", [])
#     all_text = "\n".join([it["rewritten"] for it in final_items])
#     results = await evaluate_keywords_from_full_answer(all_text)
#     state["evaluation"] = {"done": True, "results": results, "ok": None, "judge_notes": []}
#     ts = datetime.now().isoformat()
#     state["decision_log"].append({"step": "evaluation_agent", "result": "done", "time": ts, "details": {}})
#     return state

# # 평가 judge agent
# async def judge_evaluation(state: dict) -> dict:
#     """
#     평가 결과 검증
#     """
#     import json
#     import openai
#     from jsonschema import validate, ValidationError
#     results = state.get("evaluation", {}).get("results", {})
#     notes, ok = [], True
#     schema = {"type": "object", "additionalProperties": {"type": "object"}}
#     try:
#         validate(results, schema)
#     except ValidationError as e:
#         ok = False
#         notes.append(f"Schema error: {e.message}")
#     total = 0
#     for comp, detail in results.items():
#         scores = detail.get("scores", {})
#         comp_sum = sum(s.get("score", 0) for s in scores.values())
#         if comp_sum < 3 or comp_sum > 15:
#             ok = False
#             notes.append(f"{comp} sum out of range: {comp_sum}")
#         total += comp_sum
#     if total < 0 or total > 150:
#         ok = False
#         notes.append(f"Total score out of 0~150: {total}")
#     if ok:
#         prompt = f"""
# 시스템: 당신은 면접 평가 검증 전문가입니다.
# 사용자 평가 결과 JSON:
# {json.dumps(results)}
# 기준에 맞는지 JSON 형태로 { '{"ok":bool, "notes": [str]}' } 반환하세요.
# """
#         resp = await openai.ChatCompletion.acreate(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0
#         )
#         try:
#             data = json.loads(resp.choices[0].message.content)
#             ok = data.get("ok", ok)
#             notes.extend(data.get("notes", []))
#         except json.JSONDecodeError:
#             ok = False
#             notes.append("GPT eval parse error")
#     state["evaluation"]["ok"] = ok
#     state["evaluation"]["judge_notes"] = notes
#     ts = datetime.now().isoformat()
#     state["decision_log"].append({"step": "judge_evaluation", "result": "pass" if ok else "fail", "time": ts, "details": {"notes": notes}})
#     return state

# # 최종 레포트 pdf node
# def pdf_node(state: dict) -> dict:
#     questions = state.get("questions", [])
#     answers = [item["rewritten"] for item in state.get("rewrite", {}).get("final", [])]
    
#     # 1) 평가 결과 keyword_results 변환
#     keyword_results = {
#         kw: {
#             "score": sum(v["score"] for v in det["scores"].values()),
#             "reasons": "\n".join(v.get("reason", "") for v in det["scores"].values())
#         }
#         for kw, det in state.get("evaluation", {}).get("results", {}).items()
#     }

#     # 2) QA 블록 텍스트 생성 (GPT 호출 포함, 주의!)
#     qa_blocks_text = asyncio.run(reconstruct_qa_blocks(questions, answers))
#     cid = state.get("interviewee_id")
#     ts = datetime.now().strftime('%Y%m%d%H%M%S')
#     out_dir = './results'
#     os.makedirs(out_dir, exist_ok=True)
#     chart_path = os.path.join(out_dir, f"{cid}_chart_{ts}.png")
#     pdf_path = os.path.join(out_dir, f"{cid}_report_{ts}.pdf")
    
#     generate_pdf(
#         keyword_results=keyword_results,
#         chart_path=chart_path,
#         output_path=pdf_path,
#         interviewee_id=cid,
#         qa_blocks_text=qa_blocks_text,
#         total_score=sum(item.get("score", 0) for item in keyword_results.values())
#     )
#     state.setdefault("report", {}).setdefault("pdf", {})["generated"] = True
#     state["report"]["pdf"]["path"] = pdf_path
#     ts2 = datetime.now().isoformat()
#     state.setdefault("decision_log", []).append({"step": "pdf_node", "result": "generated", "time": ts2, "details": {"path": pdf_path}})
#     return state

# #  엑셀 node
# def excel_node(state: dict) -> dict:
#     state.setdefault("report", {})["excel"] = {"generated": False, "path": None}
#     return state



# # ──────────────── Flush 유틸리티: 평가 전 STT/Rewrite 잔여 처리 ────────────────
# async def flush_pending_segments(state: dict) -> dict:
#     """
#     마지막 STT 항목이 아직 rewrite되지 않았다면 rewrite 처리 → 평가 전에 반드시 실행해야 함.
#     """
#     segments = state.get("stt", {}).get("segments", [])
#     items = state.get("rewrite", {}).get("items", [])
#     if len(segments) > len(items):
#         state = await rewrite_agent(state)
#         state = await judge_rewrite(state)
#         state = append_node(state)
#     if state.get("rewrite", {}).get("items"):
#         last_item = state["rewrite"]["items"][-1]
#         if last_item.get("ok") is True:
#             state["rewrite"]["done"] = True
#     return state


# # ────────────────────────────────────────────────────────────────
# # LangGraph 파이프라인 정의 (interview_flow / final_report_flow)
# # ────────────────────────────────────────────────────────────────

# """
# 🎙️ 한 발화 종료 시 호출되는 처리 흐름입니다.

#     [실행 순서]

#     1. STT Node
#        - state['audio_path']에 해당하는 음성을 Whisper로 전사
#        - 결과는 state['stt']['segments']에 누적 저장

#     2. Rewrite Agent
#        - 가장 최근 STT segment를 문법적으로 정제 (의미 변화 없이)
#        - 정제 결과는 state['rewrite']['items']에 추가됨

#     3. Judge Rewrite Agent
#        - 정제된 문장이 원문 의미를 유지하는지 평가
#        - 평가 결과 (ok 여부 및 근거)는 state['rewrite']['items'][-1]에 기록됨

#     4. (선택적) Retry Logic
#        - 만약 ok=False일 경우, Rewrite → Judge를 최대 N회 재실행

#     5. Append Node
#        - ok=True인 segment만 state['rewrite']['final']에 최종 누적

#     [구현 가이드]
#     - 각 단계는 아래 방식으로 호출합니다:
#         state = graph.run_node("stt_node", state)
#         state = await graph.run_agent("rewrite_agent", state)
#         ...
#     """

# # interview_flow_executor
# # interview_flow_executor
# interview_builder = StateGraph(dict)
# interview_builder.add_node("stt_node", stt_node)
# interview_builder.add_node("rewrite_agent", rewrite_agent)
# interview_builder.add_node("judge_rewrite", judge_rewrite)
# interview_builder.add_node("append_node", append_node)
# interview_builder.set_entry_point("stt_node")
# interview_builder.add_edge("stt_node", "rewrite_agent")
# interview_builder.add_edge("rewrite_agent", "judge_rewrite")
# interview_builder.add_edge("judge_rewrite", "append_node")
# interview_flow_executor = interview_builder.compile()




# # final_report_flow_executor
# """
#     📄 면접 종료 시 실행되는 전체 평가 및 보고서 생성 흐름입니다.

#     [실행 순서]

#     0. flush_pending_segments
#        - 아직 append되지 않은 rewrite 후보가 있다면 처리
#        - state['rewrite']['final'] 최신 상태를 보장

#     1. Evaluation Agent
#        - state['rewrite']['final'] 기준으로 GPT 평가 수행
#        - 결과는 state['evaluation']['results']에 저장

#     2. Judge Evaluation Agent
#        - 평가 점수 형식 및 범위를 검증
#        - 문제가 있다면 state['evaluation']['ok'] = False
#        - 평가 사유는 state['evaluation']['judge_notes']에 기록

#     3. (선택적) Retry Logic
#        - ok=False일 경우, Evaluation → Judge를 최대 N회 반복

#     4. PDF Node
#        - Radar Chart + 평가 사유를 포함한 PDF 리포트 생성
#        - 결과 경로는 state['report']['pdf']['path']에 저장됨

#     5. Excel Node (미구현)
#        - 질문, 답변, 점수, 평가 이유를 Excel로 저장 (향후 확장)

#     [구현 가이드]
#     - 각 단계는 아래 방식으로 호출합니다:
#         state = await flush_pending_segments(state)
#         state = await graph.run_agent("evaluation_agent", state)
#         ...
#     """
# final_builder = StateGraph(dict)
# final_builder.add_node("flush_node", flush_pending_segments)
# final_builder.add_node("evaluation_agent", evaluation_agent)
# final_builder.add_node("judge_evaluation", judge_evaluation)
# final_builder.add_node("pdf_node", pdf_node)
# final_builder.add_node("excel_node", excel_node)
# final_builder.set_entry_point("flush_node")
# final_builder.add_edge("flush_node", "evaluation_agent")
# final_builder.add_edge("evaluation_agent", "judge_evaluation")
# final_builder.add_edge("judge_evaluation", "pdf_node")
# final_builder.add_edge("pdf_node", "excel_node")
# final_report_flow_executor = final_builder.compile()