# app/services/internal_client.py

import httpx
from typing import List, Dict

SPRINGBOOT_BASE_URL = "http://3.38.218.18:8080/api/v1"

async def fetch_interviewee_questions(interviewee_id: int) -> List[Dict]:
    """
    FastAPI → Spring Boot: 지원자별 면접 질문 5개 조회
    """
    url = f"{SPRINGBOOT_BASE_URL}/internal/interviewee/{interviewee_id}/questions"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json().get("questions", [])
        elif response.status_code == 404:
            return []
        else:
            response.raise_for_status()