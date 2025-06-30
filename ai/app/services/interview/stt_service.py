from pydub import AudioSegment
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi import UploadFile
import whisper
from typing import Optional
from datetime import datetime


# 📦 .env 환경 변수 로드
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

# 🔑 OpenAI API Key 로드 및 클라이언트 초기화
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("❌ OPENAI_API_KEY가 .env에 정의되지 않았습니다.")
# OpenAI Python v1.x 클라이언트 초기화
client = OpenAI(api_key=openai_key)

# Whisper 모델 초기화
model = whisper.load_model("base")

#🧠 OpenAI Whisper API를 통한 STT 수행
def transcribe_audio_file(file_path: str) -> str:
    """
    Whisper API를 사용하여 주어진 오디오 파일을 텍스트로 전사함
    """
    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
            language="ko"
        )
    # response_format="text" 를 사용하면 문자열이 반환됩니다.
    return transcript.strip()

async def process_audio_file(interviewee_id: int, audio_file: UploadFile) -> Optional[str]:
    """
    업로드된 오디오 파일을 처리하고 STT 결과를 반환합니다.
    
    Args:
        interviewee_id: 면접자 ID
        audio_file: 업로드된 WebM 오디오 파일
        
    Returns:
        str: STT 처리 결과 텍스트
    """
    try:
        # 임시 파일로 저장
        temp_path = f"temp_{interviewee_id}_{audio_file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        # Whisper로 STT 처리
        result = model.transcribe(temp_path, language="ko")
        
        # 임시 파일 삭제
        os.remove(temp_path)
        
        return result["text"]
        
    except Exception as e:
        print(f"STT 처리 중 오류 발생: {str(e)}")
        return None

async def save_audio_file(interviewee_id: int, audio_file: UploadFile) -> Optional[str]:
    """
    업로드된 오디오 파일을 uploads 디렉토리에 저장합니다.
    
    Args:
        interviewee_id: 면접자 ID
        audio_file: 업로드된 WebM 오디오 파일
        
    Returns:
        str: 저장된 파일 경로
    """
    try:
        # uploads 디렉토리 생성
        save_dir = os.path.join("uploads")
        os.makedirs(save_dir, exist_ok=True)
        
        # 파일명 생성 (interviewee_id_timestamp.webm 형식)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{interviewee_id}_{timestamp}.webm"
        
        # 파일 저장
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        return file_path
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")
        return None
