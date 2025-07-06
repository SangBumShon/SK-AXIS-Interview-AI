"""
SK AXIS AI 면접 평가 서비스

이 파일은 면접 답변을 AI로 평가하는 핵심 서비스입니다.
주요 기능:
- GPT-4o-mini 모델을 사용한 키워드별 평가
- 평가 기준에 따른 점수 산출 (1-5점)
- 인용구 추출 및 평가 사유 생성

평가 영역:
1. 인성적 요소 (90점): SUPEX, VWBE, Passionate, Proactive, Professional, People
2. 기술/직무 (15점): 실무 기술/지식, 문제 해결 적용력, 학습 발전 가능성
3. 도메인 전문성 (15점): 도메인 이해도, 실제 사례 적용, 전략적 사고력

총 120점 → 100점 만점으로 환산하여 최종 점수 산출
"""

import time
import os
import json
from dotenv import load_dotenv
import openai

# 평가 기준 사전 (각 키워드별 세부 평가 항목 정의됨)
from app.constants.evaluation_constants_full_all import (
    EVAL_CRITERIA_WITH_ALL_SCORES,        # 인성적 요소 (90점)
    TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,  # 기술/직무 (15점)
    DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES      # 도메인 전문성 (15점)
)

# ──────────────── 🔐 OpenAI API 키 설정 ────────────────
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ──────────────── 🧠 평가 기준 사전(JSON) 생성 ────────────────
# 모든 평가 기준을 하나의 딕셔너리로 통합
_all_criteria = {
    **EVAL_CRITERIA_WITH_ALL_SCORES,        # SUPEX, VWBE, Passionate, Proactive, Professional, People
    **TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,  # 실무 기술/지식의 깊이, 문제 해결 적용력, 학습 및 발전 가능성
    **DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES      # 도메인 맥락 이해도, 실제 사례 기반 적용 능력, 전략적 사고력
}
# GPT 프롬프트에 포함할 JSON 문자열로 변환
_criteria_block = json.dumps(_all_criteria, ensure_ascii=False, indent=2)

# ──────────────── 🧠 시스템 프롬프트 (GPT 역할 안내) ────────────────
# GPT-4o-mini에게 면접 평가 전문가 역할을 부여하고 평가 기준을 제공
SYSTEM_PROMPT = f"""
당신은 기업 면접 평가 전문가입니다. 지원자의 전체 답변을 읽고,
아래 **평가기준 사전**의 모든 키워드와 모든 세부 항목에 대해 반드시 빠짐없이 점수를 매기세요.

평가 규칙:
- 각 키워드와 세부 항목명은 아래 사전과 완전히 동일하게 사용하세요.
- 각 항목별로 1~5점의 score, quotes(문장 인용, 1개 이상), reason(이유)를 반드시 포함하세요.
- 반드시 올바른 JSON 형식(콤마 포함)으로만 출력하세요. 예시 외의 설명, 주석, 텍스트는 절대 포함하지 마세요.

출력 형식 예시:
{{
  "SUPEX": {{
    "고난도 목표에 대한 도전 의지": {{"score": 5, "quotes": ["..."], "reason": "..."}},
    "실패 극복 및 지속적 개선 노력": {{"score": 4, "quotes": ["..."], "reason": "..."}},
    "창의적 전략 실행을 통한 한계 극복": {{"score": 3, "quotes": ["..."], "reason": "..."}}
  }},
  "VWBE": {{
    "자기주도적 문제 인지 및 목표 설정": {{"score": 5, "quotes": ["..."], "reason": "..."}},
    "심층적 사고 및 몰입": {{"score": 4, "quotes": ["..."], "reason": "..."}},
    "주체적 실행 판단 및 지속성": {{"score": 3, "quotes": ["..."], "reason": "..."}}
  }},
  "기술/직무": {{
    "실무 기술/지식의 깊이": {{"score": 5, "quotes": ["..."], "reason": "..."}},
    "문제 해결 적용력": {{"score": 4, "quotes": ["..."], "reason": "..."}},
    "학습 및 발전 가능성": {{"score": 3, "quotes": ["..."], "reason": "..."}}
  }},
  "도메인 전문성": {{
    "도메인 맥락 이해도": {{"score": 5, "quotes": ["..."], "reason": "..."}},
    "실제 사례 기반 적용 능력": {{"score": 4, "quotes": ["..."], "reason": "..."}},
    "전략적 사고력": {{"score": 3, "quotes": ["..."], "reason": "..."}}
  }}
}}

평가기준 사전:
{_criteria_block}
"""

