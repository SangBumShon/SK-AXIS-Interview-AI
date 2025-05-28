from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn
import os
import json
import asyncio
import base64
import cv2
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.video_processor import VideoProcessor
import openai
from dotenv import load_dotenv
from app.routers.stt_router import router as stt_router # stt_router와 tts_router 임포트
from app.routers.tts_router import router as tts_router  # tts_router 임포트
from app.utils.vision_analyzer import VisionAnalyzer
app = FastAPI(title="면접 평가 시스템 API")

# 명시적으로 .env 파일 경로 지정
dotenv_path = os.path.join(os.path.dirname(__file__), 'app', '.env')
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /Users/phoenix/.../app
UPLOAD_DIR = os.path.join(BASE_DIR, "routers", "uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인으로 제한해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 출력 디렉토리 설정
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 현재 진행 중인 면접 세션 저장
active_interviews: Dict[str, Dict[str, Any]] = {}

# 비디오 프로세서 인스턴스
video_processor = VideoProcessor(output_dir=OUTPUT_DIR, fps=10)

# 정적 파일 서빙 설정
static_dir = Path(__file__).parent.parent / "static"
os.makedirs(static_dir, exist_ok=True)
print(f"Static directory: {static_dir}")
print(f"Static directory exists: {os.path.exists(static_dir)}")
if os.path.exists(static_dir):
    print(f"Files in static directory: {os.listdir(static_dir)}")

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 웹캠 연결 관리 클래스
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.is_capturing = False
        self.stop_event = asyncio.Event()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if not self.active_connections:
            self.stop_capture()

    async def send_frame(self, websocket: WebSocket, frame_data: str, metrics: Dict[str, Any]):
        await websocket.send_json({
            "frame": frame_data,
            "metrics": metrics
        })

    def start_capture(self):
        if not self.is_capturing:
            self.is_capturing = True
            self.stop_event.clear()
            video_processor.start_capture()

    def stop_capture(self):
        if self.is_capturing:
            self.is_capturing = False
            self.stop_event.set()
            video_processor.stop_capture()

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def root():
    # API 요청인 경우 JSON 응답 반환
    if "application/json" in os.environ.get("HTTP_ACCEPT", ""):
        return JSONResponse(content={"message": "면접 평가 시스템 API가 실행 중입니다."})
    
    # 웹 브라우저 요청인 경우 HTML 페이지 반환
    index_path = static_dir / "index.html"
    print(f"Index path: {index_path}")
    print(f"Index exists: {os.path.exists(index_path)}")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return HTMLResponse(f"<html><body><h1>인덱스 파일을 찾을 수 없습니다.</h1><p>경로: {index_path}</p></body></html>")

@app.post("/interview/start")
async def start_interview(interview_id: Optional[str] = None, camera_index: int = 0):
    """면접 세션 시작"""
    # 면접 ID 생성 (지정되지 않은 경우)
    if interview_id is None:
        interview_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 이미 진행 중인 면접인지 확인
    if interview_id in active_interviews:
        raise HTTPException(status_code=400, detail=f"이미 진행 중인 면접 ID: {interview_id}")
    
    # 면접 세션 디렉토리 생성
    interview_dir = os.path.join(OUTPUT_DIR, interview_id)
    os.makedirs(interview_dir, exist_ok=True)
    
    # 비디오 캡처 시작
    success = video_processor.start_capture(camera_index=camera_index, interview_id=interview_id)
    if not success:
        raise HTTPException(status_code=500, detail="카메라를 시작할 수 없습니다.")
    
    # 활성 면접 세션에 추가
    active_interviews[interview_id] = {
        "id": interview_id,
        "start_time": datetime.now().isoformat(),
        "status": "active",
        "output_dir": interview_dir
    }
    
    return {
        "interview_id": interview_id,
        "status": "started",
        "message": f"면접 세션이 시작되었습니다. ID: {interview_id}"
    }

@app.post("/interview/{interview_id}/stop")
async def stop_interview(interview_id: str):
    """면접 세션 종료"""
    # 진행 중인 면접인지 확인
    if interview_id not in active_interviews:
        raise HTTPException(status_code=404, detail=f"진행 중인 면접을 찾을 수 없습니다: {interview_id}")
    
    # 비디오 캡처 종료 및 분석 결과 가져오기
    analysis_summary = video_processor.stop_capture()
    
    # 분석 결과 저장
    interview_dir = active_interviews[interview_id]["output_dir"]
    summary_path = os.path.join(interview_dir, f"{interview_id}_vision_analysis.json")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_summary, f, ensure_ascii=False, indent=2)
    
    # 비언어적 요소 프롬프트 생성 및 저장
    nonverbal_prompt = video_processor.get_nonverbal_prompt()
    prompt_path = os.path.join(interview_dir, f"{interview_id}_nonverbal_prompt.txt")
    
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(nonverbal_prompt)
    
    # 면접 세션 상태 업데이트
    active_interviews[interview_id]["status"] = "completed"
    active_interviews[interview_id]["end_time"] = datetime.now().isoformat()
    active_interviews[interview_id]["analysis_summary"] = summary_path
    active_interviews[interview_id]["nonverbal_prompt"] = prompt_path
    
    return {
        "interview_id": interview_id,
        "status": "completed",
        "analysis_summary": analysis_summary,
        "nonverbal_prompt": nonverbal_prompt,
        "files": {
            "video": os.path.join(OUTPUT_DIR, f"{interview_id}.mp4"),
            "analysis_json": summary_path,
            "nonverbal_prompt": prompt_path
        }
    }

