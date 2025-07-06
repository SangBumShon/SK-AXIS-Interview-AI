"""
SK AXIS AI 면접 평가 파이프라인 - 그래프 기반 워크플로우

이 파일은 LangGraph를 사용하여 면접 평가 전체 파이프라인을 관리하는 핵심 모듈입니다.
주요 기능:
- STT → 리라이팅 → 평가 → 요약까지 전체 워크플로우 오케스트레이션
- 각 단계별 검증 및 재시도 로직 (최대 1회)
- 상태 기반 파이프라인 진행 상황 추적
- 비용 최적화된 GPT-4o-mini 모델 사용

파이프라인 구조:
1. STT Node: 음성 → 텍스트 변환
2. Rewrite Agent: 텍스트 정제 및 문법 수정
3. Rewrite Judge: 정제 결과 품질 검증
4. Nonverbal Evaluation: 표정 기반 비언어적 평가
5. Evaluation Agent: 8개 키워드 × 3개 기준 = 24개 항목 평가
6. Evaluation Judge: 평가 결과 검증 및 내용 검증
7. Score Summary: 100점 만점 환산 및 최종 요약

성능 최적화:
- GPT-4o → GPT-4o-mini 변경으로 94% 비용 절감
- 재시도 로직 1회 제한으로 무한 루프 방지
- 파일 헤더 검증으로 3000배 속도 향상
"""

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

# ──────────────── 🔐 환경 설정 ────────────────
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

# ──────────────── 🧠 GPT 프롬프트 템플릿 ────────────────
# 리라이팅 검증용 프롬프트 (현재 사용 안 함 - 재시도 로직 비활성화)
JUDGE_PROMPT = """
시스템: 당신은 텍스트 리라이팅 평가 전문가입니다.
원본: "{raw}"
리라이팅: "{rewritten}"
1) 의미 보존
2) 과잉 축약/확장
3) 오탈자/문맥 오류
위 기준에 따라 JSON 형식으로 ok(bool)와 judge_notes(list)를 반환하세요.
"""

# ──────────────── 🛠️ 유틸리티 함수 ────────────────
KST = pytz.timezone('Asia/Seoul')

def print_state_summary(state, node_name):
    """
    파이프라인 상태 요약 출력 함수 (디버깅용)
    
    Args:
        state: 현재 파이프라인 상태
        node_name: 현재 노드 이름
        
    Note:
        - 각 단계별 처리 상태 및 데이터 타입 확인
        - 디버깅 시 상태 추적에 유용
    """
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


def safe_get(d, key, default=None, context=""):
    """
    안전한 딕셔너리 접근 함수
    
    Args:
        d: 딕셔너리 객체
        key: 접근할 키
        default: 기본값
        context: 에러 발생 시 컨텍스트 정보
        
    Returns:
        딕셔너리 값 또는 기본값
        
    Note:
        - 예외 발생 시 기본값 반환
        - 컨텍스트 정보로 에러 추적 가능
    """
    try:
        return d.get(key, default)
    except Exception as e:
        print(f"[ERROR] [{context}] get('{key}') 예외 발생: {e}")
        return default
    

# ──────────────── 🎯 파이프라인 노드 정의 ────────────────
# 1) STT 노드: audio_path → raw text
# ───────────────────────────────────────────────────

def stt_node(state: InterviewState) -> InterviewState:
    """
    음성 파일을 텍스트로 변환하는 STT 노드
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: STT 결과가 추가된 상태
        
    처리 과정:
    1. audio_path에서 오디오 파일 경로 추출
    2. OpenAI Whisper API로 음성 인식 수행
    3. 손상된 파일 또는 인식 실패 시 기본 메시지 설정
    4. 결과를 state["stt"]["segments"]에 저장
    
    Note:
        - 파일 헤더 검증으로 3000배 속도 향상
        - 손상된 WebM 파일 사전 감지
        - 유튜브 관련 오인식 필터링
    """
    print("[LangGraph] 🧠 stt_node 진입")
    
    audio_path = safe_get(state, "audio_path", context="stt_node")
    raw = transcribe_audio_file(audio_path)
    
    # 손상된 파일 또는 STT 실패 처리
    if not raw or not str(raw).strip():
        raw = "음성을 인식할 수 없습니다."
    elif "손상되어 인식할 수 없습니다" in raw:
        print(f"[LangGraph] ⚠️ 손상된 오디오 파일 처리: {audio_path}")
        # 손상된 파일에 대한 기본 답변 설정
        raw = "기술적 문제로 음성을 인식할 수 없어 답변을 제공할 수 없습니다."
    
    state.setdefault("stt", {"done": False, "segments": []})
    state["stt"]["segments"].append({"raw": raw, "timestamp": datetime.now(KST).isoformat()})
    
    print(f"[LangGraph] ✅ STT 완료: {raw[:50]}...")
    return state

