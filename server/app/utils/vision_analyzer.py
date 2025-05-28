import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Any

class VisionAnalyzer:
    """
    면접자의 비언어적 요소를 분석하는 클래스
    - 자세 분석 (Pose)
    - 표정 분석 (Face Mesh)
    - 시선 처리 (Face Mesh)
    - 제스처 분석 (Hands)
    """
    
    def __init__(self):
        # MediaPipe 솔루션 초기화
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # 얼굴 감지
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 포즈 감지
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 손 감지
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 분석 결과 저장 변수
        self.frame_count = 0
        self.smile_count = 0
        self.good_posture_count = 0
        self.eye_contact_count = 0
        self.gesture_count = 0
        self.blink_count = 0
        self.face_detected_count = 0
        
        # 눈 깜빡임 감지를 위한 변수
        self.left_eye_closed = False
        self.right_eye_closed = False
        self.blink_threshold = 0.2  # 눈 깜빡임 감지 임계값
        
        # 얼굴 메시 인덱스 정의
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.MOUTH_INDICES = [61, 291, 0, 17, 61]  # 입 주변 랜드마크
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        프레임을 처리하고 분석 결과를 반환합니다.
        
        Args:
            frame: 분석할 비디오 프레임
            
        Returns:
            annotated_frame: 분석 결과가 표시된 프레임
            metrics: 분석된 메트릭 정보
        """
        self.frame_count += 1
        
        # 이미지 처리를 위해 BGR에서 RGB로 변환
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 분석 결과
        metrics = {
            "face_detected": False,
            "smile_detected": False,
            "good_posture": False,
            "eye_contact": False,
            "gesture_detected": False,
            "blink_detected": False
        }
        
        # 얼굴 메시 분석
        face_results = self.face_mesh.process(image_rgb)
        if face_results.multi_face_landmarks:
            metrics["face_detected"] = True
            self.face_detected_count += 1
            
            for face_landmarks in face_results.multi_face_landmarks:
                # 얼굴 메시 그리기
                self.mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style()
                )
                
                # 표정 분석 (웃음 감지)
                smile_score = self._analyze_smile(face_landmarks)
                if smile_score > 0.5:  # 웃음 임계값
                    metrics["smile_detected"] = True
                    self.smile_count += 1
                
                # 시선 처리 분석
                eye_contact_score = self._analyze_eye_contact(face_landmarks)
                if eye_contact_score > 0.7:  # 시선 처리 임계값
                    metrics["eye_contact"] = True
                    self.eye_contact_count += 1
                
                # 눈 깜빡임 감지
                blink_detected = self._detect_blink(face_landmarks)
                if blink_detected:
                    metrics["blink_detected"] = True
                    self.blink_count += 1
        
        # 포즈 분석
        pose_results = self.pose.process(image_rgb)
        if pose_results.pose_landmarks:
            # 포즈 랜드마크 그리기
            self.mp_drawing.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # 자세 분석
            posture_score = self._analyze_posture(pose_results.pose_landmarks)
            if posture_score > 0.7:  # 좋은 자세 임계값
                metrics["good_posture"] = True
                self.good_posture_count += 1
        
        # 손 분석
        hands_results = self.hands.process(image_rgb)
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                # 손 랜드마크 그리기
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    connection_drawing_spec=self.mp_drawing_styles.get_default_hand_connections_style()
                )
            
            # 제스처 분석
            gesture_detected = self._analyze_gesture(hands_results.multi_hand_landmarks)
            if gesture_detected:
                metrics["gesture_detected"] = True
                self.gesture_count += 1
        
        # 분석 결과 텍스트 추가
        self._add_metrics_text(frame, metrics)
        
        return frame, metrics
    
    def _analyze_smile(self, face_landmarks) -> float:
        """웃음 감지 분석"""
        # 입 주변 랜드마크 추출
        mouth_points = [face_landmarks.landmark[i] for i in self.MOUTH_INDICES]
        
        # 입의 가로 세로 비율 계산 (웃을 때 입이 가로로 넓어짐)
        x_coords = [point.x for point in mouth_points]
        y_coords = [point.y for point in mouth_points]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        
        # 입의 가로/세로 비율이 클수록 웃고 있을 가능성이 높음
        if height > 0:
            ratio = width / height
            # 정규화된 웃음 점수 반환
            return min(1.0, max(0.0, (ratio - 1.5) / 2.0))
        return 0.0
    
    def _analyze_eye_contact(self, face_landmarks) -> float:
        """시선 처리 분석"""
        # 얼굴 방향 추정
        nose_tip = face_landmarks.landmark[4]
        left_eye = face_landmarks.landmark[self.LEFT_EYE_INDICES[0]]
        right_eye = face_landmarks.landmark[self.RIGHT_EYE_INDICES[0]]
        
        # 얼굴이 정면을 향하고 있는지 확인
        eye_distance = abs(left_eye.x - right_eye.x)
        face_center_x = (left_eye.x + right_eye.x) / 2
        
        # 얼굴이 중앙에 있고 정면을 향하고 있을 때 시선 처리가 좋다고 판단
        center_score = 1.0 - min(1.0, abs(face_center_x - 0.5) * 2)
        orientation_score = min(1.0, eye_distance * 5)  # 눈 사이 거리가 클수록 정면을 향함
        
        return (center_score + orientation_score) / 2
    
    def _analyze_posture(self, pose_landmarks) -> float:
        """자세 분석"""
        # 어깨 랜드마크
        left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # 어깨의 수평 정도 확인 (좋은 자세는 어깨가 수평)
        shoulder_slope = abs(left_shoulder.y - right_shoulder.y)
        horizontal_score = 1.0 - min(1.0, shoulder_slope * 10)
        
        # 상체의 기울기 확인
        nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
        mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
        
        # 코와 어깨 중앙의 수직 정렬 확인
        vertical_alignment = abs(nose.x - mid_shoulder_x)
        vertical_score = 1.0 - min(1.0, vertical_alignment * 5)
        
        # 종합 자세 점수
        return (horizontal_score + vertical_score) / 2
    
    def _analyze_gesture(self, multi_hand_landmarks) -> bool:
        """제스처 분석"""
        # 간단한 제스처 감지 (손이 감지되면 제스처로 간주)
        # 실제 구현에서는 더 복잡한 제스처 패턴을 분석할 수 있음
        return len(multi_hand_landmarks) > 0
    
    def _detect_blink(self, face_landmarks) -> bool:
        """눈 깜빡임 감지"""
        # 왼쪽 눈 감지
        left_eye_points = [face_landmarks.landmark[i] for i in self.LEFT_EYE_INDICES]
        left_eye_height = self._calculate_eye_height(left_eye_points)
        
        # 오른쪽 눈 감지
        right_eye_points = [face_landmarks.landmark[i] for i in self.RIGHT_EYE_INDICES]
        right_eye_height = self._calculate_eye_height(right_eye_points)
        
        # 눈 감김 상태 업데이트
        prev_left_closed = self.left_eye_closed
        prev_right_closed = self.right_eye_closed
        
        self.left_eye_closed = left_eye_height < self.blink_threshold
        self.right_eye_closed = right_eye_height < self.blink_threshold
        
        # 눈 깜빡임 감지 (열린 상태에서 닫힌 상태로 전환)
        left_blink = not prev_left_closed and self.left_eye_closed
        right_blink = not prev_right_closed and self.right_eye_closed
        
        return left_blink or right_blink
    
    def _calculate_eye_height(self, eye_points) -> float:
        """눈의 세로/가로 비율 계산"""
        # 눈의 가로, 세로 길이 계산
        x_coords = [point.x for point in eye_points]
        y_coords = [point.y for point in eye_points]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        
        if width > 0:
            return height / width
        return 0
    
    def _add_metrics_text(self, frame, metrics):
        """분석 결과 텍스트를 프레임에 추가"""
        h, w, _ = frame.shape
        y_offset = 30
        
        # 얼굴 감지 상태
        cv2.putText(frame, f"얼굴 감지: {'O' if metrics['face_detected'] else 'X'}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if metrics['face_detected'] else (0, 0, 255), 2)
        y_offset += 30
        
        # 웃음 감지 상태
        cv2.putText(frame, f"웃음: {'O' if metrics['smile_detected'] else 'X'}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if metrics['smile_detected'] else (0, 0, 255), 2)
        y_offset += 30
        
        # 자세 상태
        cv2.putText(frame, f"자세: {'좋음' if metrics['good_posture'] else '개선 필요'}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if metrics['good_posture'] else (0, 0, 255), 2)
        y_offset += 30
        
        # 시선 처리 상태
        cv2.putText(frame, f"시선 처리: {'좋음' if metrics['eye_contact'] else '개선 필요'}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if metrics['eye_contact'] else (0, 0, 255), 2)
        y_offset += 30
        
        # 제스처 감지 상태
        cv2.putText(frame, f"제스처: {'O' if metrics['gesture_detected'] else 'X'}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if metrics['gesture_detected'] else (0, 0, 255), 2)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """현재 프레임의 분석 메트릭 반환"""
        # 프레임이 없는 경우 기본값 반환
        if self.frame_count == 0:
            return {
                "face_detected": False,
                "smile_detected": False,
                "good_posture": False,
                "eye_contact": False,
                "gesture_detected": False,
                "blink_detected": False,
                "error": "분석된 프레임이 없습니다."
            }
        
        # 현재까지의 분석 비율 계산
        face_rate = self.face_detected_count / self.frame_count if self.frame_count > 0 else 0
        smile_rate = self.smile_count / self.face_detected_count if self.face_detected_count > 0 else 0
        posture_rate = self.good_posture_count / self.frame_count if self.frame_count > 0 else 0
        eye_rate = self.eye_contact_count / self.face_detected_count if self.face_detected_count > 0 else 0
        gesture_rate = self.gesture_count / self.frame_count if self.frame_count > 0 else 0
        
        return {
            "face_detected": face_rate > 0.5,
            "smile_detected": smile_rate > 0.3,
            "good_posture": posture_rate > 0.5,
            "eye_contact": eye_rate > 0.5,
            "gesture_detected": gesture_rate > 0.2,
            "face_rate": face_rate,
            "smile_rate": smile_rate,
            "posture_rate": posture_rate,
            "eye_rate": eye_rate,
            "gesture_rate": gesture_rate,
            "blink_count": self.blink_count
        }
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """분석 결과 요약"""
        if self.frame_count == 0:
            return {
                "error": "No frames processed"
            }
        
        # 각 지표의 비율 계산
        face_detection_rate = self.face_detected_count / self.frame_count
        smile_rate = self.smile_count / max(1, self.face_detected_count)
        good_posture_rate = self.good_posture_count / self.frame_count
        eye_contact_rate = self.eye_contact_count / max(1, self.face_detected_count)
        gesture_rate = self.gesture_count / self.frame_count
        blink_rate = self.blink_count / max(1, self.face_detected_count * 0.1)  # 정규화된 깜빡임 비율
        
        # 종합 점수 계산 (5점 만점)
        face_score = min(5, face_detection_rate * 5)
        smile_score = min(5, smile_rate * 5)
        posture_score = min(5, good_posture_rate * 5)
        eye_contact_score = min(5, eye_contact_rate * 5)
        gesture_score = min(5, gesture_rate * 5)
        blink_score = min(5, max(0, 2.5 - abs(blink_rate - 0.5) * 5))  # 적절한 깜빡임 비율에 대한 점수
        
        # 종합 분석 결과
        return {
            "total_frames": self.frame_count,
            "face_detection": {
                "rate": face_detection_rate,
                "score": face_score,
                "comment": self._get_face_detection_comment(face_detection_rate)
            },
            "smile": {
                "rate": smile_rate,
                "score": smile_score,
                "comment": self._get_smile_comment(smile_rate)
            },
            "posture": {
                "rate": good_posture_rate,
                "score": posture_score,
                "comment": self._get_posture_comment(good_posture_rate)
            },
            "eye_contact": {
                "rate": eye_contact_rate,
                "score": eye_contact_score,
                "comment": self._get_eye_contact_comment(eye_contact_rate)
            },
            "gesture": {
                "rate": gesture_rate,
                "score": gesture_score,
                "comment": self._get_gesture_comment(gesture_rate)
            },
            "blink": {
                "rate": blink_rate,
                "score": blink_score,
                "comment": self._get_blink_comment(blink_rate)
            },
            "overall_score": (face_score + smile_score + posture_score + eye_contact_score + gesture_score + blink_score) / 6
        }
    
    def _get_face_detection_comment(self, rate):
        if rate > 0.95:
            return "면접 내내 얼굴이 잘 보였습니다."
        elif rate > 0.8:
            return "대체로 얼굴이 잘 보였으나, 간혹 카메라 밖으로 벗어났습니다."
        elif rate > 0.6:
            return "얼굴이 자주 카메라 밖으로 벗어났습니다. 카메라를 향해 앉는 것이 좋습니다."
        else:
            return "얼굴이 카메라에 제대로 잡히지 않았습니다. 카메라 위치와 앉는 자세를 조정하세요."
    
    def _get_smile_comment(self, rate):
        if rate > 0.3:
            return "적절한 미소로 친근한 인상을 주었습니다."
        elif rate > 0.1:
            return "간혹 미소를 지었으나, 더 자주 웃으면 좋을 것 같습니다."
        else:
            return "표정이 다소 경직되어 보입니다. 자연스러운 미소가 필요합니다."
    
    def _get_posture_comment(self, rate):
        if rate > 0.9:
            return "매우 바른 자세로 면접에 임했습니다."
        elif rate > 0.7:
            return "대체로 바른 자세였으나, 가끔 자세가 흐트러졌습니다."
        elif rate > 0.5:
            return "자세가 자주 흐트러졌습니다. 더 바른 자세로 앉는 것이 좋습니다."
        else:
            return "자세가 좋지 않았습니다. 허리를 펴고 어깨를 바로 하는 연습이 필요합니다."
    
    def _get_eye_contact_comment(self, rate):
        if rate > 0.8:
            return "훌륭한 시선 처리로 자신감 있는 모습을 보여주었습니다."
        elif rate > 0.6:
            return "대체로 시선 처리가 좋았으나, 가끔 시선이 흐트러졌습니다."
        elif rate > 0.4:
            return "시선 처리가 다소 부족했습니다. 카메라를 더 자주 응시하는 것이 좋습니다."
        else:
            return "시선 처리가 매우 부족했습니다. 면접관(카메라)을 응시하는 연습이 필요합니다."
    
    def _get_gesture_comment(self, rate):
        if rate > 0.3:
            return "적절한 제스처로 설명에 생동감을 더했습니다."
        elif rate > 0.1:
            return "간혹 제스처를 사용했으나, 더 활용하면 좋을 것 같습니다."
        else:
            return "제스처가 거의 없었습니다. 적절한 손동작으로 설명에 생동감을 더하세요."
    
    def _get_blink_comment(self, rate):
        if 0.3 < rate < 0.7:
            return "자연스러운 눈 깜빡임을 보였습니다."
        elif rate > 0.7:
            return "눈 깜빡임이 다소 잦았습니다. 긴장했을 수 있습니다."
        else:
            return "눈 깜빡임이 적었습니다. 다소 경직된 모습이었을 수 있습니다."
    
    def reset(self):
        """분석 결과 초기화"""
        self.frame_count = 0
        self.smile_count = 0
        self.good_posture_count = 0
        self.eye_contact_count = 0
        self.gesture_count = 0
        self.blink_count = 0
        self.face_detected_count = 0
