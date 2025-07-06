# app/main.py
"""
SK AXIS AI 면접 시스템 - FastAPI 메인 애플리케이션

이 파일은 AI 면접 시스템의 FastAPI 애플리케이션 진입점입니다.
주요 기능:
- 실시간 음성 녹음 및 STT 처리
- 비언어적 분석 (표정 분석)
- AI 기반 면접 평가 및 점수 산출
- 면접 결과 리포트 생성

API 구조:
- /api/v1/interview/* : 면접 시작/종료, 상태 관리
- /api/v1/stt/* : 음성-텍스트 변환 처리
- /api/v1/results/* : 평가 결과 조회 및 리포트 생성
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

# 각 도메인별 라우터 임포트
from .routers.interview_router import router as interview_router  # 면접 관리 API
from .routers.stt_router import router as stt_router              # STT 처리 API
from .routers.result_router import router as result_router        # 결과 조회 API

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="SK AXIS AI Interview FastAPI",
    description="AI 면접 실시간 녹음, 비언어적 분석, 평가 및 결과물 생성 API",
    version="1.0.0"
)

# ─── CORS 설정 ───
# 프론트엔드(Vue.js)에서 API 호출을 위한 CORS 정책 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 모든 도메인 허용 (개발용, 운영시 특정 도메인으로 제한 필요)
    allow_credentials=True,   # 쿠키/인증 정보 포함 요청 허용
    allow_methods=["*"],      # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],      # 모든 헤더 허용
)

# ─── API 라우터 등록 ───
# 각 도메인별 API 엔드포인트를 /api/v1 경로 하위에 등록
app.include_router(interview_router, prefix="/api/v1")  # 면접 관리: /api/v1/interview/*
app.include_router(stt_router, prefix="/api/v1")        # STT 처리: /api/v1/stt/*
app.include_router(result_router, prefix="/api/v1")     # 결과 조회: /api/v1/results/*

# ─── 정적 파일 서빙 ───
# 리포트 이미지, CSS, JS 등 정적 파일을 서빙하기 위한 설정
# project_root/ai/app/static/ 디렉토리의 파일들을 /static 경로로 접근 가능
app.mount(
    "/static",  # URL 경로 (예: http://localhost:8000/static/report.html)
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True),
    name="static"
)