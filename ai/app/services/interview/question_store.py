from typing import List, Dict
from collections import defaultdict

# 전역 임시 저장소 (메모리 기반)
applicant_question_metadata: Dict[int, List[Dict]] = defaultdict(list)

def store_question_analysis(applicant_id: int, question_number: int, intent: str, keywords: List[str]):
    applicant_question_metadata[applicant_id].append({
        "question_id": question_number,
        "intent": intent,
        "keywords": keywords
    })

def get_question_analysis(applicant_id: int) -> List[Dict]:
    return applicant_question_metadata.get(applicant_id, [])
