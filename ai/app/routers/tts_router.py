from fastapi import APIRouter, HTTPException, Form
from app.services.tts_service import text_to_speech
import os

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def tts_endpoint(text: str = Form(...)):
    try:
        output_path = os.path.join(UPLOAD_DIR, "openai_tts_output.mp3")
        file_path = text_to_speech(text, output_path)
        return {
            "message": "TTS 처리 완료 (OpenAI TTS)",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))