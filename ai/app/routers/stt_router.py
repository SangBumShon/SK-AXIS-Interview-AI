from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.interview import STTUploadResponse
from app.services.interview.stt_service import save_audio_file
from app.services.queue_executor import enqueue_task  # ⬅️ 인터뷰이별 큐 실행기
import asyncio

router = APIRouter(prefix="/stt", tags=["STT"])

# 인터뷰이별 Lock 관리
interviewee_locks = {}

@router.post("/upload", response_model=STTUploadResponse)
async def upload_stt(
    interviewee_id: int = Form(...),
    audio: UploadFile = File(...),
):
    try:
        print(f"\n{'='*30}")
        print(f"[upload_stt] ▶ 인터뷰이 ID: {interviewee_id}")
        print(f"[upload_stt] ▶ 업로드된 파일 이름: {audio.filename}")
        print(f"[upload_stt] ▶ 파일 크기: {audio.size if hasattr(audio, 'size') else 'Unknown'} bytes")

        # 1) 오디오 파일 저장
        file_path = await save_audio_file(interviewee_id, audio)
        print(f"[upload_stt] ✅ 오디오 저장 완료: {file_path}")

        if not file_path:
            raise HTTPException(status_code=500, detail="파일 저장 실패")

        # 2) 인터뷰이별 Lock 생성 (순차 처리 보장)
        if interviewee_id not in interviewee_locks:
            interviewee_locks[interviewee_id] = asyncio.Lock()
        
        async with interviewee_locks[interviewee_id]:
            print(f"[upload_stt] 🔒 Lock 획득 - 인터뷰이 {interviewee_id}")
            
            # 3) 실제 작업 정의 (큐에 넣을 비동기 함수)
            async def process():
                from app.state.store import INTERVIEW_STATE_STORE
                from app.state.question_store import QUESTION_STORE
                from app.services.pipeline.graph_pipeline import interview_flow_executor
                from app.services.interview.state_service import create_initial_state
                import traceback

                print(f"\n{'='*30}")
                print(f"[process] ▶ 인터뷰이 ID: {interviewee_id}")
                print(f"[process] ▶ 오디오 경로: {file_path}")

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

                print(f"[process] ▶ 상태 요약:")
                for k, v in state.items():
                    if isinstance(v, (list, dict)):
                        print(f"  - {k}: (len={len(v)})")
                    else:
                        print(f"  - {k}: {v}")

                try:
                    print(f"[process] ▶ LangGraph 실행 시작")
                    state = await interview_flow_executor.ainvoke(state, config={"recursion_limit": 10})
                    print(f"[process] ✅ 파이프라인 완료")
                except Exception as e:
                    print(f"[process] ❌ LangGraph 실행 오류: {e}")
                    traceback.print_exc()
                    return

                # 타입 체크 및 추적 로그 추가
                print(f"[TRACE] INTERVIEW_STATE_STORE 저장 전: interviewee_id={interviewee_id}, state type={type(state)}")
                if not isinstance(state, dict):
                    print(f"[ERROR] [STT_ROUTER] state에 dict가 아닌 값이 저장되려 합니다! 실제 타입: {type(state)}, 값: {state}")
                INTERVIEW_STATE_STORE[interviewee_id] = state
                print(f"[TRACE] INTERVIEW_STATE_STORE 저장 완료: interviewee_id={interviewee_id}, state type={type(INTERVIEW_STATE_STORE[interviewee_id])}")

                print(f"[process] ▶ STT 세그먼트 요약:")
                for i, seg in enumerate(state.get("stt", {}).get("segments", [])):
                    print(f"  [{i}] {seg['timestamp']} - {seg['raw'][:50]}...")

                print(f"{'='*30}\n")

            # 4) 큐에 등록
            await enqueue_task(interviewee_id, process)
            print(f"[upload_stt] 🔓 Lock 해제 - 인터뷰이 {interviewee_id}")

        # 5) 클라이언트에 즉시 응답
        return STTUploadResponse(result="Queued")

    except Exception as e:
        import traceback
        print(f"[upload_stt] ❌ 전체 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
