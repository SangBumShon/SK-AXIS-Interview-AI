from pydub import AudioSegment
import openai
import os
from dotenv import load_dotenv


# 📦 .env 환경 변수 로드
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

# 🔑 OpenAI API Key 로드 및 클라이언트 초기화
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("❌ OPENAI_API_KEY가 .env에 정의되지 않았습니다.")
openai.api_key = os.getenv("OPENAI_API_KEY")

#🧠 OpenAI Whisper API를 통한 STT 수행
def transcribe_audio_file(file_path: str) -> str:
    """
    Whisper API를 사용하여 주어진 오디오 파일을 텍스트로 전사함
    """
    with open(file_path, "rb") as f:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=f,
            response_format="text"
        )
    return transcript.strip()