# 사용자의 전체 답변을 GPT에게 전달하기 위한 템플릿
USER_TEMPLATE = """지원자의 전체 면접 답변:
{answer}

위 지침에 따라 평가를 수행해주세요."""


async def evaluate_keywords_from_full_answer(full_answer: str) -> dict:
    """
    GPT-4o-mini 모델을 사용하여 면접 답변을 종합 평가합니다.
    
    Args:
        full_answer (str): 지원자의 전체 면접 답변 텍스트
        
    Returns:
        dict: 키워드별 평가 결과
        {
            "SUPEX": {
                "고난도 목표에 대한 도전 의지": {
                    "score": 5,
                    "quotes": ["관련 답변 인용구"],
                    "reason": "평가 사유"
                },
                ...
            },
            "기술/직무": { ... },
            "도메인 전문성": { ... }
        }
    
    Note:
        - 총 8개 키워드 × 3개 세부 항목 = 24개 항목 평가
        - 각 항목당 1-5점 평가 (총 120점 만점)
        - 비용 절약을 위해 gpt-4o-mini 모델 사용
    """
    prompt = USER_TEMPLATE.format(answer=full_answer)

    start = time.perf_counter()
    try:
        # OpenAI GPT API 호출
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # 비용 절약을 위해 mini 모델 사용 (94% 비용 절감)
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,      # 일관성 있는 평가를 위해 낮은 temperature 설정
            max_tokens=16000      # 모든 평가 항목 출력을 위한 충분한 토큰 할당
        )
        elapsed = round(time.perf_counter() - start, 2)
        print(f"✅ 평가 완료 ({elapsed}초 소요)")

        # GPT 응답에서 본문 추출 → JSON 파싱
        raw_result = response.choices[0].message.content.strip()
        print(f"Raw evaluation result:\n{raw_result}\n")
        
        try:
            result = json.loads(raw_result)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 오류: {e}")
            # 파싱 실패 시 안전한 파싱 함수 사용
            return parse_llm_keyword_evaluation(raw_result)

    except Exception as e:
        print(f"❌ GPT 평가 오류: {e}")
        return {}


def parse_llm_keyword_evaluation(raw: str) -> dict:
    """
    GPT의 응답 문자열을 안전하게 JSON 형식으로 파싱합니다.
    
    GPT가 가끔 JSON 외에 추가 텍스트를 포함하는 경우를 대비한 안전 파싱 함수입니다.

    Args:
        raw (str): GPT 응답 문자열

    Returns:
        dict: 파싱된 평가 결과 (실패 시 빈 딕셔너리 반환)
    """
    import json
    try:
        # JSON 블록만 추출 (첫 번째 { 부터 마지막 } 까지)
        start_idx = raw.find('{')
        end_idx = raw.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = raw[start_idx:end_idx+1]
        else:
            json_str = raw
        
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 파싱 오류: {e}")
        print(f"원본 응답: {raw[:200]}...")  # 디버깅을 위한 일부 출력
        return {}


# ──────────────── 🗑️ 사용하지 않는 코드 (참고용) ────────────────
# 벡터 기반 키워드 검색 보조 기능 (현재 미사용)
# from app.services.vector_service import search_related_keywords

# def enrich_evaluation_with_keywords(answer_text: str) -> str:
#     """벡터 검색을 통한 키워드 보강 (현재 미사용)"""
#     related = search_related_keywords(answer_text)
#     keyword_summary = "\n".join(f"- {r['term']}: {r['description']}" for r in related)
#     return keyword_summary

# LangChain 기반 평가 시스템 (현재 미사용, OpenAI 직접 호출로 대체)
# from langchain_community.chat_models import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.chains import LLMChain

# 기존 LangChain 기반 평가 함수 (현재 미사용)
# def evaluate_answer(answer: str) -> str:
#     """LangChain 기반 답변 평가 (현재 미사용)"""
#     prompt = ChatPromptTemplate.from_template(
#         "다음 면접 답변을 평가해 주세요:\n\n{answer}\n\n"
#         "평가 기준:\n"
#         "- 답변의 명확성, 일관성, 관련성\n"
#         "- 어휘 사용과 문법적 정확성\n"
#         "- 전체적인 표현력과 설득력\n"
#         "평가 기준을 0점에서 5점 사이로 점수화하고, 각 기준에 대한 설명을 포함해 주세요.\n"
#         "평가 결과를 간결하게 요약해 주세요."
#     )
#     chain = LLMChain(llm=chat_model, prompt=prompt)
#     response = chain.run(answer=answer)
#     return response.strip()