# app/services/interview/interview_service.py

from typing import Dict, Any
import asyncio
from app.services.interview.question_matcher import match_representative_question
from app.services.interview.question_block_handler import (
    start_new_block,
    add_turn_to_current_block,
    finalize_current_block,
    get_all_blocks
)
from app.services.interview.block_processor import finalize_and_process_block
from app.services.interview.interview_state import CURRENT_INTERVIEWEE_IDS, IS_STREAMING, REPRESENTATIVE_QUESTIONS

async def handle_transcription_chunk(speaker: str, text: str):
    """
    1) speaker 태그 판정
    2) 면접관이면 → TF-IDF로 대표질문 매칭 → 새 블록 또는 꼬리질문
    3) 지원자이면 → 해당 블록에 답변으로 추가
    """
    # 1) 면접 진행 중이 아니면 무시
    if not IS_STREAMING:
        return

    # 2) 면접관 발화
    if speaker == "interviewer":
        matched_idx = match_representative_question(text, threshold=0.8)
        if matched_idx is not None:
            # ✅ 실제 QID 매핑: 인덱스 기반으로 질문 리스트에서 QID 추출
            matched_qid = int(REPRESENTATIVE_QUESTIONS[matched_idx]["qid"])

            for aid in CURRENT_INTERVIEWEE_IDS:
                prev_blk = finalize_current_block(aid)
                if prev_blk:
                    await finalize_and_process_block(aid)

            for aid in CURRENT_INTERVIEWEE_IDS:
                start_new_block(aid, matched_qid)
                add_turn_to_current_block(aid, "interviewer", text)
        else:
            for aid in CURRENT_INTERVIEWEE_IDS:
                add_turn_to_current_block(aid, "interviewer_tail", text)

    # 3) 지원자 발화
    elif speaker.startswith("applicant_"):
        # 예: applicant_0 → idx=0 → 실제 aid = CURRENT_INTERVIEWEE_IDS[0]
        idx = int(speaker.split("_")[1])
        if idx < len(CURRENT_INTERVIEWEE_IDS):
            aid = CURRENT_INTERVIEWEE_IDS[idx]
            add_turn_to_current_block(aid, speaker, text)

    # 4) 기타 화자(Unknown)는 무시
    else:
        return
