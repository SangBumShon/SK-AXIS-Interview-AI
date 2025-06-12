FROM python:3.9-slim

WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libpulse0 \
    libportaudio2 \
    ffmpeg \
    build-essential \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# OpenCV, MediaPipe 및 STT 관련 패키지 설치
RUN pip install --no-cache-dir \
    opencv-python==4.9.0.80 \
    mediapipe==0.10.5 \
    openai-whisper \
    google-cloud-speech \
    pyaudio \
    pydub \
    fastapi \
    uvicorn \
    python-multipart \
    websockets \
    aiofiles \
    httpx \
    reportlab \
    pandas \
    openpyxl \
    python-dotenv \
    fpdf2

# 애플리케이션 코드 복사
COPY . .

# 출력 디렉토리 생성
RUN mkdir -p output app/uploads app/temp static

# 환경 변수 설정
ENV OPENAI_API_KEY=""
ENV SPRING_API_URL="http://springboot:8080/api/v1"
ENV OUTPUT_DIR="/app/output"
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행 (개발 모드 비활성화)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]