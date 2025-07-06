# Interview Service 모듈 가이드 요약

## stt_service.py
- 음성 파일을 Whisper로 STT 처리하여 텍스트 세그먼트 생성

## rewrite_service.py
- STT 텍스트를 GPT를 통해 문법/의미 보존 기반으로 정제

## evaluation_service.py
- 정제된 답변을 바탕으로 키워드 기반 평가를 수행 (SUPEX/VWBE/4P/기술역량 등)

## graph_pipeline_sample.py
- LangGraph 기반 파이프라인 정의 (STT→리라이팅→평가→리포트 생성까지 전체 흐름 정의)

## interview.py
- 상태 기반 인터뷰 흐름 정의 또는 엔트리 포인트 (예: test_runner 등에서 활용됨)

## nonverbal_service.py
- 비언어적 요소 처리 모듈 (예: 표정, 자세 등 평가)

