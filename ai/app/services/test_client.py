from typing import List, Dict, Any

async def fetch_interviewee_questions(interviewee_id: int) -> List[Dict[str, Any]]:
    """
    테스트용 더미 질문 반환
    """
    return [
        {
            "question_id": 1,
            "type": "공통질문",
            "content": "자신의 장점을 말씀해 주세요."
        },
        {
            "question_id": 2,
            "type": "공통질문",
            "content": "팀으로 일할 때 중요하게 생각하는 점은?"
        },
        {
            "question_id": 3,
            "type": "공통질문",
            "content": "본인의 단점은 무엇인가요?"
        },
        {
            "question_id": 4,
            "type": "개별질문",
            "content": "지원 동기가 궁금합니다."
        },
        {
            "question_id": 5,
            "type": "개별질문",
            "content": "자기소개서에서 언급한 경험을 더 자세히 설명해 주세요."
        }
    ] 