import openai
import os
import json
from dotenv import load_dotenv
from typing import List, Dict
from app.constants.eval_criteria import EVAL_CRITERIA
from app.services.interview.question_store import store_question_analysis

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_question_analysis_prompt(question_text: str) -> str:
    return f"""
다음은 면접 질문입니다:

"{question_text}"

이 질문의 의도를 한 문장으로 요약해주세요.
그리고 SUPEX, VWBE, Passionate, Professional, Proactive, People 중 이 질문과 관련된 키워드를 2개 이상 추출해주세요.
답변은 다음 JSON 형식으로 해주세요:

{{
  "intent": "...",
  "keywords": ["...", "..."]
}}
"""

def analyze_question_with_llm(question_text: str) -> Dict:
    prompt = build_question_analysis_prompt(question_text)
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
        assert "intent" in parsed and "keywords" in parsed
        return parsed
    except Exception:
        raise ValueError(f"LLM 응답이 잘못되었습니다: {content}")

def generate_applicant_question_metadata(applicant_id: int, question_list: List[Dict]) -> Dict:
    question_info = []
    for q in question_list:
        analysis = analyze_question_with_llm(q["text"])
        question_info.append({
            "question_id": q["id"],
            "text": q["text"],
            "intent": analysis["intent"],
            "keywords": analysis["keywords"]
        })
        store_question_analysis(
            applicant_id=applicant_id,
            question_number=q["id"],
            intent=analysis["intent"],
            keywords=analysis["keywords"]
        )

    return {
        "applicant_id": applicant_id,
        "questions": question_info
    }
