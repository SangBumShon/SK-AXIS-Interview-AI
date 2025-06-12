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
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

from app.schemas.nonverbal import Posture, FacialExpression, NonverbalData, NonverbalScore

# 1) 환경 변수 & LLM 초기화
load_dotenv()
_openai_key = os.getenv("OPENAI_API_KEY")
if not _openai_key:
    raise ValueError("OPENAI_API_KEY가 설정되어 있지 않습니다.")

_llm = ChatOpenAI(
    model_name="gpt-4-turbo-preview",
    temperature=0.7,
    openai_api_key=_openai_key
)

# 2) PromptTemplate 정의
_posture_prompt = PromptTemplate(
    input_variables=["posture_data"],
    template="""
당신은 면접 전문가입니다. 지원자의 자세를 분석하고 평가해주세요.

자세 데이터:
- 다리 벌림 횟수: {posture_data[leg_spread]}
- 다리 떨림 횟수: {posture_data[leg_shake]}
- 고개 숙임 횟수: {posture_data[head_down]}

JSON 형식으로 응답해주세요:
{"score": float, "analysis": str, "feedback": str}
"""
)

_facial_prompt = PromptTemplate(
    input_variables=["facial_data"],
    template="""
당신은 면접 전문가입니다. 지원자의 표정을 분석하고 평가해주세요.

표정 데이터:
- 웃음 횟수: {facial_data[smile]}
- 무표정 횟수: {facial_data[neutral]}
- 당황 횟수: {facial_data[embarrassed]}
- 울상 횟수: {facial_data[tearful]}
- 찡그림 횟수: {facial_data[frown]}

JSON 형식으로 응답해주세요:
{"score": float, "analysis": str, "feedback": str}
"""
)

_overall_prompt = PromptTemplate(
    input_variables=["posture_analysis", "facial_analysis"],
    template="""
당신은 면접 전문가입니다. 지원자의 비언어적 소통을 종합적으로 분석하고 평가해주세요.

자세 분석:
{posture_analysis}

표정 분석:
{facial_analysis}

JSON 형식으로 응답해주세요:
{"score": float, "analysis": str, "feedback": str}
"""
)

# 3) 자세 평가
async def evaluate_posture(posture: Posture) -> Tuple[float, str, str]:
    data = {
        "leg_spread": posture.leg_spread,
        "leg_shake": posture.leg_shake,
        "head_down": posture.head_down
    }
    prompt = _posture_prompt.format(posture_data=data)
    resp = await _llm.ainvoke(prompt)
    res = json.loads(resp.content)
    return res["score"], res["feedback"], res["analysis"]

# 4) 표정 평가
async def evaluate_facial_expression(facial: FacialExpression) -> Tuple[float, str, str]:
    data = {
        "smile": facial.smile,
        "neutral": facial.neutral,
        "embarrassed": facial.embarrassed,
        "tearful": facial.tearful,
        "frown": facial.frown
    }
    prompt = _facial_prompt.format(facial_data=data)
    resp = await _llm.ainvoke(prompt)
    res = json.loads(resp.content)
    return res["score"], res["feedback"], res["analysis"]

# 5) 종합 평가
async def evaluate(nonverbal: NonverbalData) -> NonverbalScore:
    # (1) 자세
    p_score, p_fb, p_an = await evaluate_posture(nonverbal.posture)
    # (2) 표정
    f_score, f_fb, f_an = await evaluate_facial_expression(nonverbal.facial_expression)
    # (3) 종합 LLM 평가
    prompt = _overall_prompt.format(posture_analysis=p_an, facial_analysis=f_an)
    resp = await _llm.ainvoke(prompt)
    over = json.loads(resp.content)
    # (4) 직접 계산
    overall_score = round(p_score * 0.6 + f_score * 0.4, 2)
    feedback = {"자세": p_fb, "표정": f_fb, "종합": over.get("feedback", "")}    
    return NonverbalScore(
        posture_score=p_score,
        facial_score=f_score,
        overall_score=overall_score,
        feedback=feedback,
        detailed_analysis=over.get("analysis", "")
    )
