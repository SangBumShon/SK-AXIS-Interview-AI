# app/services/interview/question_block_handler.py

from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime

# 현재 진행 중인 블록을 지원자별로 관리
current_blocks: Dict[int, Dict] = {}
# 완료된(평가 대기 중) 블록을 지원자별로 관리
finalized_blocks: Dict[int, List[Dict]] = {}

def start_new_block(applicant_id: int, matched_question_id: int):
    block_id = str(uuid4())
    new_block = {
        "block_id": block_id,
        "representative_question_id": matched_question_id,
        "start_time": datetime.utcnow().isoformat(),
        "turns": []  # [{"speaker":"interviewer","text":"…"}, {"speaker":"applicant_0","text":"…"}]
    }
    current_blocks[applicant_id] = new_block
    return block_id

def get_current_block(applicant_id: int) -> Optional[Dict]:
    return current_blocks.get(applicant_id)

def add_turn_to_current_block(applicant_id: int, speaker: str, text: str):
    blk = get_current_block(applicant_id)
    if blk:
        blk["turns"].append({"speaker": speaker, "text": text})

def finalize_current_block(applicant_id: int) -> Optional[Dict]:
    blk = get_current_block(applicant_id)
    if blk:
        blk["end_time"] = datetime.utcnow().isoformat()
        return blk
    return None

from app.services.interview.question_store import get_question_analysis

def get_question_intent_and_keywords(applicant_id: int, question_id: int):
    lst = get_question_analysis(applicant_id)
    for entry in lst:
        if entry["question_id"] == question_id:
            return entry["intent"], entry["keywords"]
    return "", []

def get_all_blocks(applicant_id: int) -> List[Dict]:
    return finalized_blocks.get(applicant_id, [])
