"""
SK AXIS AI 면접 시스템 - 면접 라우터

이 파일은 면접 진행과 관련된 API 엔드포인트를 정의합니다.
주요 기능:
- 면접 종료 처리 및 최종 평가 실행
- 비언어적 데이터 수집 및 분석
- LangGraph 기반 AI 평가 파이프라인 실행

API 엔드포인트:
- POST /interview/end: 면접 종료 및 최종 리포트 생성

주요 처리 흐름:
1. 비언어적 데이터 수집 (표정)
2. 마지막 음성 파일 STT 처리
3. AI 기반 종합 평가 실행
4. 최종 리포트 생성 및 저장

참고사항:
- /interview/start 엔드포인트는 현재 SpringBoot에서 처리하므로 비활성화
- 추후 AI 로직 확장 시 필요하면 활성화 가능
"""

# app/routers/interview_router.py
from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
import httpx

from app.schemas.interview import (
    StartInterviewRequest,
    StartInterviewResponse,
    EndInterviewRequest,
    EndInterviewResponse,
    Question,
    NonverbalData
)

from app.services.pipeline.graph_pipeline import final_flow_executor, interview_flow_executor
from app.schemas.state import InterviewState
from app.state.store import INTERVIEW_STATE_STORE  # 전역 메모리 스토어
from app.services.interview.nonverbal_service import evaluate
from app.state.question_store import QUESTION_STORE

from app.services.interview.interview_end_processing_service import (
    process_last_audio_segment,
    save_nonverbal_counts
)

# 환경 변수 로드
load_dotenv()

router = APIRouter(prefix="/interview", tags=["Interview"])

RESULT_DIR = os.getenv("RESULT_DIR", "./result")
os.makedirs(RESULT_DIR, exist_ok=True)

SPRINGBOOT_BASE_URL = os.getenv("SPRING_API_URL", "http://localhost:8080/api/v1")

# ──────────────── 🚀 면접 시작 엔드포인트 (현재 비활성화) ────────────────
# 
# 현재 면접 시작은 SpringBoot에서 처리하므로 이 엔드포인트는 사용하지 않음
# 추후 AI 로직 확장 시 (예: 실시간 질문 생성, 맞춤형 질문 추천 등) 활성화 가능
# 
# @router.post("/start", response_model=StartInterviewResponse)
# async def start_interview(req: StartInterviewRequest):
#     """
#     면접 시작 및 질문 로드 (현재 비활성화)
#     
#     SpringBoot 백엔드에서 질문을 가져와 QUESTION_STORE에 저장
#     추후 AI 기반 질문 생성 로직 추가 시 활용 예정
#     """
#     url = f"{SPRINGBOOT_BASE_URL}/interviews/start"
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, json={"interviewee_ids": req.interviewee_ids})
#         if response.status_code == 200:
#             questions_per_interviewee = response.json().get("questions_per_interviewee", {})
#             if not questions_per_interviewee:
#                 raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
#             for interviewee_id, questions in questions_per_interviewee.items():
#                 QUESTION_STORE[int(interviewee_id)] = questions
#             return StartInterviewResponse(questions_per_interviewee=questions_per_interviewee)
#         else:
#             raise HTTPException(status_code=response.status_code, detail="질문을 찾을 수 없습니다.")

# ──────────────── 🏁 면접 종료 엔드포인트 ────────────────

@router.post("/end", response_model=EndInterviewResponse)
async def end_interview(req: EndInterviewRequest):
    """
    면접 종료 및 최종 평가 처리
    
    Args:
        req (EndInterviewRequest): 면접 종료 요청 (면접 ID, 비언어적 데이터 포함)
    
    Returns:
        EndInterviewResponse: 처리 결과 및 리포트 생성 상태
    
    처리 과정:
    1. 각 면접자별로 상태 데이터 조회
    2. 비언어적 데이터 변환 및 저장
    3. 마지막 음성 파일 STT 처리 (interview_flow_executor)
    4. 최종 리포트 생성 (final_flow_executor)
    5. done 플래그 설정 및 상태 저장
    
    Note:
        - LangGraph 기반 AI 파이프라인 실행
        - 비동기 처리로 다중 면접자 동시 처리
        - 오류 발생 시 부분 처리 결과 반환
    """
    processed_count = 0
    skipped_ids = []

    try:
        # 각 면접자별로 순차 처리
        for interviewee_id_str, nv in req.data.items():
            interviewee_id = int(interviewee_id_str)
            print(f"[DEBUG] Processing interviewee_id: {interviewee_id}")

            # 면접자 상태 데이터 조회
            state = INTERVIEW_STATE_STORE.get(interviewee_id)
            print(f"[TRACE] INTERVIEW_STATE_STORE 조회: interviewee_id={interviewee_id}, found={state is not None}")

            # 상태 데이터 유효성 검증
            if not isinstance(state, dict):
                print(f"[ERROR] [INTERVIEW_ROUTER] state가 dict가 아님! interviewee_id={interviewee_id}, 실제 타입: {type(state)}, 값: {state}")
                skipped_ids.append(interviewee_id)
                continue

            # 비언어적 데이터 변환
            if not isinstance(nv, NonverbalData):
                nv = NonverbalData(**nv)
            print(f"[DEBUG] 변환된 nv 데이터: {nv}")

            # (1) 마지막 녹음 파일 STT 처리
            audio_path = state.get("audio_path")
            if audio_path:  # 처리할 음성 파일이 있는 경우
                print(f"[DEBUG] audio_path 존재함: {audio_path}")
                # LangGraph interview_flow_executor 실행 (STT → 재작성 → 평가)
                state = await interview_flow_executor.ainvoke(state, config={"recursion_limit": 10})
                state["audio_path"] = ""  # 중복 실행 방지

            # (2) 비언어적 데이터 저장
            state["nonverbal_counts"] = {
                "expression": nv.facial_expression.dict(),
                "timestamp": nv.timestamp,
            }
            print(f"[DEBUG] state['nonverbal_counts']: {state['nonverbal_counts']}")

            # (3) 최종 리포트 생성
            print(f"[DEBUG] final_flow_executor 실행 전 - done: {state.get('done')}")
            # LangGraph final_flow_executor 실행 (종합 평가 → 최종 리포트)
            state = await final_flow_executor.ainvoke(state, config={"recursion_limit": 10})
            print(f"[DEBUG] final_flow_executor 실행 후 - done: {state.get('done')}")
            
            # done 플래그 수동 설정 (파이프라인에서 누락된 경우)
            if state.get("done") is None and state.get("summary"):
                state["done"] = True
                print(f"[DEBUG] done 플래그 수동 설정 - summary 존재로 인해 완료 처리")
            
            # 처리 완료된 상태 저장
            INTERVIEW_STATE_STORE[interviewee_id] = state
            print(f"[DEBUG] INTERVIEW_STATE_STORE 저장 완료 - interviewee_id: {interviewee_id}, done: {state.get('done')}")

            processed_count += 1

        # 처리 결과 반환
        if processed_count == 0:
            return EndInterviewResponse(
                result="partial",
                report_ready=False,
            )

        return EndInterviewResponse(
            result="done" if len(skipped_ids) == 0 else "partial",
            report_ready=True,
            message=None if len(skipped_ids) == 0 else f"Skipped interviewees: {skipped_ids}"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[DEBUG] Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
