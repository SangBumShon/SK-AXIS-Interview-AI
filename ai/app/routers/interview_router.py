from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import httpx, time, os
from dotenv import load_dotenv
import json
import asyncio

from app.services.internal_client import fetch_interviewee_questions
from app.services.interview.initial_question_analyzer import generate_applicant_question_metadata
from app.services.interview.question_block_handler import (
    finalize_current_block,
    get_all_blocks
)
from app.services.interview.block_processor import finalize_and_process_block
from app.services.interview.report_service import create_radar_chart, generate_pdf

from app.services.interview.mediapipe_service import VideoStreamer
from app.services.interview.recorder_service import CombinedAudioRecorder
from app.services.interview.stt_service import single_segment_callback
from app.services.interview.interview_state import CURRENT_INTERVIEWEE_IDS, IS_STREAMING

from app.schemas.interview import (
    StartInterviewRequest,
    StartInterviewResponse,
    EndInterviewRequest,
    EndInterviewResponse
)
# /interview/start 시점에 VideoStreamer(MediaPipe)와 CombinedAudioRecorder를 동시에 시작합니다.

# CombinedAudioRecorder는 "왼쪽/오른쪽 지원자 입열림 + RMS"를 조합해, 계속해서 화자를 감지하며 한 세그먼트가 끝나는 순간마다 single_segment_callback을 호출합니다.

# single_segment_callback → "WAV 저장 → Whisper 전사 → handle_transcription_chunk("interviewer" or "applicant_i", text)" 형태로 블록 매칭/평가 로직이 작동합니다.

# /interview/end에서 두 개의 스트리머를 중단하고, 마지막 열린 블록을 마감하여 리포트 생성 → Spring Boot 전송까지 이어집니다.
load_dotenv()
router = APIRouter(tags=["Interview"])

# 결과 저장 경로 (환경변수 RESULT_DIR 없으면 "./result")
RESULT_DIR = os.getenv("RESULT_DIR", "./result")
os.makedirs(RESULT_DIR, exist_ok=True)

_video_streamer: VideoStreamer | None = None
_audio_recorder: CombinedAudioRecorder | None = None


@router.post("/interview/start", response_model=StartInterviewResponse)
async def start_interview(req: StartInterviewRequest):
    """
    - Spring Boot에서 지원자별 질문 5개 내려받고 초기 분석
    - VideoStreamer(MediaPipe) & CombinedAudioRecorder(start) 실행
    """
    global _video_streamer, _audio_recorder

    questions_per_interviewee: Dict[int, List] = {}
    for interviewee_id in req.interviewee_ids:
        raw_list = await fetch_interviewee_questions(interviewee_id)
        if not raw_list:
            raise HTTPException(
                status_code=404,
                detail=f"지원자 ID {interviewee_id}의 질문을 찾을 수 없습니다."
            )

        # 질문 의도+키워드 분석
        question_dicts = [{"id": q["question_id"], "text": q["content"]} for q in raw_list]
        await generate_applicant_question_metadata(
            applicant_id=interviewee_id,
            question_list=question_dicts
        )

        # 응답 스키마 매핑
        questions_per_interviewee[interviewee_id] = [
            {
                "question_id": q["question_id"],
                "type": q["type"],
                "content": q["content"]
            }
            for q in raw_list
        ]

    CURRENT_INTERVIEWEE_IDS.clear()
    CURRENT_INTERVIEWEE_IDS.update(req.interviewee_ids)
    IS_STREAMING = True

    # 1) MediaPipe VideoStreamer 시작
    if not _video_streamer:
        _video_streamer = VideoStreamer(camera_index=0)
        _video_streamer.start()

    # 2) CombinedAudioRecorder 시작 (callback=single_segment_callback)
    if not _audio_recorder:
        _audio_recorder = CombinedAudioRecorder(
            samplerate=16000,
            channels=1,
            callback=single_segment_callback
        )
        _audio_recorder.start()

    return StartInterviewResponse(
        questions_per_interviewee=questions_per_interviewee,
        status="started"
    )


@router.post("/interview/end", response_model=EndInterviewResponse)
async def end_interview(req: EndInterviewRequest):
    """
    - CombinedAudioRecorder 및 VideoStreamer 중단
    - 열린 블록 마감 → 평가 → PDF/엑셀 생성 → Spring Boot 전송
    """
    global IS_STREAMING, _video_streamer, _audio_recorder

    try:
        # 1) 오디오 녹음기 중단
        if _audio_recorder:
            _audio_recorder.stop()
            _audio_recorder = None

        # 2) 비디오 스트리머 중단
        if _video_streamer:
            _video_streamer.stop()
            _video_streamer = None

        # 3) 열린 블록 모두 마감 → 평가
        IS_STREAMING = False
        for interviewee_id in CURRENT_INTERVIEWEE_IDS:
            last_blk = finalize_current_block(interviewee_id)
            if last_blk:
                await finalize_and_process_block(interviewee_id)

        # 4) PDF/엑셀 생성 및 Spring Boot 전송
        batch_payload = {"interview_id": req.interview_id, "results": []}
        from app.services.interview.question_block_handler import finalized_blocks

        for interviewee_id in CURRENT_INTERVIEWEE_IDS:
            comp_results: Dict[str, Dict] = {}
            for b in finalized_blocks.get(interviewee_id, []):
                qid_str = str(b["question_id"])
                comp_results[qid_str] = {
                    "avg_score": 0,
                    "reasons": b["evaluation"]["raw_response"]
                }

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(RESULT_DIR, f"interview_{interviewee_id}_{timestamp}_chart.png")
            pdf_path   = os.path.join(RESULT_DIR, f"interview_{interviewee_id}_{timestamp}_report.pdf")
            excel_path = os.path.join(RESULT_DIR, f"interview_{interviewee_id}_{timestamp}_result.xlsx")
            stt_path   = os.path.join(RESULT_DIR, f"interview_{interviewee_id}_{timestamp}_stt.txt")

            interview_date = time.strftime("%Y-%m-%d %H:%M:%S")
            applicant_name = f"Applicant_{interviewee_id}"
            question_blocks = get_all_blocks(interviewee_id)

            create_radar_chart(comp_results, chart_path)
            generate_pdf(
                comp_results=comp_results,
                chart_path=chart_path,
                output_path=pdf_path,
                applicant_name=applicant_name,
                interview_date=interview_date,
                question_blocks=[{
                    "question": str(b["question_id"]),
                    "summary": b["evaluation"]["raw_response"]
                } for b in finalized_blocks.get(interviewee_id, [])]
            )

            # TODO: 엑셀 생성 함수 호출 → excel_path

            scores = [
                int(b["evaluation"].get("score", 0))
                for b in finalized_blocks.get(interviewee_id, [])
            ]
            average_score = sum(scores) // len(scores) if scores else 0
            comment = finalized_blocks.get(interviewee_id, [])[0]["evaluation"]["raw_response"] \
                      if finalized_blocks.get(interviewee_id) else ""

            batch_payload["results"].append({
                "interviewee_id": interviewee_id,
                "score": average_score,
                "comment": comment,
                "pdf_path": pdf_path,
                "excel_path": excel_path,
                "stt_path": stt_path
            })

        springboot_url = f"http://springboot:8080/api/v1/internal/interview/{req.interview_id}/results"
        async with httpx.AsyncClient() as client:
            resp = await client.post(springboot_url, json=batch_payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Spring Boot 연동 실패")

        return EndInterviewResponse(result="done", report_ready=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
