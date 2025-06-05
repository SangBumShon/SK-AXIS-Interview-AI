import sounddevice as sd
import numpy as np
import wave
from threading import Thread, Event
from tempfile import NamedTemporaryFile
from pathlib import Path
import time

# mouth_open_state를 통해 “왼쪽(idx=0) 지원자” 혹은 “오른쪽(idx=1) 지원자”가 입을 벌린 시점을 기록합니다.

# RMS(음량) 계산으로 “실제 발화 여부”를 판단하고, Hangover를 적용해 잠깐의 음량 저하나 입닫힘을 무시합니다.

# “지원자 A/B가 말하는 동안”은 speaker="applicant_0" 또는 "applicant_1"로, “면접관(둘 다 안 말함 + RMS 기준 만족)”은 speaker="interviewer"로 인식합니다.

# speaker != current_speaker 구간에서만 세그먼트를 끊고 WAV로 저장하여, Whisper STT로 넘깁니다.

# MediaPipe 전역 상태 import
from app.services.interview.mediapipe_service import mouth_open_state

# Smoothing/Hangover 파라미터
MOUTH_HOLD_TIME = 0.2        # 입열림 신호를 0.2초 동안 유지
SPEECH_HANGOVER_TIME = 0.3   # RMS가 기준 아래로 내려가도 0.3초 동안은 같은 화자 유지

class CombinedAudioRecorder:
    def __init__(
        self,
        samplerate: int = 16000,
        channels: int = 1,
        callback=None  # callback(speaker_tag, wav_bytes)
    ):
        """
        :param samplerate: 오디오 샘플링 레이트(Hz)
        :param channels: 채널 수(1=mono)
        :param callback: 녹음 세그먼트 종료 시 호출할 함수 → (speaker_tag, wav_bytes)
        """
        self.sr = samplerate
        self.ch = channels
        self.callback = callback

        self._stop_event = Event()
        self._thread: Thread | None = None

        # 현재 화자 상태: None / "interviewer" / "applicant_i"
        self.current_speaker: str | None = None
        # PCM raw를 누적할 버퍼
        self.segment_buffer = bytearray()
        # RawInputStream 인스턴스
        self._stream: sd.RawInputStream | None = None

        # “입열림(True)”이 마지막으로 감지된 시각 (time.time() 기준)
        self._last_mouth_open_time = [0.0, 0.0]  # [왼쪽 지원자, 오른쪽 지원자]

        # 마지막으로 “충분한 음량”이 감지된 시각
        self._last_voiced_time = 0.0

    def _detect_speaker(self, pcm_bytes: bytes) -> str | None:
        """
        pcm_bytes: int16 raw bytes (0.1초 분량)
        - MediaPipe 입열림 Smoothing + RMS 기반 Hangover 적용
        """
        now = time.time()

        # 1) PCM raw → numpy array → RMS 계산
        audio_arr = np.frombuffer(pcm_bytes, dtype=np.int16)
        rms = np.sqrt(np.mean(audio_arr.astype(np.float32) ** 2))

        # 2) MediaPipe 입열림 신호 감지 시각 갱신
        for idx, is_open in enumerate(mouth_open_state):
            if is_open:
                self._last_mouth_open_time[idx] = now

        # 3) “지원자 i” 입열림 여부(hold) 판단 (마지막 입열림으로부터 MOUTH_HOLD_TIME 이내)
        applicant_active = None
        for idx in (0, 1):
            if now - self._last_mouth_open_time[idx] <= MOUTH_HOLD_TIME and rms > 500:
                applicant_active = f"applicant_{idx}"
                break

        # 4) “Hangover”용: 최근 SPEECH_HANGOVER_TIME 이내에 rms>threshold였다면
        if rms > 500:
            self._last_voiced_time = now

        # (A) 이전 화자가 interviewer이고, 최근 음성(Hangover) 상태라면 interviewer 유지
        if self.current_speaker == "interviewer" and (now - self._last_voiced_time) <= SPEECH_HANGOVER_TIME:
            return "interviewer"

        # (B) applicant_active가 있으면 지원자
        if applicant_active is not None:
            return applicant_active

        # (C) RMS가 충분히 높으면 면접관(발화 중)
        if rms > 500:
            return "interviewer"

        # (D) 그 외에는 “침묵”
        return None

    def _process_segment_end(self, speaker: str, pcm_bytes: bytes):
        """
        화자 세그먼트가 끝났을 때 호출
        - PCM raw → 임시 WAV 파일로 저장 → callback(speaker, wav_bytes)
        """
        with NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name

        wf = wave.open(wav_path, 'wb')
        wf.setnchannels(self.ch)
        wf.setsampwidth(2)  # int16 → 2바이트
        wf.setframerate(self.sr)
        wf.writeframes(pcm_bytes)
        wf.close()

        with open(wav_path, 'rb') as f:
            wav_bytes = f.read()

        if self.callback:
            self.callback(speaker, wav_bytes)

        Path(wav_path).unlink(missing_ok=True)

    def _recording_loop(self):
        """
        백그라운드 스레드로 실행됨
        - 0.1초 단위로 RawInputStream을 읽으면서 화자 전환 감지
        """
        def sd_callback(indata, frames, time_info, status):
            if self._stop_event.is_set():
                raise sd.CallbackStop()

            pcm_bytes = indata.tobytes()
            speaker = self._detect_speaker(pcm_bytes)

            # 1) 화자 전환 시 이전 세그먼트 마감
            if speaker != self.current_speaker:
                if self.current_speaker is not None and self.segment_buffer:
                    self._process_segment_end(self.current_speaker, bytes(self.segment_buffer))
                self.current_speaker = speaker
                self.segment_buffer = bytearray()

            # 2) 화자가 None(침묵)이면 녹음 중단
            if speaker is None:
                return

            # 3) 화자가 “interviewer” 또는 “applicant_i”이면 PCM 누적
            self.segment_buffer.extend(pcm_bytes)

        block_size = int(self.sr * 0.1)  # 0.1초 단위
        self._stream = sd.RawInputStream(
            samplerate=self.sr,
            channels=self.ch,
            dtype='int16',
            blocksize=block_size,
            callback=sd_callback
        )
        self._stream.start()

        try:
            while not self._stop_event.is_set():
                time.sleep(0.05)
        except Exception:
            pass

        # 종료 시 남은 버퍼 마감
        if self.current_speaker is not None and self.segment_buffer:
            self._process_segment_end(self.current_speaker, bytes(self.segment_buffer))

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.current_speaker = None
        self.segment_buffer = bytearray()
        self._last_mouth_open_time = [0.0, 0.0]
        self._last_voiced_time = 0.0
        self._thread = Thread(target=self._recording_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
