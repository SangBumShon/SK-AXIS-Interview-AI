# app/services/internal_client.py

import httpx
import os
from typing import List, Dict

# .env 파일에 정의된 SPRING_API_URL 환경 변수 사용
# 기본값은 Docker Compose에서 정의한 서비스 이름 사용
SPRINGBOOT_BASE_URL = os.environ.get("SPRING_API_URL", "http://sk-axis-springboot:8080/api/v1")

async def fetch_interviewee_questions(interviewee_id: int) -> List[Dict]:
    """
    FastAPI → Spring Boot: 지원자별 면접 질문 5개 조회 (단일 지원자)
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


async def fetch_multiple_interviewee_questions(interviewee_ids: List[int]) -> Dict[str, List[Dict]]:
    """
    FastAPI → Spring Boot: 다중 지원자 질문 5개 조회 (여러 지원자)
    """
    url = f"{SPRINGBOOT_BASE_URL}/internal/interviewees/questions"
    payload = {"interviewee_ids": interviewee_ids}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("questions_per_interviewee", {})
        elif response.status_code == 404:
            return {}
        else:
            response.raise_for_status()