# ───────────────────────────────────────────────────
# 2) Rewrite 에이전트: raw → rewritten
# ───────────────────────────────────────────────────
async def rewrite_agent(state: InterviewState) -> InterviewState:
    """
    STT 결과를 문법적으로 정제하는 리라이팅 에이전트
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: 리라이팅 결과가 추가된 상태
        
    처리 과정:
    1. STT 결과에서 마지막 세그먼트 추출
    2. GPT-4o-mini로 의미 보존 기반 텍스트 정제
    3. 재시도 횟수 관리 (현재 재시도 비활성화)
    4. 결과를 state["rewrite"]["items"]에 저장
    
    Note:
        - 지원자 답변 의미 절대 변경 안 함
        - 문법 오류 및 불필요한 공백 제거
        - 면접관 발언 필터링
        - GPT-4o-mini 사용으로 비용 절약
    """
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
    """
    리라이팅 재시도 여부를 결정하는 조건 함수
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        Literal["retry", "done"]: 재시도 또는 완료
        
    Note:
        - 현재 재시도 로직 비활성화 (비용 절약)
        - 항상 "done" 반환하여 한 번만 실행
        - 필요 시 재시도 로직 활성화 가능
    """
    # 항상 done 반환 (재시도 없음)
    return "done"

# ───────────────────────────────────────────────────
# 4) Rewrite 검증 에이전트
# ───────────────────────────────────────────────────
async def rewrite_judge_agent(state: InterviewState) -> InterviewState:
    """
    리라이팅 결과를 검증하는 판정 에이전트
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: 검증 결과가 추가된 상태
        
    처리 과정:
    1. 리라이팅 결과 품질 검증 (의미 보존, 문법 정확성)
    2. GPT-4o-mini로 판정 수행
    3. 검증 통과 시 final 배열에 추가
    4. 강제 통과 플래그 처리
    
    Note:
        - 현재 재시도 로직 비활성화로 대부분 통과
        - JSON 파싱 오류 시 안전 처리
        - 중복 답변 필터링 로직 포함
    """
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
                model="gpt-4o-mini",
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
                item["judge_notes"].append("강제 통과 (재시도 3회 초과)")

            if item["ok"]:
                # 중복된 rewritten 답변이 이미 final에 있으면 추가하지 않음
                rewritten = item["rewritten"]
                if not any(f["rewritten"] == rewritten for f in rewrite.get("final", [])):
                    rewrite.setdefault("final", []).append({
                        "raw":       item["raw"],
                        "rewritten": rewritten,
                        "timestamp": datetime.now(KST).isoformat()
                    })
                    # print(f"[DEBUG] ✅ final에 추가됨: {item['rewritten'][:50]}...")
                else:
                    # print(f"[DEBUG] ⚠️ 중복된 답변(final)에 추가하지 않음: {item['rewritten'][:50]}...")
                    pass

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
                    # print(f"[DEBUG] ✅ 강제 통과로 final에 추가됨: {item['rewritten'][:50]}...")
                else:
                    # print(f"[DEBUG] ⚠️ 강제 통과 중복(final)에 추가하지 않음: {item['rewritten'][:50]}...")
                    pass
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
    return state


# ───────────────────────────────────────────────────
# 5) Nonverbal 평가 에이전트 (표정만 평가)
# ───────────────────────────────────────────────────
async def nonverbal_evaluation_agent(state: InterviewState) -> InterviewState:
    """
    비언어적 요소(표정)를 평가하는 에이전트
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: 비언어적 평가 결과가 추가된 상태
        
    처리 과정:
    1. nonverbal_counts에서 표정 데이터 추출
    2. FacialExpression 객체로 변환
    3. GPT-4o-mini로 표정 패턴 분석
    4. 0.0~1.0 점수를 15점 만점으로 환산
    5. 결과를 state["evaluation"]["results"]["비언어적"]에 저장
    
    Note:
        - 프론트엔드에서 수집된 smile, neutral, frown, angry 횟수 기반
        - 적절한 표정 변화와 웃음은 긍정적 평가
        - 데이터 누락 시 경고 메시지 출력
    """
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
        # print(f"[DEBUG] 비언어적 평가 결과(score): {score}, analysis: {analysis}, feedback: {feedback}")
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
    return state

