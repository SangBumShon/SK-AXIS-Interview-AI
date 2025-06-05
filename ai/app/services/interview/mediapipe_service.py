import cv2
import mediapipe as mp
import time
from threading import Thread, Event

# 전역 상태: 왼쪽 지원자(applicant_0), 오른쪽 지원자(applicant_1)의 입 열림 여부
mouth_open_state = [False, False]

class VideoStreamer:
    def __init__(self, camera_index: int = 0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"카메라 {camera_index}을 열 수 없습니다.")

        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True
        )
        self._stop_event = Event()
        self._thread: Thread | None = None

    def _run(self):
        # 첫 프레임 읽어서 해상도 확인
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("카메라에서 영상을 읽을 수 없습니다.")
        height, width, _ = frame.shape

        # 입술 거리 임계값 (픽셀 단위). 환경에 맞춰 조정 필요
        LIP_OPEN_THRESHOLD = 15

        while not self._stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_face_mesh.process(rgb)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # (1) 상순(landmark 13), 하순(landmark 14) 좌표
                lip_top = face_landmarks.landmark[13]
                lip_bottom = face_landmarks.landmark[14]
                y_top = int(lip_top.y * height)
                y_bot = int(lip_bottom.y * height)
                lip_distance = abs(y_bot - y_top)

                # (2) 얼굴 중심 x 좌표 (landmark 1)로 왼쪽/오른쪽 구분
                face_center = face_landmarks.landmark[1]
                x_center = int(face_center.x * width)
                side_idx = 0 if x_center < width // 2 else 1

                # (3) 전역 상태 갱신
                mouth_open_state[side_idx] = (lip_distance > LIP_OPEN_THRESHOLD)

            time.sleep(0.03)

        self.cap.release()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
