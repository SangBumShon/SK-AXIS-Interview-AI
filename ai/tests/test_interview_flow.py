from app.services.pipeline.graph_pipeline_sample import interview_flow_executor

dummy_state = {
    "interviewee_id": "person1",
    "audio_path": "./temp_recordings/sample.wav",  # 실제 존재하는 wav 파일 경로
    "stt": {"done": False, "segments": []},
    "rewrite": {"done": False, "items": []},
    "decision_log": []
}

async def run_interview_test():
    result = await interview_flow_executor.invoke(dummy_state)
    print("🗒️ 결과 요약:")
    for item in result.get("rewrite", {}).get("items", []):
        print("- 원본:", item["raw"])
        print("- 리라이팅:", item["rewritten"])
        print("- 평가 결과:", item.get("ok"), item.get("judge_notes"))
    print("✅ 전체 decision_log:", result.get("decision_log", []))

if __name__ == "__main__":
    asyncio.run(run_interview_test())
