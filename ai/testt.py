# test_pipeline.py

import asyncio
from app.services.pipeline.graph_pipeline_sample import (
    interview_flow_executor,
    final_report_flow_executor
)
from app.schemas.state import InterviewState

async def main():
    # 1) 초기 상태 생성
    state: InterviewState = {
        "interviewee_id": "person1",
        "audio_path": "./app/temp_recordings/sample.wav",  # 실제 WAV 파일 경로로 변경하세요
        "stt": {"done": False, "segments": []},
        "rewrite": {"done": False, "items": []},
        "evaluation": {"done": False, "results": {}},
        "report": {"pdf": {"generated": False, "path": None}},
        "decision_log": [],
    }

    print("▶ Running interview_flow_executor (STT → Rewrite)...")
    # 수정: .ainvoke() 메서드 사용
    state = await interview_flow_executor.ainvoke(state)
    print("✔ STT and Rewrite complete")
    print("STT segments:", state["stt"]["segments"])
    print("Rewrite items:", state["rewrite"]["items"])

    print("\n▶ Running final_report_flow_executor (Evaluation → PDF)...")
    # 수정: .ainvoke() 메서드 사용
    state = await final_report_flow_executor.ainvoke(state)
    print("✔ Evaluation and PDF generation complete")
    print("PDF Path:", state["report"]["pdf"]["path"])
    print("Decision log:")
    for log in state["decision_log"]:
        print(" ", log)

if __name__ == "__main__":
    asyncio.run(main())
