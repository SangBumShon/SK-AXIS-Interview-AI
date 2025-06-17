# Multi-stage build 사용
FROM python:3.9-slim as builder

# 빌드 의존성만 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 실행 단계
FROM python:3.9-slim

# 런타임 의존성만 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libpulse0 \
    libportaudio2 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 빌더에서 Python 패키지 복사
COPY --from=builder /root/.local /root/.local

# PATH 설정
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY . .
RUN mkdir -p output app/uploads app/temp static

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]