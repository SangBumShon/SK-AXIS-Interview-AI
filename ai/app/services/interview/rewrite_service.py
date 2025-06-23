import time
import os
from dotenv import load_dotenv
import openai

# Load environment variables and initialize API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 프롬프트: 의미 보존 + 문법/공백 정제 + 질문-답변 흐름 유지
REWRITE_PROMPT = """
다음은 면접 대화 STT 결과입니다. 지원자 답변의 의미는 변경하지 마세요.
- 문법 오류 및 오탈자 수정
- 불필요한 공백 제거
- 핵심 내용(질문-답변 흐름)은 그대로 보존
- 면접관 답변이 포착되면 해당 부분은 제거

{answer_raw}
"""

async def rewrite_answer(raw: str) -> tuple[str, float]:
    """
    STT로 받은 raw 텍스트를 의미 보존 기반으로 정제합니다.
    반환값: (정제된 답변, 처리 시간 초)
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
    rewritten = response.choices[0].message.content.strip()
    return rewritten, round(elapsed, 2)
