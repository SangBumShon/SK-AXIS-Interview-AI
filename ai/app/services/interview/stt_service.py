"""
SK AXIS AI 면접 음성 인식 (STT) 서비스

이 파일은 면접 중 녹음된 음성을 텍스트로 변환하는 STT 서비스입니다.
주요 기능:
- WebM 오디오 파일 처리 및 검증
- OpenAI Whisper API를 통한 한국어 음성 인식
- 파일 손상 검사 및 오류 처리
- STT 결과 후처리 및 필터링

성능 최적화:
- 파일 헤더만 읽어서 빠른 검증 (전체 파일을 로드하지 않고 헤더만 읽어서 빠른 검증)
- 손상된 WebM 파일 사전 감지
- 잘못된 STT 결과 필터링 (유튜브 관련 오인식 제거)
"""

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

def is_valid_audio_file(file_path: str) -> bool:
    """
    오디오 파일이 손상되었는지 빠르게 검사합니다.
    성능 최적화: 헤더만 읽어서 빠른 검증
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(file_path):
            print(f"[파일 검사] 파일이 존재하지 않음: {file_path}")
            return False

        # 파일 크기 확인 (0바이트 파일 감지)
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            print(f"[파일 검사] 빈 파일 감지: {file_path}")
            return False

        # 최소 크기 확인 (1KB 미만은 의심스러움)
        if file_size < 1024:
            print(f"[파일 검사] 파일이 너무 작음: {file_path} ({file_size} bytes)")
            return False

        # 🚀 성능 최적화: 파일 헤더만 읽어서 빠른 검증
        try:
            with open(file_path, 'rb') as f:
                # 처음 1KB만 읽어서 헤더 확인
                header = f.read(1024)

                # WebM 파일 시그니처 확인
                if file_path.lower().endswith('.webm'):
                    # WebM은 EBML 헤더로 시작 (0x1A, 0x45, 0xDF, 0xA3)
                    if len(header) < 4 or header[:4] != b'\x1A\x45\xDF\xA3':
                        print(f"[파일 검사] 잘못된 WebM 헤더: {file_path}")
                        return False

                # 기본적인 파일 무결성 확인 (전체 파일 읽지 않음)
                # 파일 끝부분도 확인 (마지막 100바이트)
                if file_size > 100:
                    f.seek(-100, 2)  # 파일 끝에서 100바이트 전으로 이동
                    tail = f.read(100)
                    if len(tail) == 0:
                        print(f"[파일 검사] 파일 끝 부분 읽기 실패: {file_path}")
                        return False

            print(f"[파일 검사] ✅ 유효한 오디오 파일: {file_path} ({file_size} bytes)")
            return True

        except Exception as e:
            print(f"[파일 검사] 파일 헤더 읽기 실패: {file_path} - {e}")
            return False

    except Exception as e:
        print(f"[파일 검사] 파일 검사 중 오류: {file_path} - {e}")
        return False

# 🧠 OpenAI Whisper API를 통한 STT 수행
def transcribe_audio_file(file_path: str) -> str:
    """
    Whisper API를 사용하여 주어진 오디오 파일을 텍스트로 전사함
    """
    # 🔍 파일 유효성 검사 먼저 수행
    if not is_valid_audio_file(file_path):
        print(f"[STT] ❌ 손상된 오디오 파일 감지: {file_path}")
        return "음성 파일이 손상되어 인식할 수 없습니다."
    
    try:
        print(f"[STT] 📄 STT 처리 시작: {file_path}")

        with open(file_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
                language="ko",
                # 프롬프트 추가로 맥락 제공
            )

    except Exception as e:
        print(f"[STT] ❌ OpenAI API 오류: {e}")
        # OpenAI API 오류 시 기본 텍스트 반환
        return "음성을 명확하게 인식할 수 없습니다."
    
    # response_format="text" 를 사용하면 문자열이 반환됩니다.
    result = transcript.strip()

    # 후처리: 명백히 잘못된 변환 필터링
    if is_invalid_transcription(result):
        print(f"[STT 후처리] ❌ 잘못된 변환 감지되어 필터링됨: '{result}'")
        return "음성을 명확하게 인식할 수 없습니다."
    
    print(f"[STT 후처리] ✅ 유효한 변환 결과: '{result}'")
    return result

def is_invalid_transcription(text: str) -> bool:
    """
    명백히 잘못된 STT 결과를 감지합니다.
    """
    if not text or len(text.strip()) == 0:
        return True

    # 잘못된 변환 패턴들 (띄어쓰기 변형 포함)
    invalid_patterns = [
        "시청해주셔서 감사합니다",
        "시청 해주셔서 감사합니다", 
        "시청해 주셔서 감사합니다",
        "오늘도 영상 시청 해주셔서 감사합니다",
        "오늘도 시청해 주셔서 감사합니다",
        "오늘도 시청해주셔서 감사합니다",
        "영상 시청해주셔서 감사합니다",
        "영상 시청해 주셔서 감사합니다",
        "시청 감사합니다",
        "시청해주셔서",
        "시청해 주셔서",
        "먹방",
        "빠이빠이", 
        "구독",
        "영상 시청",
        "채널",
        "유튜브",
        "좋아요",
        "구독 버튼",
        "알림 설정"
    ]

    text_lower = text.lower()
    for pattern in invalid_patterns:
        if pattern in text_lower:
            print(f"[STT 필터링] 감지된 유튜브 관련 패턴: '{pattern}' in '{text[:50]}...'")
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