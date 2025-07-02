# app/routers/result_router.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv

from app.state.store import INTERVIEW_STATE_STORE
from app.schemas.result import (
    ResultStatusResponse,
    ResultStatusListResponse,
    FinalResultResponse,
    FinalResultListResponse
)

# 환경 변수 로드
load_dotenv()

router = APIRouter(prefix="/results", tags=["Result"])

# S3 버킷 정보 (실제 환경에 맞게 수정 필요)
S3_BUCKET = os.getenv("S3_BUCKET", "sk-axis-bucket")
REPORT_PREFIX = os.getenv("REPORT_PREFIX", "reports")

@router.get("/statuses", response_model=ResultStatusListResponse)
async def get_result_statuses(
    interviewee_ids: str = Query(..., description="쉼표로 구분된 면접자 ID 목록 ex) 101,102")
):
    """
    다수 면접자의 평가 상태를 확인하는 API (폴링용)
    """
    try:
        # 쉼표로 구분된 문자열을 정수 리스트로 변환
        id_list = [int(id_str) for id_str in interviewee_ids.split(",") if id_str.strip()]
        
        if not id_list:
            raise HTTPException(status_code=400, detail="유효한 면접자 ID가 제공되지 않았습니다.")
        
        result_statuses = []
        
        for interviewee_id in id_list:
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            
            # 기본 응답 구조
            status_response = ResultStatusResponse(
                interviewee_id=interviewee_id,
                status="PENDING",
                score=None,
                pdf_path=None
            )
            
            # 상태가 존재하고 report 정보가 있으면 DONE으로 처리
            if state and isinstance(state, dict) and state.get("report", {}).get("pdf_path"):
                status_response.status = "DONE"
                
                # 점수 정보 추출 (summary에서 가져옴)
                if "summary" in state and isinstance(state["summary"], dict) and "total_score" in state["summary"]:
                    status_response.score = state["summary"]["total_score"]
                
                # PDF 경로 설정
                status_response.pdf_path = state["report"]["pdf_path"]
            
            result_statuses.append(status_response)
        
        return result_statuses
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"상태 조회 중 오류 발생: {str(e)}")

@router.get("", response_model=FinalResultListResponse)
async def get_final_results(
    interviewee_ids: str = Query(..., description="쉼표로 구분된 면접자 ID 목록 ex) 101,102")
):
    """
    다수 면접자의 최종 평가 결과를 조회하는 API
    """
    try:
        # 쉼표로 구분된 문자열을 정수 리스트로 변환
        id_list = [int(id_str) for id_str in interviewee_ids.split(",") if id_str.strip()]
        
        if not id_list:
            raise HTTPException(status_code=400, detail="유효한 면접자 ID가 제공되지 않았습니다.")
        
        # 평가 항목별 비중 (일단은 고정값)
        weights = {
            "언어적 요소": "45%",
            "직무·도메인": "45%",
            "비언어적 요소": "10%"
        }
        
        results = []
        
        for interviewee_id in id_list:
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            
            # 상태가 없거나 평가가 완료되지 않은 경우 건너뜀
            if not state or not isinstance(state, dict) or not state.get("report", {}).get("pdf_path"):
                continue
            
            # 역량 점수 추출
            competencies = {}
            if "evaluation" in state and isinstance(state["evaluation"], dict) and "results" in state["evaluation"]:
                eval_results = state["evaluation"]["results"]
                
                # SK 역량 점수 (SUPEX, VWBE, Passionate, Proactive, Professional, People)
                for key in ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]:
                    if key in eval_results:
                        competencies[key] = eval_results[key].get("score", 0)
                
                # 직무/도메인 점수
                for key in ["기술/직무", "도메인 전문성"]:
                    if key in eval_results:
                        # '/' 문자는 JSON 키로 사용 시 문제가 될 수 있어 '.'로 변경
                        competencies[key.replace("/", ".")] = eval_results[key].get("score", 0)
            
            # 언어적 평가 요약
            language = {
                "score": 0,
                "reason": "평가 정보가 없습니다."
            }
            
            # 비언어적 평가 요약
            nonverbal = {
                "score": 0,
                "reason": "평가 정보가 없습니다."
            }
            
            # 요약 정보에서 언어적/비언어적 점수와 이유 추출
            if "summary" in state and isinstance(state["summary"], dict):
                summary = state["summary"]
                
                # 언어적 평가
                if "language_score" in summary:
                    language["score"] = summary["language_score"]
                if "language_reason" in summary:
                    language["reason"] = summary["language_reason"]
                
                # 비언어적 평가
                if "nonverbal_score" in summary:
                    nonverbal["score"] = summary["nonverbal_score"]
                if "nonverbal_reason" in summary:
                    nonverbal["reason"] = summary["nonverbal_reason"]
            
            # PDF 경로
            pdf_path = state["report"]["pdf_path"]
            
            # 결과 객체 생성
            result = FinalResultResponse(
                interviewee_id=interviewee_id,
                competencies=competencies,
                language=language,
                nonverbal=nonverbal,
                pdf_path=pdf_path
            )
            
            results.append(result)
        
        # 최종 응답 생성
        return FinalResultListResponse(
            weights=weights,
            results=results
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"결과 조회 중 오류 발생: {str(e)}")
