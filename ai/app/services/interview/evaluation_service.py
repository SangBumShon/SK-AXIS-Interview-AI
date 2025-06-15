import time
import os
import json
from dotenv import load_dotenv
import openai

# 평가 기준 사전 (각 키워드별 세부 평가 항목 정의됨)
from app.constants.evaluation_constants_full_all import (
    EVAL_CRITERIA_WITH_ALL_SCORES,
    TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,
    DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES
)

# ──────────────── 🔐 OpenAI API 키 설정 ────────────────
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ──────────────── 🧠 평가 기준 사전(JSON) 생성 ────────────────
_all_criteria = {
    "인성/SUPEX_V_WBE": EVAL_CRITERIA_WITH_ALL_SCORES,
    "기술/직무": TECHNICAL_EVAL_CRITERIA_WITH_ALL_SCORES,
    "도메인 전문성": DOMAIN_EVAL_CRITERIA_WITH_ALL_SCORES
}
_criteria_block = json.dumps(_all_criteria, ensure_ascii=False, indent=2)

# ──────────────── 🧠 시스템 프롬프트 (GPT 역할 안내) ────────────────
SYSTEM_PROMPT = f"""
당신은 기업 면접 평가 전문가입니다. 지원자의 전체 답변을 읽고,
아래 **평가기준 사전**의 모든 키워드와 모든 세부 항목에 대해 반드시 빠짐없이 점수를 매기세요.

- 각 키워드와 세부 항목명은 아래 사전과 완전히 동일하게 사용하세요.
- 각 항목별로 1~5점의 score, quotes(문장 인용, 1개 이상), reason(이유)를 반드시 포함하세요.
- 반드시 올바른 JSON 형식(콤마 포함)으로만 출력하세요. 예시 외의 설명, 주석, 텍스트는 절대 포함하지 마세요.

예시:
{{
  "SUPEX": {{
    "고난도 목표에 대한 도전 의지": {{"score": 5, "quotes": ["..."], "reason": "..."}},
    ...
  }},
  ...
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
    Evaluate keywords from a full answer using the GPT-4o model.
    @param full_answer (str): The full answer provided by the candidate.
    @return dict: Evaluation results including keywords, scores, reasons, and citations.
    """
    prompt = USER_TEMPLATE.format(answer=full_answer)

    start = time.perf_counter()
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # 최신 멀티모달 모델 사용
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=16000  # 출력 길이 제한 증가
        )
        elapsed = round(time.perf_counter() - start, 2)
        print(f"✅ 평가 완료 ({elapsed}초 소요)")

        # GPT 응답에서 본문 추출 → JSON 파싱
        content = response.choices[0].message.content
        return parse_llm_keyword_evaluation(content)

    except Exception as e:
        print(f"❌ GPT 평가 오류: {e}")
        return {}



def parse_llm_keyword_evaluation(raw: str) -> dict:
    """
    GPT의 응답 문자열을 안전하게 JSON 형식으로 파싱합니다.

    Args:
        raw (str): GPT 응답 문자열

    Returns:
        dict: 파싱된 평가 결과 (실패 시 빈 딕셔너리 반환)
    """
    import json
    try:
        # JSON 블록만 추출
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
        return {}


# 벡터 기반 키워드 검색 보조
# from app.services.vector_service import search_related_keywords

# def enrich_evaluation_with_keywords(answer_text: str) -> str:
#     related = search_related_keywords(answer_text)
#     keyword_summary = "\n".join(f"- {r['term']}: {r['description']}" for r in related)
#     return keyword_summary
# from langchain_community.chat_models import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.chains import LLMChain

# from dotenv import load_dotenv
# import os

# load_dotenv()

# openai_key = os.getenv("OPENAI_API_KEY")
# if not openai_key:
#     raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# chat_model = ChatOpenAI(
#     model="gpt-4o",
#     temperature=0.0,
#     openai_api_key=openai_key
# )

# def evaluate_answer(answer: str) -> str:
#     """
#     면접 답변을 평가하는 함수
#     :param answer: 면접 답변 텍스트
#     :return: 평가 결과 텍스트
#     """
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