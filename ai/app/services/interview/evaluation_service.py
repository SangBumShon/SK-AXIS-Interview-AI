# app/services/interview/evaluation_service.py

import time
import os
import json
from dotenv import load_dotenv
import openai
from typing import Dict

from app.constants.eval_criteria import EVAL_CRITERIA

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

EVAL_SYSTEM = "당신은 면접 평가 전문가입니다."

INTENT_CRITERIA = [
    "핵심 주제 적합성",
    "의도 충실도",
    "구체성과 깊이"
]

EVAL_PROMPT_TEMPLATE = """
지원자의 다음 답변에 대해 다음을 평가하세요:

1. 질문 의도에 대한 평가
질문의 의도는 다음과 같습니다:
"{intent}"
다음 세 가지 기준으로 5점 만점으로 각각 평가하세요:
{intent_criteria_list}

2. 질문과 관련된 키워드: {keywords}
각 키워드에 대해 사전 정의된 세 가지 항목을 기준으로 5점 만점으로 평가하세요.
각 항목별 점수와 평가 사유를 작성하고, 감점이 있었다면 어느 항목에서 몇 점이 감점되었는지, 그리고 그 사유를 별도로 3문장 이내로 요약하세요.

질문: {question}
답변: {answer}

3. 평가 요약 (총 6문장 내외):
- 1~2.5문장: 질문의도 평가 총점 및 평가 사유
- 2.5~4.5문장: 키워드별 평가 사유 및 총점
- 4.5~6문장: 전체 총평 및 전체 점수

마지막으로 전체 종합 점수를 100점 만점으로 제시하고, 그 이유를 간략히 서술하세요.
"""

def format_criteria(criteria: list[str]) -> str:
    return "\n".join(f"- {c}" for c in criteria)

async def evaluate_answer_block(
    question: str,
    answer: str,
    intent: str,
    keywords: list[str]
) -> Dict:
    prompt = EVAL_PROMPT_TEMPLATE.format(
        question=question,
        answer=answer,
        intent=intent,
        keywords=", ".join(keywords),
        intent_criteria_list=format_criteria(INTENT_CRITERIA)
    )

    start = time.perf_counter()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EVAL_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=1200
    )
    elapsed = time.perf_counter() - start

    content = response.choices[0].message.content.strip()
    # content 안에 “score: XX점” 등을 파싱하려면 추가 로직 필요
    return {
        "raw_response": content,
        "elapsed_seconds": round(elapsed, 2)
    }