@app.get("/interview/{interview_id}/status")
async def get_interview_status(interview_id: str):
    """면접 세션 상태 확인"""
    if interview_id not in active_interviews:
        raise HTTPException(status_code=404, detail=f"면접 세션을 찾을 수 없습니다: {interview_id}")
    
    return active_interviews[interview_id]

@app.websocket("/ws/video/{interview_id}")
async def websocket_video_endpoint(websocket: WebSocket, interview_id: str):
    """실시간 비디오 스트리밍 웹소켓"""
    await websocket.accept()
    
    try:
        # 면접 세션 확인
        if interview_id not in active_interviews or active_interviews[interview_id]["status"] != "active":
            await websocket.send_json({"error": "활성화된 면접 세션이 아닙니다."})
            await websocket.close()
            return
        
        while True:
            # 프레임 처리
            frame, is_new_frame = video_processor.process_frame()
            
            if frame is None:
                # 프레임이 없으면 잠시 대기
                await asyncio.sleep(0.01)
                continue
            
            if is_new_frame:
                # 프레임을 JPEG로 인코딩
                _, buffer = cv2.imencode('.jpg', frame)
                # 바이너리 데이터로 변환하여 전송
                await websocket.send_bytes(buffer.tobytes())
            
            # 프레임 레이트 조절을 위한 대기
            await asyncio.sleep(0.01)
    
    except WebSocketDisconnect:
        print(f"클라이언트 연결 종료: {interview_id}")
    except Exception as e:
        print(f"웹소켓 오류: {str(e)}")
    finally:
        # 연결 종료 시 처리
        if websocket.client_state != 0:  # 이미 닫히지 않은 경우에만
            await websocket.close()

@app.get("/interviews")
async def list_interviews():
    """모든 면접 세션 목록 조회"""
    return list(active_interviews.values())

@app.delete("/interview/{interview_id}")
async def delete_interview(interview_id: str):
    """면접 세션 삭제"""
    if interview_id not in active_interviews:
        raise HTTPException(status_code=404, detail=f"면접 세션을 찾을 수 없습니다: {interview_id}")
    
    # 활성 면접인 경우 먼저 종료
    if active_interviews[interview_id]["status"] == "active":
        await stop_interview(interview_id)
    
    # 면접 세션 정보 삭제
    del active_interviews[interview_id]
    
    return {"status": "deleted", "interview_id": interview_id}

# 비디오 프레임 처리 및 전송 루프
async def process_frames():
    while manager.is_capturing:
        # 프레임 처리가 필요한지 확인
        processed_frame, is_new_frame = video_processor.process_frame()
        
        if is_new_frame and processed_frame is not None:
            # 프레임을 JPEG로 인코딩
            _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            # Base64로 인코딩
            frame_data = base64.b64encode(buffer).decode('utf-8')
            
            # 분석 결과 가져오기
            metrics = video_processor.vision_analyzer.get_current_metrics()
            
            # 모든 연결된 클라이언트에 전송
            for connection in manager.active_connections:
                try:
                    await manager.send_frame(connection, frame_data, metrics)
                except Exception as e:
                    print(f"프레임 전송 오류: {e}")
        
        # 프레임 레이트 제어
        await asyncio.sleep(0.01)  # 10ms 대기

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # 캡처 시작
    manager.start_capture()
    
    # 프레임 처리 태스크 시작
    task = asyncio.create_task(process_frames())
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            command = json.loads(data)
            
            if command.get("action") == "stop":
                manager.stop_capture()
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        # 태스크 취소
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

@app.get("/analysis")
async def get_analysis():
    """분석 결과 요약 반환"""
    # 분석 결과가 없는 경우를 대비한 기본 응답 생성
    if video_processor.vision_analyzer.frame_count == 0:
        return {
            "error": "분석된 프레임이 없습니다.",
            "face_detection": {"rate": 0, "comment": "얼굴이 감지되지 않았습니다."},
            "smile": {"rate": 0, "comment": "표정 분석을 할 수 없습니다."},
            "posture": {"rate": 0, "comment": "자세 분석을 할 수 없습니다."},
            "eye_contact": {"rate": 0, "comment": "시선 처리 분석을 할 수 없습니다."},
            "gesture": {"rate": 0, "comment": "제스처 분석을 할 수 없습니다."},
            "blink": {"comment": "눈 깜빡임 분석을 할 수 없습니다."},
            "overall_score": 0
        }
    
    # 분석 결과 요약 가져오기
    analysis = video_processor.vision_analyzer.get_analysis_summary()
    return analysis

if __name__ == "__main__":
    import cv2  # 여기서 임포트해야 uvicorn 실행 시 문제 없음
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)