from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import subprocess
import uuid

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_audio_from_video(video_path: str, audio_path: str):
    command = [
        "ffmpeg",
        "-i", video_path,
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path,
        "-y"
    ]
    subprocess.run(command, check=True)

@router.post("/")
async def upload_chunk(video_chunk: UploadFile = File(...)):
    # 유니크 파일명으로 저장 (chunk마다 충돌 방지)
    unique_id = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_DIR, f"{unique_id}.webm")
    audio_path = os.path.join(UPLOAD_DIR, f"{unique_id}.wav")

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video_chunk.file, buffer)

    try:
        extract_audio_from_video(video_path, audio_path)
        from app.services.stt_service import transcribe_audio_file
        # text = transcribe_audio_file(audio_path)
        text = transcribe_audio_file("/Users/park/Downloads/voice-ai-pjt-rpt/app/routers/uploads/output.wav")
        # .txt 파일로 저장
        text_file_path = os.path.join(UPLOAD_DIR, f"{unique_id}.txt")
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(text)

        from app.services.evaluation_service import evaluate_answer
        evaluation_result = evaluate_answer(text)
        return {"text": evaluation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
