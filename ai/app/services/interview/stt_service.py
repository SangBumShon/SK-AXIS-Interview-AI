import os
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
from openai import OpenAI

from app.services.interview.interview_service import handle_transcription_chunk
# CombinedAudioRecorder가 세그먼트를 끊을 때마다 single_segment_callback("interviewer", wav_bytes) 또는 single_segment_callback("applicant_i", wav_bytes)를 호출합니다.

# 이 콜백은 WAV 파일로 저장한 뒤 Whisper STT를 돌리고, 나온 텍스트를 handle_transcription_chunk(speaker_tag, text)에 넘겨줍니다.

# speaker_tag="applicant_0" 일 때, handle_transcription_chunk 내부에서 idx=0 → CURRENT_INTERVIEWEE_IDS[0]를 실제 지원자 ID로 매핑하여 블록에 답변을 저장합니다.
load_dotenv()
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

USE_WHISPER_API = True
if not USE_WHISPER_API:
    import whisper
    whisper_model = whisper.load_model("small")

async def transcribe_whisper(wav_path: str) -> str:
    """
    Whisper API 또는 로컬 Whisper 모델로 WAV 파일 전사 후 텍스트 반환
    """
    if USE_WHISPER_API:
        with open(wav_path, "rb") as f:
            resp = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        return resp["text"].strip()
    else:
        result = whisper_model.transcribe(wav_path)
        return result["text"]

def single_segment_callback(speaker_tag: str, wav_bytes: bytes):
    """
    CombinedAudioRecorder에서 호출됨:
    - speaker_tag: "interviewer" or "applicant_0" or "applicant_1"
    - wav_bytes: 해당 세그먼트 WAV raw bytes
    → WAV 저장 → Whisper 전사 → handle_transcription_chunk 호출
    """
    import asyncio

    async def _process_and_handle():
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(wav_bytes)

        text = await transcribe_whisper(tmp_path)
        await handle_transcription_chunk(speaker_tag, text)
        os.remove(tmp_path)

    asyncio.get_event_loop().create_task(_process_and_handle())
