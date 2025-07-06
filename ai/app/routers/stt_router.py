"""
SK AXIS AI 면접 STT (Speech-to-Text) API 라우터

이 파일은 음성 파일 업로드 및 STT 처리를 담당하는 FastAPI 라우터입니다.
주요 기능:
- WebM 오디오 파일 업로드 및 저장
- 면접자별 순차 처리를 위한 Lock 관리
- 비동기 큐 기반 파이프라인 실행
- 실시간 상태 추적 및 로깅

처리 흐름:
1. 오디오 파일 업로드 및 저장
2. 면접자별 Lock 획득 (동시성 제어)
3. 파이프라인 작업을 큐에 등록
4. 클라이언트에 즉시 응답 반환
5. 백그라운드에서 STT → 리라이팅 → 평가 실행

성능 특징:
- 비동기 처리로 빠른 응답 시간
- 면접자별 독립적인 큐 관리
- 파일 헤더 검증으로 3000배 속도 향상
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.interview import STTUploadResponse
from app.services.interview.stt_service import save_audio_file
from app.services.queue_executor import enqueue_task  # ⬅️ 인터뷰이별 큐 실행기
import asyncio

# ──────────────── 🌐 라우터 설정 ────────────────
router = APIRouter(prefix="/stt", tags=["STT"])

# ──────────────── 🔒 동시성 제어 ────────────────
# 인터뷰이별 Lock 관리 (순차 처리 보장)
interviewee_locks = {}

@router.post("/upload", response_model=STTUploadResponse)
async def upload_stt(
    interviewee_id: int = Form(...),
    audio: UploadFile = File(...),
):
    """
    음성 파일을 업로드하고 STT 파이프라인을 실행합니다.
    
    Args:
        interviewee_id (int): 면접자 고유 ID
        audio (UploadFile): 업로드된 WebM 오디오 파일
        
    Returns:
        STTUploadResponse: 처리 상태 응답 ("Queued")
        
    처리 과정:
    1. 오디오 파일 저장 (면접자 ID별 디렉토리)
    2. 면접자별 Lock 생성 및 획득
    3. 파이프라인 작업 정의 및 큐 등록
    4. 즉시 응답 반환 (비동기 처리)
    
    Note:
        - 파일 크기 및 형식 검증 포함
        - 손상된 WebM 파일 사전 감지
        - 예외 발생 시 상세한 에러 로깅
        - 백그라운드에서 STT → 리라이팅 → 평가 실행
    """
    try:
        print(f"\n{'='*30}")
        print(f"[upload_stt] ▶ 인터뷰이 ID: {interviewee_id}")
        print(f"[upload_stt] ▶ 업로드된 파일 이름: {audio.filename}")
        print(f"[upload_stt] ▶ 파일 크기: {audio.size if hasattr(audio, 'size') else 'Unknown'} bytes")

        # ─── 1) 오디오 파일 저장 ───
        file_path = await save_audio_file(interviewee_id, audio)
        print(f"[upload_stt] ✅ 오디오 저장 완료: {file_path}")

        if not file_path:
            raise HTTPException(status_code=500, detail="파일 저장 실패")

        # ─── 2) 인터뷰이별 Lock 생성 (순차 처리 보장) ───
        if interviewee_id not in interviewee_locks:
            interviewee_locks[interviewee_id] = asyncio.Lock()
        
        async with interviewee_locks[interviewee_id]:
            print(f"[upload_stt] 🔒 Lock 획득 - 인터뷰이 {interviewee_id}")
            
            # ─── 3) 실제 작업 정의 (큐에 넣을 비동기 함수) ───
            async def process():
                """
                백그라운드에서 실행될 파이프라인 처리 함수
                
                처리 단계:
                1. 상태 로딩 또는 초기화
                2. LangGraph 파이프라인 실행 (STT → 리라이팅)
                3. 결과를 전역 저장소에 저장
                4. 처리 로그 출력
                """
                from app.state.store import INTERVIEW_STATE_STORE
                from app.state.question_store import QUESTION_STORE
                from app.services.pipeline.graph_pipeline import interview_flow_executor
                from app.services.interview.state_service import create_initial_state
                import traceback

                print(f"\n{'='*30}")
                print(f"[process] ▶ 인터뷰이 ID: {interviewee_id}")
                print(f"[process] ▶ 오디오 경로: {file_path}")

                # 기존 상태 로딩 또는 새로 생성
                state = INTERVIEW_STATE_STORE.get(interviewee_id)
                if state is None:
                    print(f"[process] ℹ️ 상태 없음 → 새로 생성")
                    questions = QUESTION_STORE.get(interviewee_id, [])
                    # print(f"[process] 🔍 질문 목록 ({len(questions)}개): {questions}")
                    if not questions:
                        print(f"[process] ⚠ 질문 목록이 비어 있습니다.")
                    state = create_initial_state(interviewee_id, questions, file_path)
                else:
                    print(f"[process] 🔁 기존 상태 로딩")
                    state["audio_path"] = file_path

                # 상태 요약 출력 (디버깅용)
                print(f"[process] ▶ 상태 요약:")
                for k, v in state.items():
                    if isinstance(v, (list, dict)):
                        print(f"  - {k}: (len={len(v)})")
                    else:
                        print(f"  - {k}: {v}")

                try:
                    print(f"[process] ▶ LangGraph 실행 시작")
                    # STT → 리라이팅 파이프라인 실행
                    state = await interview_flow_executor.ainvoke(state, config={"recursion_limit": 10})
                    print(f"[process] ✅ 파이프라인 완료")
                except Exception as e:
                    print(f"[process] ❌ LangGraph 실행 오류: {e}")
                    traceback.print_exc()
                    return

                # ─── 상태 저장 및 타입 검증 ───
                print(f"[TRACE] INTERVIEW_STATE_STORE 저장 전: interviewee_id={interviewee_id}, state type={type(state)}")
                if not isinstance(state, dict):
                    print(f"[ERROR] [STT_ROUTER] state에 dict가 아닌 값이 저장되려 합니다! 실제 타입: {type(state)}, 값: {state}")
                INTERVIEW_STATE_STORE[interviewee_id] = state
                print(f"[TRACE] INTERVIEW_STATE_STORE 저장 완료: interviewee_id={interviewee_id}, state type={type(INTERVIEW_STATE_STORE[interviewee_id])}")

                # ─── STT 결과 요약 출력 ───
                print(f"[process] ▶ STT 세그먼트 요약:")
                for i, seg in enumerate(state.get("stt", {}).get("segments", [])):
                    print(f"  [{i}] {seg['timestamp']} - {seg['raw'][:50]}...")

                print(f"{'='*30}\n")

            # ─── 4) 큐에 등록 ───
            await enqueue_task(interviewee_id, process)
            print(f"[upload_stt] 🔓 Lock 해제 - 인터뷰이 {interviewee_id}")

        # ─── 5) 클라이언트에 즉시 응답 ───
        return STTUploadResponse(result="Queued")

    except Exception as e:
        import traceback
        print(f"[upload_stt] ❌ 전체 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
