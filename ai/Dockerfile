FROM python:3.9-slim

WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# OpenCV 및 MediaPipe 설치
RUN pip install --no-cache-dir opencv-python==4.9.0.80 mediapipe==0.10.5

# 애플리케이션 코드 복사
COPY . .

# 출력 디렉토리 생성
RUN mkdir -p output
RUN mkdir -p app/uploads
RUN mkdir -p static

# 환경 변수 설정
ENV OPENAI_API_KEY=""
ENV SPRING_API_URL="http://springboot:8080/api/v1"
ENV OUTPUT_DIR="/app/output"

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
