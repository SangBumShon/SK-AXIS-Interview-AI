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

반드시 다음 JSON 형식으로만 응답해주세요:
{{
    "score": 0.0,  # 0.0 ~ 1.0 사이의 실수
    "analysis": "분석 내용",
    "feedback": "피드백 내용"
}}

예시 응답:
{{
    "score": 0.8,
    "analysis": "지원자는 대체로 안정적인 자세를 유지했으나, 다리를 벌리는 행동이 다소 관찰되었습니다.",
    "feedback": "자세를 더 안정적으로 유지하면 좋겠습니다."
}}
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

반드시 다음 JSON 형식으로만 응답해주세요:
{{
    "score": 0.0,  # 0.0 ~ 1.0 사이의 실수
    "analysis": "분석 내용",
    "feedback": "피드백 내용"
}}

예시 응답:
{{
    "score": 0.9,
    "analysis": "지원자는 적절한 표정 변화를 보여주었으며, 특히 웃음이 많은 것이 긍정적입니다.",
    "feedback": "자연스러운 표정 변화가 좋았습니다."
}}
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

반드시 다음 JSON 형식으로만 응답해주세요:
{{
    "score": 0.0,  # 0.0 ~ 1.0 사이의 실수
    "analysis": "분석 내용",
    "feedback": "피드백 내용"
}}

예시 응답:
{{
    "score": 0.85,
    "analysis": "전반적으로 안정적인 자세와 자연스러운 표정 변화를 보여주었습니다.",
    "feedback": "비언어적 소통이 전반적으로 우수합니다."
}}
"""
)

# 3) 자세 평가
async def evaluate_posture(posture: Posture) -> Tuple[float, str, str, str]:
    data = {
        "leg_spread": posture.leg_spread,
        "leg_shake": posture.leg_shake,
        "head_down": posture.head_down
    }
    prompt = _posture_prompt.format(posture_data=data)
    resp = await _llm.ainvoke(prompt)
    try:
        res = json.loads(resp.content)
        if "score" not in res:
            raise KeyError("LLM 응답에 'score' 키가 없습니다.")
        return res["score"], res["feedback"], res["analysis"], resp.content
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {resp.content}") from e
    except KeyError as e:
        raise ValueError(f"LLM 응답에 필수 키가 없습니다: {resp.content}") from e

# 4) 표정 평가
async def evaluate_facial_expression(facial: FacialExpression) -> Tuple[float, str, str, str]:
    data = {
        "smile": facial.smile,
        "neutral": facial.neutral,
        "embarrassed": facial.embarrassed,
        "tearful": facial.tearful,
        "frown": facial.frown
    }
    prompt = _facial_prompt.format(facial_data=data)
    resp = await _llm.ainvoke(prompt)
    try:
        res = json.loads(resp.content)
        if "score" not in res:
            raise KeyError("LLM 응답에 'score' 키가 없습니다.")
        return res["score"], res["feedback"], res["analysis"], resp.content
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {resp.content}") from e
    except KeyError as e:
        raise ValueError(f"LLM 응답에 필수 키가 없습니다: {resp.content}") from e

# 5) 종합 평가
async def evaluate(nonverbal: NonverbalData) -> NonverbalScore:
    # (1) 자세
    p_score, p_fb, p_an, p_raw_llm = await evaluate_posture(nonverbal.posture)
    # (2) 표정
    f_score, f_fb, f_an, f_raw_llm = await evaluate_facial_expression(nonverbal.facial_expression)
    # (3) 종합 LLM 평가
    prompt = _overall_prompt.format(posture_analysis=p_an, facial_analysis=f_an)
    resp = await _llm.ainvoke(prompt)
    try:
        over = json.loads(resp.content)
        if "score" not in over:
            raise KeyError("LLM 응답에 'score' 키가 없습니다.")
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 응답을 JSON으로 파싱할 수 없습니다: {resp.content}") from e
    except KeyError as e:
        raise ValueError(f"LLM 응답에 필수 키가 없습니다: {resp.content}") from e
    # (4) 직접 계산
    overall_score = round(p_score * 0.6 + f_score * 0.4, 2)
    feedback = {"자세": p_fb, "표정": f_fb, "종합": over.get("feedback", "")}    
    return NonverbalScore(
        interviewee_id=nonverbal.interviewee_id,
        posture_score=p_score,
        facial_score=f_score,
        overall_score=overall_score,
        feedback=feedback,
        detailed_analysis=over.get("analysis", ""),
        posture_raw_llm_response=p_raw_llm,
        facial_raw_llm_response=f_raw_llm,
        overall_raw_llm_response=resp.content
    )
