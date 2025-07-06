# app/services/nonverbal_service.py
"""
비언어적 요소 AI 평가 서비스
- 자세(posture) 평가
- 표정(facial) 평가
- 종합(overall) 평가
- (선택) counts 기반 단발 평가 함수 지원
"""
import os
import json
from typing import Dict, Tuple, List
from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.nonverbal import Posture, FacialExpression, NonverbalData, NonverbalScore

# 1) 환경 변수 & OpenAI 클라이언트 초기화
load_dotenv()
_openai_key = os.getenv("OPENAI_API_KEY")
if not _openai_key:
    raise ValueError("OPENAI_API_KEY가 설정되어 있지 않습니다.")

_client = OpenAI(api_key=_openai_key)

# 2) 프롬프트 템플릿 정의
def _get_facial_prompt(facial_data: dict) -> str:
    return f"""당신은 면접 전문가입니다. 지원자의 표정을 분석하고 평가해주세요.

표정 데이터:
- 웃음 횟수: {facial_data['smile']}
- 무표정 횟수: {facial_data['neutral']}
- 찡그림 횟수: {facial_data['frown']}
- 화남 횟수: {facial_data['angry']}

반드시 다음 JSON 형식으로만 응답해주세요:
{{
    "score": 0.0,
    "analysis": "분석 내용",
    "feedback": "피드백 내용"
}}

예시 응답:
{{
    "score": 0.9,
    "analysis": "지원자는 적절한 표정 변화를 보여주었으며, 특히 웃음이 많은 것이 긍정적입니다.",
    "feedback": "자연스러운 표정 변화가 좋았습니다."
}}"""

def _get_overall_prompt(facial_analysis: str) -> str:
    return f"""당신은 면접 전문가입니다. 지원자의 비언어적 소통을 종합적으로 분석하고 평가해주세요.

표정 분석:
{facial_analysis}

반드시 다음 JSON 형식으로만 응답해주세요:
{{
    "score": 0.0,
    "analysis": "분석 내용",
    "feedback": "피드백 내용"
}}

예시 응답:
{{
    "score": 0.85,
    "analysis": "전반적으로 안정적인 자세와 자연스러운 표정 변화를 보여주었습니다.",
    "feedback": "비언어적 소통이 전반적으로 우수합니다."
}}"""

# 3) 표정 평가 함수
async def evaluate(nonverbal: FacialExpression) -> dict:
    data = {
        "smile": nonverbal.smile,
        "neutral": nonverbal.neutral,
        "frown": nonverbal.frown,
        "angry": nonverbal.angry
    }
    
    prompt = _get_facial_prompt(data)
    
    # OpenAI 클라이언트 직접 사용
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    raw = response.choices[0].message.content.strip()
    
    # 마크다운 코드블록 제거
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    
    try:
        res = json.loads(raw)
        if "score" not in res:
            raise KeyError("LLM 응답에 'score' 키가 없습니다.")
        return res  # score, analysis, feedback 모두 반환
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {raw}") from e
    except KeyError as e:
        raise ValueError(f"LLM 응답에 필수 키가 없습니다: {raw}") from e