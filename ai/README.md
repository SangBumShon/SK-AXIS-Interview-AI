# 면접 평가 시스템 - 비언어적 요소 분석 모듈

이 프로젝트는 면접자의 실시간 영상을 분석하여 비언어적 요소(자세, 표정, 시선처리, 제스처 등)를 평가하는 시스템입니다.

## 기능

- 실시간 영상 캡처 및 저장 (10FPS)
- MediaPipe를 이용한 비언어적 요소 분석:
  - 얼굴 감지 및 표정 분석
  - 자세 분석
  - 시선 처리 분석
  - 제스처 분석
  - 눈 깜빡임 감지
- 분석 결과를 바탕으로 GPT 프롬프트 생성
- FastAPI를 이용한 REST API 및 WebSocket 제공

## 설치 방법

1. 필요한 패키지 설치:

```bash
# 기본 패키지 설치
pip install -r requirements.txt

# OpenCV 및 MediaPipe 설치
pip install opencv-python==4.9.0.80 mediapipe==0.10.5
```

## 프로젝트 구조

```
ai/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI 메인 애플리케이션
│   ├── video_processor.py     # 비디오 처리 모듈
│   └── utils/
│       ├── __init__.py
│       └── vision_analyzer.py # 비언어적 요소 분석 모듈
├── output/                    # 출력 파일 저장 디렉토리
└── requirements.txt           # 의존성 패키지
```

## API 엔드포인트

- `POST /interview/start`: 면접 세션 시작
- `POST /interview/{interview_id}/stop`: 면접 세션 종료 및 분석 결과 반환
- `GET /interview/{interview_id}/status`: 면접 세션 상태 확인
- `GET /interviews`: 모든 면접 세션 목록 조회
- `DELETE /interview/{interview_id}`: 면접 세션 삭제
- `WebSocket /ws/video/{interview_id}`: 실시간 비디오 스트리밍

## 사용 방법

1. 서버 실행:

```bash
cd ai
python -m app.main
```

2. API 호출 예시:

```bash
# 면접 시작 (응답으로 받은 interview_id를 메모해두세요)
curl -X POST "http://localhost:8000/interview/start"

# 예시: {"interview_id":"20250527_174848","status":"started","message":"면접 세션이 시작되었습니다. ID: 20250527_174848"}

# 면접 종료 (위에서 받은 실제 interview_id를 사용해야 합니다)
curl -X POST "http://localhost:8000/interview/20250527_174848/stop"
```

## 비언어적 요소 분석 결과

분석 결과는 다음 항목을 포함합니다:

1. 얼굴 감지율
2. 미소 감지율
3. 바른 자세 유지율
4. 적절한 시선 처리율
5. 제스처 사용률
6. 눈 깜빡임 패턴
7. 종합 평가 점수 (5점 만점)

각 항목에 대한 점수와 코멘트가 제공됩니다.

