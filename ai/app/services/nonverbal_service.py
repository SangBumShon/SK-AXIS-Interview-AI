from typing import List, Dict

# ✅ 프레임 단위 비언어 분석 결과에서 질문 단위 시간 구간 추출
def extract_segments_for_question(segments: List[dict], start: float, end: float) -> List[dict]:
    return [s for s in segments if start <= s.get("time", 0) <= end]

# ✅ 비언어 요약 통계 계산 함수
def summarize_behavior_metrics(segments: List[dict]) -> Dict[str, float]:
    if not segments:
        return {}

    total = len(segments)
    blink = sum(1 for s in segments if s.get("blink"))
    gaze_away = sum(1 for s in segments if not s.get("eye_contact", True))
    frown = sum(1 for s in segments if s.get("expression") == "찡그림")
    smile = sum(1 for s in segments if s.get("expression") == "웃음")
    lip_tension = sum(1 for s in segments if s.get("lip_tension"))
    head_down = sum(1 for s in segments if s.get("stance_stability") == "흔들림")

    return {
        "blink_rate": blink / total,
        "gaze_away_rate": gaze_away / total,
        "frown_count": frown,
        "smile_count": smile,
        "lip_tension_count": lip_tension,
        "head_down_count": head_down,
        "total_frames": total
    }

# ✅ GPT 기반 신뢰도 평가
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def evaluate_truthfulness_with_llm(answer: str, metrics: Dict[str, float]) -> Dict:
    prompt = f"""
다음은 면접 질문에 대한 지원자의 답변과 해당 구간에서의 비언어적 행동 요약입니다.

[답변 내용]
{answer}

[비언어적 행동 요약]
- 시선 회피 비율: {metrics.get("gaze_away_rate", 0)*100:.1f}%
- 눈 깜빡임 비율: {metrics.get("blink_rate", 0)*100:.1f}%
- 찡그림 횟수: {metrics.get("frown_count", 0)}회
- 웃음 횟수: {metrics.get("smile_count", 0)}회
- 입술 긴장 횟수: {metrics.get("lip_tension_count", 0)}회
- 고개 숙임 횟수: {metrics.get("head_down_count", 0)}회

이 정보를 바탕으로, 지원자의 신뢰도를 1~5점으로 평가하고, 근거를 간결히 서술하세요.
형식:
- 신뢰도 점수: N점
- 평가 사유: ...
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    score_line = next((line for line in content.split("\n") if "신뢰도" in line), "")
    reason_line = next((line for line in content.split("\n") if "사유" in line), "")

    return {
        "truth_score": int(score_line.replace("신뢰도 점수:", "").replace("점", "").strip()) if score_line else -1,
        "justification": reason_line.replace("평가 사유:", "").strip() if reason_line else content
    }
