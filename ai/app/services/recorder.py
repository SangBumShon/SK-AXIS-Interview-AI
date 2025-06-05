import cv2
import sounddevice as sd
import numpy as np
import threading
import time
from scipy.io.wavfile import write


def record_video(video_path: str, duration: int = 60, camera_index: int = 0):
    """
    비디오를 로컬 카메라에서 녹화합니다.

    :param video_path: 저장할 mp4 파일 경로
    :param duration: 녹화 시간 (초)
    :param camera_index: 사용할 카메라 장치 번호
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"카메라 {camera_index}를 열 수 없습니다.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    start_time = time.time()
    print(f"🎥 비디오 녹화 시작 ({duration}초)...")
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"✅ 비디오 녹화 완료: {video_path}")


def record_audio(audio_path: str, duration: int = 60, fs: int = 16000, audio_device: int = None):
    """
    오디오를 지정된 마이크 장치에서 녹음합니다.

    :param audio_path: 저장할 wav 파일 경로
    :param duration: 녹음 시간 (초)
    :param fs: 샘플링 주파수
    :param audio_device: 사용할 오디오 장치 번호 (없으면 기본 장치 사용)
    """
    print(f"🎙️ 오디오 녹음 시작 ({duration}초)...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16', device=audio_device)
    sd.wait()
    write(audio_path, fs, audio)
    print(f"✅ 오디오 녹음 완료: {audio_path}")


def record_both(video_path: str, audio_path: str, duration: int = 60, camera_index: int = 0, audio_device: int = None):
    """
    비디오와 오디오를 동시에 녹화합니다.

    :param video_path: mp4 파일 경로
    :param audio_path: wav 파일 경로
    :param duration: 녹화 시간
    :param camera_index: 카메라 번호
    :param audio_device: 마이크 번호
    """
    t1 = threading.Thread(target=record_video, args=(video_path, duration, camera_index))
    t2 = threading.Thread(target=record_audio, args=(audio_path, duration, 16000, audio_device))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