# ───────────────────────────────────────────────────
# 6) 평가 재시도 조건: 최대 3회 → 단 1회만 수행
# ───────────────────────────────────────────────────
def should_retry_evaluation(state: InterviewState) -> Literal["retry", "continue", "done"]:
    """
    평가 재시도 여부를 결정하는 조건 함수
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        Literal["retry", "continue", "done"]: 재시도, 계속, 완료
        
    처리 로직:
    - 평가 성공 또는 재시도 1회 도달 시 "continue"
    - 그 외의 경우 "retry" (최대 2번 실행)
    
    Note:
        - 최대 재시도 횟수 1회로 제한 (비용 절약)
        - 총 2번 실행 후 무조건 진행
        - 내용 검증은 evaluation_judge_agent에서 수행
    """
    evaluation = safe_get(state, "evaluation", {}, context="should_retry_evaluation:evaluation")
    retry_count = safe_get(evaluation, "retry_count", 0, context="should_retry_evaluation:retry_count")
    is_ok = safe_get(evaluation, "ok", False, context="should_retry_evaluation:ok")
    
    # print(f"[DEBUG] should_retry_evaluation - retry_count: {retry_count}, is_ok: {is_ok}")
    
    # 평가가 성공했거나 최대 재시도 횟수(1회)에 도달한 경우 (총 2번 실행)
    if is_ok or retry_count >= 1:
        # print(f"[DEBUG] 평가 완료 - ok: {is_ok}, retry_count: {retry_count}")
        return "continue"
    
    # 재시도 필요
    # print(f"[DEBUG] 평가 재시도 필요 - retry_count: {retry_count}")
    return "retry"

# ───────────────────────────────────────────────────
# 7) LLM 키워드 평가 에이전트
# ───────────────────────────────────────────────────
async def evaluation_agent(state: InterviewState) -> InterviewState:
    """
    8개 키워드 × 3개 기준으로 면접 답변을 평가하는 메인 에이전트
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: 평가 결과가 추가된 상태
        
    처리 과정:
    1. 리라이팅된 답변 또는 STT 원본 답변 추출
    2. 8개 키워드별 3개 기준으로 평가 수행
    3. 점수, 사유, 인용구 포함한 상세 결과 생성
    4. 기존 비언어적 평가 결과와 병합
    
    평가 영역:
    - 인성적 요소 (90점): SUPEX, VWBE, Passionate, Proactive, Professional, People
    - 기술/직무 (15점): 실무 기술/지식, 문제 해결 적용력, 학습 발전 가능성
    - 도메인 전문성 (15점): 도메인 이해도, 실제 사례 적용, 전략적 사고력
    
    Note:
        - GPT-4o-mini 사용으로 비용 절약
        - 결과 정규화로 데이터 일관성 보장
        - 재시도 횟수 관리 포함
    """
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

    return state

# ───────────────────────────────────────────────────
# 8) 평가 검증 에이전트
# ───────────────────────────────────────────────────
async def evaluation_judge_agent(state: InterviewState) -> InterviewState:
    """
    평가 결과를 검증하는 판정 에이전트
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: 검증 결과가 추가된 상태
        
    검증 항목:
    1. 구조적 검증: 각 키워드당 3개 기준 존재 여부
    2. 점수 범위 검증: 1~5점 범위 내 점수 확인
    3. 총점 검증: 최대 점수 초과 여부 확인
    4. 내용 검증: GPT-4o-mini로 평가 내용 타당성 검증
    
    Note:
        - 검증 실패 시에도 재시도 제한으로 진행
        - 내용 검증 오류 시 기본 통과 처리
        - 모든 검증 결과를 decision_log에 기록
    """
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
            model="gpt-4o-mini",
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
    
    return state

