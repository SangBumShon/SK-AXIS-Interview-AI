# app/services/interview/block_processor.py

import asyncio
from typing import Dict, Any

from app.services.interview.rewrite_service import rewrite_question_block
from app.services.interview.evaluation_service import evaluate_answer_block
from app.services.interview.question_block_handler import (
    current_blocks,
    finalized_blocks,
    get_question_intent_and_keywords
)


async def finalize_and_process_block(applicant_id: int) -> Dict[str, Any]:
    """
    열린 블록을 닫고, 그 블록에 대해 rewrite → evaluate → finalized_blocks에 저장
    """
    block = current_blocks.pop(applicant_id, None)
    if not block:
        return {"error": "No active block for this applicant."}

    # 1) 발화(turns) 병합 → rewrite
    full_text = "\n".join([f"{turn['speaker']}: {turn['text']}" for turn in block["turns"]])
    rewritten_text, _ = await rewrite_question_block(full_text)

    # 2) 평가 (의도+키워드 가져와서 LLM 평가 호출)
    question_id = block["representative_question_id"]
    intent, keywords = get_question_intent_and_keywords(applicant_id, question_id)
    evaluation = await evaluate_answer_block(
        question=str(question_id),
        answer=rewritten_text,
        intent=intent,
        keywords=keywords
    )

    # 3) finalized_blocks에 저장
    finalized_blocks.setdefault(applicant_id, []).append({
        "question_id": question_id,
        "dialogue": block["turns"],
        "rewritten_text": rewritten_text,
        "evaluation": evaluation
    })

    return {
        "question_id": question_id,
        "status": "processed"
    }
