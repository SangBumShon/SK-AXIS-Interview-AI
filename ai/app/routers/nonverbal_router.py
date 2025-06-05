from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

router = APIRouter()

# 비언어적 요소 데이터 모델
class NonverbalData(BaseModel):
    timestamp: float  # 타임스탬프
    emotion: str  # 감정 상태
    posture: str  # 자세
    eye_contact: bool  # 시선 접촉
    voice_tone: str  # 목소리 톤
    confidence_score: float  # 자신감 점수 (0-1)
    additional_notes: Optional[str] = None  # 추가 메모

# 비언어적 요소 분석 결과 저장
class NonverbalAnalysis(BaseModel):
    interview_id: str
    start_time: datetime
    end_time: datetime
    nonverbal_data: List[NonverbalData]
    overall_analysis: Dict[str, float]  # 전체 분석 결과

# 결과를 저장할 디렉토리
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../results")
os.makedirs(RESULTS_DIR, exist_ok=True)

@router.post("/nonverbal")
async def save_nonverbal_data(data: NonverbalData):
    """
    비언어적 요소 데이터를 저장
    """
    try:
        # 현재 시간을 파일명으로 사용
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(RESULTS_DIR, f"nonverbal_{timestamp}.json")
        
        # 데이터를 JSON으로 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "message": "비언어적 요소 데이터가 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nonverbal/analysis")
async def save_nonverbal_analysis(analysis: NonverbalAnalysis):
    """
    비언어적 요소 분석 결과를 저장
    """
    try:
        # 인터뷰 ID를 파일명으로 사용
        file_path = os.path.join(RESULTS_DIR, f"nonverbal_analysis_{analysis.interview_id}.json")
        
        # 분석 결과를 JSON으로 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(analysis.dict(), f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "message": "비언어적 요소 분석 결과가 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nonverbal/analysis/{interview_id}")
async def get_nonverbal_analysis(interview_id: str):
    """
    특정 인터뷰의 비언어적 요소 분석 결과를 조회
    """
    try:
        file_path = os.path.join(RESULTS_DIR, f"nonverbal_analysis_{interview_id}.json")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        with open(file_path, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        
        return analysis_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 