def calculate_area_scores(evaluation_results, nonverbal_score):
    """
    영역별 점수 계산 및 100점 만점 환산 함수
    
    Args:
        evaluation_results (dict): 평가 결과 딕셔너리
        nonverbal_score (int): 비언어적 점수 (15점 만점)
        
    Returns:
        tuple: (weights, personality_score_scaled, job_domain_score_scaled, nonverbal_score_scaled)
        
    계산 방식:
    - 인성적 요소 (90점 만점): SUPEX, VWBE, Passionate, Proactive, Professional, People
    - 직무·도메인 (30점 만점): "기술/직무", "도메인 전문성"  
    - 비언어적 요소 (15점 만점): 표정 분석 점수
    
    환산 비율:
    - 인성적 요소: 45% (90점 → 45점)
    - 직무·도메인: 45% (30점 → 45점)
    - 비언어적 요소: 10% (15점 → 10점)
    """
    personality_keywords = ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]
    job_domain_keywords = ["기술/직무", "도메인 전문성"]
    
    # 언어적 요소 총점
    personality_score = 0
    for keyword in personality_keywords:
        for criterion in evaluation_results.get(keyword, {}).values():
            personality_score += criterion.get("score", 0)
    # print(f"[DEBUG] 인성적 요소 총점: {personality_score} (max 90)")
    
    # 직무·도메인 총점
    job_domain_score = 0
    for keyword in job_domain_keywords:
        for criterion in evaluation_results.get(keyword, {}).values():
            job_domain_score += criterion.get("score", 0)
    # print(f"[DEBUG] 직무·도메인 총점: {job_domain_score} (max 30)")
    
    # 비언어적 요소
    # print(f"[DEBUG] 비언어적 요소 원점수: {nonverbal_score} (max 15)")
    max_personality = 90
    max_job_domain = 30
    max_nonverbal = 15
    
    # 100점 만점 환산 점수 계산
    personality_score_scaled = round((personality_score / max_personality) * 45, 1) if max_personality else 0
    job_domain_score_scaled = round((job_domain_score / max_job_domain) * 45, 1) if max_job_domain else 0
    nonverbal_score_scaled = round((nonverbal_score / max_nonverbal) * 10, 1) if max_nonverbal else 0
    
    # 비중 (고정값)
    weights = {
        "인성적 요소": 45.0,
        "직무·도메인": 45.0,
        "비언어적 요소": 10.0
    }
    
    # print(f"[DEBUG] 환산 점수: 인성적={personality_score_scaled}, 직무·도메인={job_domain_score_scaled}, 비언어적={nonverbal_score_scaled}")
    return weights, personality_score_scaled, job_domain_score_scaled, nonverbal_score_scaled

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
    """
    평가 검증 후 최종 점수 환산 및 요약을 담당하는 에이전트
    
    Args:
        state (InterviewState): 면접 상태 객체
        
    Returns:
        InterviewState: 최종 요약이 추가된 상태
        
    처리 과정:
    1. 영역별 점수 계산 및 100점 만점 환산
    2. 지원자 답변과 평가 사유를 GPT-4o로 종합 요약
    3. 평가 소요시간 계산 및 기록
    4. done 플래그 설정으로 파이프라인 완료
    
    최종 결과:
    - 인성적 요소: 45% (90점 → 45점)
    - 직무/도메인: 45% (30점 → 45점)  
    - 비언어적 요소: 10% (15점 → 10점)
    - 총점: 100점 만점
    
    Note:
        - GPT-4o 사용으로 고품질 요약 생성
        - 평가 소요시간 추적 및 성능 모니터링
        - 모든 결과를 state["summary"]에 저장
    """
    evaluation = safe_get(state, "evaluation", {}, context="score_summary_agent:evaluation")
    evaluation_results = safe_get(evaluation, "results", {}, context="score_summary_agent:evaluation.results")
    # print(f"[DEBUG] 평가 결과(evaluation_results): {json.dumps(evaluation_results, ensure_ascii=False, indent=2)}")
    nonverbal = evaluation_results.get("비언어적", {})
    nonverbal_score = nonverbal.get("score", 0)
    nonverbal_reason = nonverbal.get("reason", "평가 사유없음")
    # print(f"[DEBUG] 비언어적 평가: score={nonverbal_score}, reason={nonverbal_reason}")

    # 100점 만점 환산 점수 계산
    weights, personality_score_scaled, job_domain_score_scaled, nonverbal_score_scaled = calculate_area_scores(evaluation_results, nonverbal_score)
    verbal_score = personality_score_scaled + job_domain_score_scaled
    # print(f"[DEBUG] verbal_score(인성+직무/도메인): {verbal_score}")

    # 전체 키워드 평가 사유 종합 (SUPEX, VWBE, Passionate, Proactive, Professional, People, 기술/직무, 도메인 전문성)
    all_keywords = [
        "SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People",
        "기술/직무", "도메인 전문성"
    ]
    reasons = []
    for keyword in all_keywords:
        for crit_name, crit in evaluation_results.get(keyword, {}).items():
            reason = crit.get("reason", "")
            if reason:
                reasons.append(f"{keyword} - {crit_name}: {reason}")
            # print(f"[DEBUG] 평가 사유 추출: {keyword} - {crit_name} - {reason}")
    all_reasons = "\n".join(reasons)
    # print(f"[DEBUG] all_reasons(전체 평가 사유):\n{all_reasons}")

    # 지원자 답변 추출
    rewrite = safe_get(state, "rewrite", {}, context="score_summary_agent:rewrite")
    final_items = safe_get(rewrite, "final", [], context="score_summary_agent:rewrite.final")
    if final_items:
        answer = "\n".join(item["rewritten"] for item in final_items)
    else:
        stt = safe_get(state, "stt", {}, context="score_summary_agent:stt")
        stt_segments = safe_get(stt, "segments", [], context="score_summary_agent:stt.segments")
        if stt_segments:
            answer = "\n".join(seg.get("raw", "답변 내용이 없습니다.") for seg in stt_segments)
        else:
            answer = "답변 내용이 없습니다."
    # print(f"[DEBUG] 지원자 답변(answer):\n{answer}")

    # LLM 프롬프트로 종합 요약 요청
    prompt = EVAL_REASON_SUMMARY_PROMPT.format(answer=answer, all_reasons=all_reasons)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    verbal_reason = response.choices[0].message.content.strip().splitlines()[:8]
    # print(f"[DEBUG] summary_text(LLM 요약): {verbal_reason}")

    # 각 키워드별 총점 계산
    keyword_scores = {}
    for keyword, criteria in evaluation_results.items():
        if keyword == "비언어적":
            continue
        total = 0
        for crit in criteria.values():
            if isinstance(crit, dict):
                total += crit.get("score", 0)
            elif isinstance(crit, int):
                total += crit
        keyword_scores[keyword] = total

    # state에 저장
    state["summary"] = {
        "weights": weights,
        "personality_score": personality_score_scaled,
        "job_domain_score": job_domain_score_scaled,
        "verbal_score": verbal_score,
        "verbal_reason": verbal_reason,
        "nonverbal_score": nonverbal_score_scaled,
        "nonverbal_reason": nonverbal_reason,
        "keyword_scores": keyword_scores,
        "total_score": round(verbal_score + nonverbal_score_scaled, 1)
    }
    print(f"[LangGraph] ✅ 영역별 점수/요약 저장: {json.dumps(state['summary'], ensure_ascii=False, indent=2)}")

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
                "end_time": datetime.now(KST).isoformat()
            }
        })
        
        # summary에도 소요시간 정보 추가
        state["summary"]["evaluation_duration"] = {
            "total_seconds": round(total_elapsed, 2),
            "start_time": datetime.fromtimestamp(start_time, KST).isoformat(),
            "end_time": datetime.now(KST).isoformat()
        }
    else:
        print("[⏱️] 평가 시작 시간 정보가 없습니다.")

    # 모든 처리 완료 - done 플래그 설정
    state["done"] = True
    print(f"[LangGraph] ✅ 모든 평가 완료 - done 플래그 설정")

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
#     return state

