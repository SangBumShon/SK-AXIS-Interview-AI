from pydub import AudioSegment
from langchain_community.chat_models import ChatOpenAI
import whisper
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

model = whisper.load_model("base")
openai = OpenAI(api_key=openai_key)

def convert_webm_to_wav(webm_path, wav_path):
    audio = AudioSegment.from_file(webm_path, format="webm")
    audio.export(wav_path, format="wav")

def transcribe_audio_file(wav_path: str) -> str:
    try:
        result = model.transcribe(wav_path)
        raw_text = result["text"]

        prompt = f"""
        다음은 Whisper로 추출한 면접 답변 텍스트입니다:

        "{raw_text}"

        아래 기준에 맞게 면접 답변 스타일로 자연스럽게 다듬어 주세요:
        - 면접관의 질문은 제외하고, 면접자의 답변만 포함
        - 문맥 유지
        - 오타, 띄어쓰기 수정
        - 의미 없는 특수문자 제거
        - 어색한 표현은 공식적이고 부드럽게 고치기
        - 쉼표와 마침표 등 문장 부호 보완

        다듬어진 텍스트만 출력해 주세요.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"음성 인식 중 오류 발생: {str(e)}")
