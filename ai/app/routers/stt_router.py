# app/routers/stt_router.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas.interview import STTUploadResponse
from app.services.pipeline.graph_pipeline import interview_flow_executor
from app.state.store import INTERVIEW_STATE_STORE
from app.state.question_store import QUESTION_STORE
from app.services.interview.stt_service import save_audio_file
from app.services.interview.state_service import create_initial_state

router = APIRouter(prefix="/stt", tags=["STT"])

@router.post("/upload", response_model=STTUploadResponse)
async def upload_stt(
    interviewee_id: int = Form(...),
    audio: UploadFile = File(...),
):
    """답변 단위 음성 파일 업로드 및 STT 파이프라인 실행 (디버깅 포함)"""
    try:
        import traceback

        print(f"\n{'='*30}")
        print(f"[upload_stt] ▶ 인터뷰이 ID: {interviewee_id}")
        print(f"[upload_stt] ▶ 업로드된 파일 이름: {audio.filename}")
        print(f"[upload_stt] ▶ 파일 크기: {audio.size if hasattr(audio, 'size') else 'Unknown'} bytes")

        # 1) 오디오 파일 저장
        file_path = await save_audio_file(interviewee_id, audio)
        print(f"[upload_stt] ✅ 오디오 저장 완료: {file_path}")

        if not file_path:
            raise HTTPException(status_code=500, detail="파일 저장 실패")

        # 2) 상태 가져오기 또는 새로 생성
        state = INTERVIEW_STATE_STORE.get(interviewee_id)
        if state is None:
            print(f"[upload_stt] ℹ️ 새로운 상태 생성 중...")
            questions = QUESTION_STORE.get(interviewee_id, [])
            print(f"[upload_stt] 🔍 질문 목록 ({len(questions)}개): {questions}")
            if not questions:
                print(f"[upload_stt] ⚠ 질문 목록이 비어 있습니다.")
            state = create_initial_state(interviewee_id, questions, file_path)
        else:
            print(f"[upload_stt] 🔁 기존 상태 불러오기")
            state["audio_path"] = file_path

        print(f"[upload_stt] ▶ 초기 상태:")
        for k, v in state.items():
            if isinstance(v, (list, dict)):
                print(f"  - {k}: (len={len(v)})")
            else:
                print(f"  - {k}: {v}")

        # 3) LangGraph 파이프라인 실행
        print(f"[upload_stt] ▶ LangGraph 파이프라인 시작")
        try:
            state = await interview_flow_executor.ainvoke(state, config={"recursion_limit": 50})
        except Exception as e:
            import traceback
            print(f"[upload_stt] ❌ LangGraph 실행 중 예외 발생: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"LangGraph 처리 중 오류 발생: {str(e)}")

        print(f"[upload_stt] ✅ 파이프라인 완료")

        # 4) 상태 저장
        INTERVIEW_STATE_STORE[interviewee_id] = state
        print(f"[upload_stt] ✅ 상태 저장 완료")

        # 5) STT 세그먼트 요약
        print("[upload_stt] ▶ STT 결과 세그먼트 요약:")
        for i, seg in enumerate(state.get("stt", {}).get("segments", [])):
            print(f"  [{i}] {seg['timestamp']} - {seg['raw'][:50]}...")

        print(f"{'='*30}\n")
        return STTUploadResponse(result="OK")

    except Exception as e:
        import traceback
        print(f"[upload_stt] ❌ 전체 예외 발생: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")
