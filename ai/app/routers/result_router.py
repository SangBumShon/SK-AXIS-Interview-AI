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
        
        # 디버깅을 위한 로그 추가
        print(f"[DEBUG] 요청된 interviewee_ids: {interviewee_ids}")
        print(f"[DEBUG] 파싱된 id_list: {id_list}")
        print(f"[DEBUG] INTERVIEW_STATE_STORE 키 목록: {list(INTERVIEW_STATE_STORE.keys())}")
        print(f"[DEBUG] INTERVIEW_STATE_STORE 크기: {len(INTERVIEW_STATE_STORE)}")
        
        for interviewee_id in id_list:
            str_key = str(interviewee_id)
            state = INTERVIEW_STATE_STORE.get(str_key)
            
            print(f"[DEBUG] interviewee_id: {interviewee_id}, str_key: '{str_key}', state found: {state is not None}")
            
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
            state = INTERVIEW_STATE_STORE.get(str(interviewee_id))
            
            # 상태가 없거나 평가가 완료되지 않은 경우 건너뜀
            if not state or not isinstance(state, dict) or not state.get("report", {}).get("pdf_path"):
                continue
            
            # 역량 점수 추출
            competencies = {}
            if "evaluation" in state and isinstance(state["evaluation"], dict) and "results" in state["evaluation"]:
                eval_results = state["evaluation"]["results"]
                
                # SK 역량 점수 (SUPEX, VWBE, Passionate, Proactive, Professional, People)
                sk_competencies = ["SUPEX", "VWBE", "Passionate", "Proactive", "Professional", "People"]
                for key in sk_competencies:
                    if key in eval_results and isinstance(eval_results[key], dict):
                        competencies[key] = eval_results[key].get("score", 0)
                
                # 직무/도메인 점수
                domain_competencies = ["기술/직무", "도메인 전문성"]
                for key in domain_competencies:
                    if key in eval_results and isinstance(eval_results[key], dict):
                        # '/' 문자는 JSON 키로 사용 시 문제가 될 수 있어 '.'로 변경
                        safe_key = key.replace("/", ".")
                        competencies[safe_key] = eval_results[key].get("score", 0)
            
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
                
                # 언어적 평가 (verbal_score, verbal_reason 사용)
                if "verbal_score" in summary:
                    language["score"] = summary["verbal_score"]
                if "verbal_reason" in summary:
                    reason = summary["verbal_reason"]
                    # list인 경우 문자열로 변환
                    if isinstance(reason, list):
                        language["reason"] = "\n".join(reason)
                    else:
                        language["reason"] = reason
                
                # 비언어적 평가 (nonverbal_score, nonverbal_reason 사용)
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
