# app/services/nonverbal_service.py
"""
SK AXIS AI 면접 비언어적 요소 평가 서비스

이 파일은 면접 중 수집된 비언어적 데이터를 AI로 분석하고 평가하는 서비스입니다.
주요 기능:
- 표정 분석: 웃음, 무표정, 찡그림, 화남 횟수 기반 평가
- GPT-4o-mini를 사용한 표정 패턴 분석
- 0.0~1.0 점수 산출 후 15점 만점으로 환산

평가 기준:
- 적절한 표정 변화와 웃음은 긍정적 평가
- 과도한 무표정이나 부정적 표정은 감점
- 면접 상황에 맞는 자연스러운 표정 변화 중시

데이터 흐름:
프론트엔드 → NonverbalData → FacialExpression → GPT 분석 → 점수 반환
"""

import os
import json
from typing import Dict, Tuple, List
from dotenv import load_dotenv
from openai import OpenAI

from app.schemas.nonverbal import Posture, FacialExpression, NonverbalData, NonverbalScore

# ──────────────── 🔐 환경 설정 ────────────────
# 1) 환경 변수 & OpenAI 클라이언트 초기화
load_dotenv()
_openai_key = os.getenv("OPENAI_API_KEY")
if not _openai_key:
    raise ValueError("OPENAI_API_KEY가 설정되어 있지 않습니다.")

# OpenAI 클라이언트 초기화 (비용 절약을 위해 gpt-4o-mini 사용)
_client = OpenAI(api_key=_openai_key)

# ──────────────── 🧠 프롬프트 템플릿 ────────────────
def _get_facial_prompt(facial_data: dict) -> str:
    """
    표정 분석을 위한 GPT 프롬프트를 생성합니다.
    
    Args:
        facial_data (dict): 표정 데이터 (smile, neutral, frown, angry 횟수)
        
    Returns:
        str: GPT에게 전달할 프롬프트 문자열
    """
    return f"""당신은 면접 전문가입니다. 지원자의 표정을 분석하고 평가해주세요.

표정 데이터:
- 웃음 횟수: {facial_data['smile']}
- 무표정 횟수: {facial_data['neutral']}
- 찡그림 횟수: {facial_data['frown']}
- 화남 횟수: {facial_data['angry']}

평가 기준:
- 적절한 웃음과 표정 변화는 긍정적으로 평가
- 과도한 무표정이나 부정적 표정은 감점
- 면접 상황에 맞는 자연스러운 표정이 중요
- 점수는 0.0~1.0 범위로 산출

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
    """
    종합 비언어적 평가를 위한 GPT 프롬프트를 생성합니다. (현재 미사용)
    
    Args:
        facial_analysis (str): 표정 분석 결과
        
    Returns:
        str: GPT에게 전달할 프롬프트 문자열
    """
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

# ──────────────── 🎯 표정 평가 함수 ────────────────
async def evaluate(nonverbal: FacialExpression) -> dict:
    """
    표정 데이터를 분석하여 비언어적 평가를 수행합니다.
    
    Args:
        nonverbal (FacialExpression): 표정 데이터 객체
        - smile: 웃음 횟수
        - neutral: 무표정 횟수  
        - frown: 찡그림 횟수
        - angry: 화남 횟수
        
    Returns:
        dict: 평가 결과
        {
            "score": 0.0~1.0,           # 정규화된 점수
            "analysis": "분석 내용",     # GPT 분석 결과
            "feedback": "피드백 내용"    # 개선 제안
        }
        
    Note:
        - GPT-4o-mini 모델 사용 (비용 절약)
        - 반환된 score는 graph_pipeline에서 15점 만점으로 환산
        - JSON 파싱 실패 시 ValueError 발생
    """
    # 표정 데이터를 딕셔너리로 변환
    data = {
        "smile": nonverbal.smile,
        "neutral": nonverbal.neutral,
        "frown": nonverbal.frown,
        "angry": nonverbal.angry
    }
    
    # GPT 프롬프트 생성
    prompt = _get_facial_prompt(data)
    
    # OpenAI GPT API 호출
    response = _client.chat.completions.create(
        model="gpt-4o-mini",  # 비용 절약을 위해 mini 모델 사용
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7       # 창의적 분석을 위해 적당한 temperature 설정
    )
    
    # GPT 응답 추출
    raw = response.choices[0].message.content.strip()
    
    # 마크다운 코드블록 제거 (GPT가 가끔 ```json으로 감싸는 경우 대응)
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    
    try:
        # JSON 파싱
        res = json.loads(raw)
        if "score" not in res:
            raise KeyError("LLM 응답에 'score' 키가 없습니다.")
        return res  # score, analysis, feedback 모두 반환
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {raw}") from e
    except KeyError as e:
        raise ValueError(f"LLM 응답에 필수 키가 없습니다: {raw}") from e