from pydub import AudioSegment
from openai import OpenAI
import os
from dotenv import load_dotenv
from fastapi import UploadFile
import whisper
from typing import Optional
from datetime import datetime
import numpy as np


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
    # 오디오 전처리 비활성화 (원본 파일 직접 사용)
    # processed_path = preprocess_audio(file_path)
    
    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
            language="ko",
            # 프롬프트 추가로 맥락 제공
        )
    
    # 전처리된 임시 파일 삭제 (전처리 비활성화로 주석 처리)
    # if processed_path != file_path and os.path.exists(processed_path):
    #     os.remove(processed_path)
    
    # response_format="text" 를 사용하면 문자열이 반환됩니다.
    result = transcript.strip()
    
    # 후처리: 명백히 잘못된 변환 필터링
    if is_invalid_transcription(result):
        print(f"[STT 후처리] 잘못된 변환 감지: {result}")
        return "음성을 명확하게 인식할 수 없습니다."
    
    return result

def is_invalid_transcription(text: str) -> bool:
    """
    명백히 잘못된 STT 결과를 감지합니다.
    """
    if not text or len(text.strip()) == 0:
        return True
    
    # 잘못된 변환 패턴들
    invalid_patterns = [
        "시청해주셔서 감사합니다",
        "시청 해주셔서 감사합니다",
        "오늘도 영상 시청 해주셔서 감사합니다",
        "먹방",
        "빠이빠이", 
        "구독",
        "영상 시청",
        "채널",
        "유튜브"
    ]
    
    text_lower = text.lower()
    for pattern in invalid_patterns:
        if pattern in text_lower:
            return True
    
    # 너무 짧은 의미없는 단어들
    if len(text.strip()) < 3:
        return True
        
    return False

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

