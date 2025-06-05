# app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers.interview_router import router as interview_router
from .routers.internal_router import router as internal_router

app = FastAPI(
    title="SK AXIS AI Interview FastAPI",
    description="AI 면접 실시간 녹음, 비언어적 분석, 평가 및 결과물 생성 API",
    version="1.0.0"
)

# ─── CORS 설정 (필요하다면) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 실제 서비스라면 허용 도메인을 제한하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ─── API 라우터 등록 ───
app.include_router(interview_router, prefix="/api/v1")
app.include_router(internal_router, prefix="/api/v1")


# ─── static 디렉토리를 "/"에 마운트 ───
# project_root/ai/app/static/index.html 이 존재해야 합니다.
app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True),
    name="static"
)