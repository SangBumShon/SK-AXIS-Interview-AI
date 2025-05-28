import cv2
import base64
import json
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os
from typing import List, Dict, Any

from app.video_processor import VideoProcessor

app = FastAPI()

# 정적 파일 서빙 설정
static_dir = Path(__file__).parent.parent / "static"
os.makedirs(static_dir, exist_ok=True)

# 정적 파일 경로 디버그 출력
print(f"Static directory: {static_dir}")
print(f"Static directory exists: {os.path.exists(static_dir)}")
if os.path.exists(static_dir):
    print(f"Files in static directory: {os.listdir(static_dir)}")

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 비디오 프로세서 초기화
video_processor = VideoProcessor(output_dir=str(Path(__file__).parent.parent / "output"))

# 웹소켓 연결을 관리하는 클래스
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

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = static_dir / "index.html"
    print(f"Index path: {index_path}")
    print(f"Index exists: {os.path.exists(index_path)}")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return HTMLResponse(f"<html><body><h1>인덱스 파일을 찾을 수 없습니다.</h1><p>경로: {index_path}</p></body></html>")

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
    # 캡처가 진행 중이 아니더라도 분석 결과 제공
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
    uvicorn.run("app.webcam_server:app", host="127.0.0.1", port=8000, reload=True)
