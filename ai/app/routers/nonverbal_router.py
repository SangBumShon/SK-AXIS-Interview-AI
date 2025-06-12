import os
import json
import threading
import numpy as np
import sounddevice as sd

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from scipy.io.wavfile import write
from typing import Dict, List
from datetime import datetime

from app.schemas.nonverbal import NonverbalData
from app.schemas.state import InterviewState
from app.services.pipeline.graph_pipeline import interview_flow_executor
from app.state.store import INTERVIEW_STATE_STORE

router = APIRouter(tags=["Nonverbal"])

class AudioRecorder:
    def __init__(self, output_dir: str, interview_id: int, interviewee_id: str):
        self.output_dir = output_dir
        self.interview_id = interview_id
        self.interviewee_id = interviewee_id
        self.fs = 16000
        self.channels = 1
        self._buffer: List[np.ndarray] = []
        self._is_recording = False
        self._stream: sd.InputStream | None = None
        self.wav_path: str | None = None

    def _callback(self, indata: np.ndarray, frames: int, time_info, status):
        if self._is_recording:
            self._buffer.append(indata.copy())

    def start(self):
        if self._is_recording:
            return
        self._buffer = []
        self._stream = sd.InputStream(
            samplerate=self.fs,
            channels=self.channels,
            callback=self._callback
        )
        self._stream.start()
        self._is_recording = True
        print(f"▶ [Recorder] {self.interviewee_id} 녹음 시작")

    def stop_and_save(self):
        if not self._is_recording or self._stream is None:
            return None
        self._is_recording = False
        self._stream.stop()
        self._stream.close()
        self._stream = None
        print(f"▶ [Recorder] {self.interviewee_id} 녹음 중지, WAV로 저장 중...")

        audio_data = np.concatenate(self._buffer, axis=0)
        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_{self.interview_id}_{self.interviewee_id}_{timestamp}.wav"
        wav_path = os.path.join(self.output_dir, filename)
        write(wav_path, self.fs, audio_data)
        self.wav_path = wav_path
        print(f"✅ [Recorder] 저장 완료: {wav_path}")
        return wav_path

# 전역 상태 저장소
active_recorders: Dict[str, AudioRecorder] = {}
inactive_count_map: Dict[str, int] = {}  # ✅ 누락되었던 선언 추가
CURRENT_INTERVIEW_ID = 1

@router.websocket("/ws/nonverbal")
async def websocket_nonverbal_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("▶ WebSocket 연결 수락됨 (/ws/nonverbal)")

    try:
        while True:
            text_data: str = await websocket.receive_text()
            try:
                raw = json.loads(text_data)
                if isinstance(raw, list):
                    nonverbal_list: List[NonverbalData] = [
                        NonverbalData.parse_obj(item) for item in raw
                    ]
                else:
                    single_obj = NonverbalData.parse_obj(raw)
                    nonverbal_list = [single_obj]

                for nv in nonverbal_list:
                    interviewee_id = nv.interviewee_id
                    is_speaking = nv.is_speaking
                    print(f"[수신] interviewee_id={interviewee_id}, is_speaking={is_speaking}")

                    if is_speaking:
                        inactive_count_map[interviewee_id] = 0

                        if interviewee_id not in active_recorders:
                            recorder = AudioRecorder(
                                output_dir="./temp_recordings",
                                interview_id=CURRENT_INTERVIEW_ID,
                                interviewee_id=interviewee_id
                            )
                            active_recorders[interviewee_id] = recorder
                            thread = threading.Thread(target=recorder.start, daemon=True)
                            thread.start()

                    else:
                        inactive_count_map[interviewee_id] = inactive_count_map.get(interviewee_id, 0) + 1
                        print(f" 비발화 누적 횟수: {inactive_count_map[interviewee_id]}")

                        if inactive_count_map[interviewee_id] >= 3:
                            if interviewee_id in active_recorders:
                                recorder = active_recorders.pop(interviewee_id)
                                wav_path = recorder.stop_and_save()
                                inactive_count_map[interviewee_id] = 0  # 초기화

                                if wav_path:
                                    state = INTERVIEW_STATE_STORE.get(interviewee_id, {
                                        "interviewee_id": interviewee_id,
                                        "audio_path": wav_path,
                                        "stt": {"done": False, "segments": []},
                                        "rewrite": {"done": False, "items": []},
                                        "evaluation": {"done": False, "results": {}},
                                        "report": {"pdf_path": ""},
                                        "decision_log": [],
                                    })
                                    state["audio_path"] = wav_path
                                    await interview_flow_executor(state)
                                    INTERVIEW_STATE_STORE[interviewee_id] = state

            except json.JSONDecodeError:
                print("⚠ 잘못된 JSON 메시지:", text_data)
            except Exception as ex:
                print("⚠ WebSocket 메시지 처리 중 예외:", ex)

    except WebSocketDisconnect:
        print("◀ 클라이언트 연결 종료 (/ws/nonverbal)")
    except Exception as e:
        print("◀ WebSocket 처리 중 치명적 예외:", e)
