# # app/main.py

# import uvicorn
# from fastapi import FastAPI
# from app.routers import interview_router, internal_router, nonverbal_router

# app = FastAPI(
#     title="SK AXIS AI Interview FastAPI",
#     description="AI 면접 실시간 녹음/녹화, 평가, 파일 경로 연동 API (다대다 구조 완벽 대응)",
#     version="1.0.0",
#     openapi_url="/api/v1/openapi.json",
#     docs_url="/api/v1/docs"
# )

# # 라우터 등록
# app.include_router(interview_router.router, prefix="/api/v1")
# app.include_router(internal_router.router, prefix="/api/v1")
# app.include_router(nonverbal_router.router, prefix="/api/v1")


# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
# app/main.py

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers.interview_router import router as interview_router
from .routers.nonverbal_router import router as nonverbal_router

app = FastAPI()

# ─── CORS 설정(필요하다면) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 실제 서비스라면 허용 도메인을 제한하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── static 디렉토리를 "/"에 마운트 ───
# index.html 파일이 여기에 있어야 함: project_root/static/index.html
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../static"), html=True), name="static")

# ─── API 라우터 등록 ───
app.include_router(interview_router, prefix="/api")
app.include_router(nonverbal_router, prefix="/api")

# (필요하다면 다른 라우터도 등록)
# app.include_router(다른_라우터, prefix="/…")
