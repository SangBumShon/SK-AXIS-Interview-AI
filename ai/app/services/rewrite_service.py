# app/services/interview/rewrite_service.py
import time
import os
from dotenv import load_dotenv
import openai

# Load environment variables and initialize API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt template for rewriting raw STT text
REWRITE_PROMPT = """
다음은 면접 대화 STT 결과입니다. 면접관 질문과 지원자 답변의 의미는 변경하지 마세요.
- 문법 오류 및 오탈자 수정
- 불필요한 공백 제거
- 핵심 내용(질문-답변 흐름)은 그대로 보존

{answer_raw}
"""

async def rewrite_answer(raw: str) -> tuple[str, float]:
    """
    Rewrite raw STT text using OpenAI and measure elapsed time.
    Returns: (rewritten_text, elapsed_seconds)
    """
    prompt = REWRITE_PROMPT.format(answer_raw=raw)
    start = time.perf_counter()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.0
    )
    elapsed = time.perf_counter() - start
    text = response.choices[0].message.content.strip()
    return text, round(elapsed, 2)
