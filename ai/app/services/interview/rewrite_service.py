# app/services/interview/rewrite_service.py

import time
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

REWRITE_SYSTEM = "당신은 면접 녹취를 정제하는 전문가입니다."

REWRITE_PROMPT_TEMPLATE = """
다음은 면접 질문 블록입니다. 질문, 꼬리 질문, 답변 순서와 의미는 절대 바꾸지 마세요.

- 질문-답변 흐름을 유지하세요
- 문법 오류 및 오탈자를 교정하세요
- 띄어쓰기와 문장 부호를 자연스럽게 정리하세요
- 발화자 표기를 보존하세요 (예: '면접관:', '지원자:')

### 원본 블록:
{raw_block}

### 정제된 블록:
"""

async def rewrite_question_block(raw_block: str) -> tuple[str, float]:
    """
    블록형 질문-답변을 정제하여 반환
    :param raw_block: "면접관: …\n지원자: …" 형식의 원문
    :return: (정제된 텍스트, 소요 시간)
    """
    prompt = REWRITE_PROMPT_TEMPLATE.format(raw_block=raw_block)
    start = time.perf_counter()
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.0
    )
    elapsed = time.perf_counter() - start
    return response.choices[0].message.content.strip(), round(elapsed, 2)