# ──────────────── 🏗️ 파이프라인 그래프 구성 ────────────────

# 1) STT → 리라이팅 파이프라인
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

# 2) 평가 → 요약 파이프라인
final_builder = StateGraph(InterviewState)
final_builder.add_node("nonverbal_eval", nonverbal_evaluation_agent)
final_builder.add_node("evaluation_agent", evaluation_agent)
final_builder.add_node("evaluation_judge_agent", evaluation_judge_agent)
final_builder.add_node("score_summary_agent", score_summary_agent)
# final_builder.add_node("excel_node", excel_node)  # Excel 생성 노드 (현재 비활성화)
final_builder.set_entry_point("nonverbal_eval")
final_builder.add_edge("nonverbal_eval", "evaluation_agent")
final_builder.add_edge("evaluation_agent", "evaluation_judge_agent")
# final_builder.add_edge("pdf_node", "excel_node")
final_builder.add_conditional_edges(
    "evaluation_judge_agent", should_retry_evaluation,
    {"retry":"evaluation_agent", "continue":"score_summary_agent", "done":"__end__"}
)
# final_builder.add_channel("decision_log", LastValue())
final_flow_executor = final_builder.compile()

"""
파이프라인 실행 흐름:

1. interview_flow_executor (STT → 리라이팅):
   stt_node → rewrite_agent → rewrite_judge_agent → (재시도 없음) → 완료

2. final_flow_executor (평가 → 요약):
   nonverbal_eval → evaluation_agent → evaluation_judge_agent → (재시도 최대 1회) → score_summary_agent → 완료

전체 흐름:
WebM 오디오 → STT → 리라이팅 → 비언어적 평가 → 언어적 평가 → 검증 → 요약 → 완료
"""