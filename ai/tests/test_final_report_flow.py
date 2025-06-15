import sys
import os
import json
import asyncio
from datetime import datetime

# 1. sys.path 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. 파이프라인 로딩
from ai.app.services.pipeline.graph_pipeline import final_report_flow_executor

# 3. JSON 로딩 함수 (rewrite.items 구조 지원)
def load_rewrite_items(file_name: str) -> list:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(base_dir, 'test_data', file_name)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        try:
            return data["rewrite"]["items"]
        except KeyError:
            raise ValueError("❌ JSON 파일에 'rewrite.items' 키가 없습니다.")

# 4. State 구성
def build_state_from_rewrite_items(items: list) -> dict:
    return {
        "interviewee_id": 12345,
        "rewrite": {
            "done": True,
            "items": items
        },
        "questions": [
            "지원 동기는 무엇인가요?",
            "협업 경험에 대해 설명해주세요?",
            "문제를 해결한 경험은?",
            "사용할 수 있는 기술은?",
            "입사 후 포부는?"
        ],
        "evaluation": {"results": {}},
        "nonverbal_counts": {
            "posture": {
                "leg_spread": 2,
                "leg_shake": 1,
                "head_down": 0
            },
            "facial_expression": {
                "smile": 3,
                "neutral": 2,
                "embarrassed": 0,
                "tearful": 0,
                "frown": 1
            },
            "gaze": 0,
            "gesture": 0
        }
    }

# 5. 비동기 실행
async def run_test():
    items = load_rewrite_items("rewrite_items_full.json")
    state = build_state_from_rewrite_items(items)
    result = await final_report_flow_executor.ainvoke(state)
    
    print("✅ PDF 생성 결과:", result.get("report", {}).get("pdf"))
    print("\n=== decision_log ===")
    for log in result.get("decision_log", []):
        print(log)

# 6. 메인 실행
if __name__ == "__main__":
    asyncio.run(run_test())
