# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from .routers.interview_router import router as interview_router
from .routers.stt_router import router as stt_router
from .routers.mock_router import router as mock_router

app = FastAPI(
    title="SK AXIS AI Interview FastAPI",
    description="AI 면접 실시간 녹음, 비언어적 분석, 평가 및 결과물 생성 API",
    version="1.0.0"
)

# ─── CORS 설정 (필요하다면) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",      # Vue 개발 서버
        "http://localhost:8080",      # 다른 포트
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "ws://localhost:3000",        # WebSocket용
        "ws://localhost:8001",],      # 실제 서비스라면 허용 도메인을 제한하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API 라우터 등록 ───
app.include_router(interview_router, prefix="/api/v1")
app.include_router(stt_router, prefix="/api/v1")
app.include_router(mock_router, prefix="/api/v1")


# ─── static 디렉토리를 "/"에 마운트 ───
# project_root/ai/app/static/index.html 이 존재해야 합니다.
app.mount(
    "/static",  # or "/assets", "/public" 등 다른 경로로 변경 가능
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True),
    name="static"
)