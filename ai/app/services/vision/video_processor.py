import cv2
import numpy as np
import time
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from app.utils.vision_analyzer import VisionAnalyzer


class VideoProcessor:
    """
    면접자의 영상을 처리하고 분석하는 클래스
    - 영상 캡처 및 저장
    - 비언어적 요소 분석
    - 분석 결과 요약
    """

    def __init__(self, output_dir: str = "./output", fps: int = 10):
        """
        Args:
            output_dir: 영상 및 분석 결과 저장 디렉토리
            fps: 분석할 프레임 레이트 (초당 프레임 수)
        """
        self.output_dir = output_dir
        self.target_fps = fps
        self.vision_analyzer = VisionAnalyzer()
        # self.video_writer = None  # 영상 저장 기능 비활성화
        self.cap = None
        self.frame_interval = 1.0 / fps  # 프레임 간 시간 간격 (초)
        self.last_frame_time = 0
        self.interview_id = None
        self.metrics_history = []

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

    def start_capture(self, camera_index: int = 0, interview_id: Optional[str] = None) -> bool:
        """
        카메라 캡처 시작

        Args:
            camera_index: 카메라 인덱스 (기본값: 0)
            interview_id: 면접 ID (없으면 현재 시간으로 생성)

        Returns:
            성공 여부
        """
        # 면접 ID 설정
        if interview_id is None:
            self.interview_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.interview_id = interview_id

        # 카메라 열기
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"카메라 {camera_index}를 열 수 없습니다.")
            return False

        # # 카메라 설정
        # width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # # 비디오 저장 설정
        # video_path = os.path.join(self.output_dir, f"{self.interview_id}.mp4")
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # self.video_writer = cv2.VideoWriter(video_path, fourcc, self.target_fps, (width, height))

        # 분석기 초기화
        self.vision_analyzer.reset()
        self.metrics_history = []
        self.last_frame_time = time.time()

        print(f"영상 분석 시작")
        return True

    def process_frame(self) -> Tuple[Optional[np.ndarray], bool]:
        """
        프레임 처리 및 분석

        Returns:
            processed_frame: 처리된 프레임 (None이면 종료)
            is_new_frame: 새 프레임 여부
        """
        if self.cap is None or not self.cap.isOpened():
            return None, False

        # 현재 시간 확인
        current_time = time.time()
        elapsed = current_time - self.last_frame_time

        # 목표 FPS에 맞게 프레임 처리
        if elapsed < self.frame_interval:
            # 아직 다음 프레임을 처리할 시간이 아님
            return None, False

        # 새 프레임 읽기
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None, False

        # 프레임 분석
        processed_frame, metrics = self.vision_analyzer.process_frame(frame)

        # 분석 결과 저장
        self.metrics_history.append(metrics)

        # # 비디오 파일에 저장
        # if self.video_writer is not None:
        #     self.video_writer.write(processed_frame)

        # 타임스탬프 업데이트
        self.last_frame_time = current_time

        return processed_frame, True

    def stop_capture(self) -> Dict[str, Any]:
        """
        캡처 중지 및 리소스 해제

        Returns:
            분석 결과 요약
        """
        # 비디오 캡처 종료
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        # # 비디오 저장 종료
        # if self.video_writer is not None:
        #     self.video_writer.release()
        #     self.video_writer = None

        # 분석 결과 요약
        analysis_summary = self.vision_analyzer.get_analysis_summary()

        # 분석 결과 저장
        summary_path = os.path.join(self.output_dir, f"{self.interview_id}_vision_analysis.json")

        # 여기서 JSON으로 저장하는 코드를 추가할 수 있음
        # import json
        # with open(summary_path, 'w', encoding='utf-8') as f:
        #     json.dump(analysis_summary, f, ensure_ascii=False, indent=2)

        print(f"영상 분석 종료 및 분석 완료: {summary_path}")
        return analysis_summary

    def get_nonverbal_prompt(self) -> str:
        """
        비언어적 요소를 분석한 결과를 GPT 프롬프트로 변환

        Returns:
            GPT 프롬프트 문자열
        """
        # 분석 결과 가져오기
        analysis = self.vision_analyzer.get_analysis_summary()

        # 오류 처리
        if "error" in analysis:
            return "비언어적 요소 분석 중 오류가 발생했습니다."

        # 프롬프트 생성
        prompt = "## 면접자의 비언어적 요소 분석\n\n"

        # 얼굴 감지
        face_rate = analysis["face_detection"]["rate"] * 100
        prompt += f"1. **얼굴 감지**: 면접 시간의 {face_rate:.1f}%동안 얼굴이 감지되었습니다. {analysis['face_detection']['comment']}\n\n"

        # 표정 (웃음)
        smile_rate = analysis["smile"]["rate"] * 100
        prompt += f"2. **표정**: 얼굴이 감지된 시간 중 {smile_rate:.1f}%에서 미소가 감지되었습니다. {analysis['smile']['comment']}\n\n"

        # 자세
        posture_rate = analysis["posture"]["rate"] * 100
        prompt += f"3. **자세**: 면접 시간의 {posture_rate:.1f}%동안 바른 자세를 유지했습니다. {analysis['posture']['comment']}\n\n"

        # 시선 처리
        eye_rate = analysis["eye_contact"]["rate"] * 100
        prompt += f"4. **시선 처리**: 얼굴이 감지된 시간 중 {eye_rate:.1f}%에서 적절한 시선 처리가 관찰되었습니다. {analysis['eye_contact']['comment']}\n\n"

        # 제스처
        gesture_rate = analysis["gesture"]["rate"] * 100
        prompt += f"5. **제스처**: 면접 시간의 {gesture_rate:.1f}%동안 손 제스처가 사용되었습니다. {analysis['gesture']['comment']}\n\n"

        # 눈 깜빡임
        blink_comment = analysis["blink"]["comment"]
        prompt += f"6. **눈 깜빡임**: {blink_comment}\n\n"

        # 종합 점수
        overall_score = analysis["overall_score"]
        prompt += f"7. **종합 평가**: 비언어적 요소 종합 점수는 5점 만점에 {overall_score:.1f}점입니다.\n\n"

        # 점수 해석
        if overall_score >= 4.0:
            prompt += "비언어적 요소가 매우 우수합니다. 자신감 있고 전문적인 인상을 주었습니다."
        elif overall_score >= 3.0:
            prompt += "비언어적 요소가 양호합니다. 일부 개선할 부분이 있지만 전반적으로 좋은 인상을 주었습니다."
        elif overall_score >= 2.0:
            prompt += "비언어적 요소가 보통입니다. 개선이 필요한 부분이 있습니다."
        else:
            prompt += "비언어적 요소가 부족합니다. 면접 상황에서의 비언어적 커뮤니케이션 능력을 향상시킬 필요가 있습니다."

        return prompt