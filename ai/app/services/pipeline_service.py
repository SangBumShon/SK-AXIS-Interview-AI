# # app/services/interview/pipeline_service.py
# import json
# import asyncio
# from app.services.rewrite_service import rewrite_answer
# from app.services.evaluation_service import evaluate_answer
# from app.services.report_service import create_radar_chart, generate_pdf
# import os
#
# async def run_pipeline(
#     input_json: str,
#     chart_path: str = "radar_chart.png",
#     output_pdf: str = "interview_report.pdf"
# ) -> None:
#     # Load data
#     with open(input_json, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#
#     # Group by competency
#     groups: dict[str, list] = {}
#     for item in data:
#         groups.setdefault(item["competency"], []).append(item)
#
#     comp_results: dict[str, dict] = {}
#
#     # Process each competency group
#     for comp, items in groups.items():
#         scores_list: list[int] = []
#         total_reasons: list[str] = []
#         for it in items:
#             rewritten, _ = await rewrite_answer(it["answer_raw"])
#             _, total, _ = await evaluate_answer(comp, it["question"], rewritten)
#             scores_list.append(total)
#             total_reasons.append(f"\"{it['question']}\" → {total}점")
#
#         avg_score = round(sum(scores_list) / len(scores_list)) if scores_list else 0
#         comp_results[comp] = {
#             "avg_score": avg_score,
#             "reasons": "\n".join(total_reasons)
#         }
#
#     # Generate visuals and PDF
#     create_radar_chart(comp_results, chart_path)
#     pdf_time = generate_pdf(comp_results, chart_path, output_pdf)
#     print(f"Report generated in {pdf_time:.2f}s: {output_pdf}")
#
#
# RESULT_DIR = r"D:\result"
# os.makedirs(RESULT_DIR, exist_ok=True)
#
# chart_path = os.path.join(RESULT_DIR, "radar_chart.png")
# output_pdf = os.path.join(RESULT_DIR, "interview_report.pdf")
#
# # Optional entry point for standalone execution
# if __name__ == "__main__":
#     asyncio.run(run_pipeline("ultra_extensive_final_interview_stt_data.json"))
import json
import asyncio
from typing import List
from itertools import groupby
from app.services.rewrite_service import rewrite_answer
from app.services.evaluation_service import evaluate_answer
from app.services.report_service import create_radar_chart, generate_pdf

async def run_pipeline(
    input_json: str,
    chart_path: str = "radar_chart.png",
    output_pdf: str = "interview_report.pdf"
) -> None:
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    await run_pipeline_from_data(data, chart_path, output_pdf)


async def run_pipeline_from_data(
    data: List[dict],
    chart_path: str = "radar_chart.png",
    output_pdf: str = "interview_report.pdf"
) -> None:
    # group 필드를 기준으로 질문군 단위로 묶기
    data.sort(key=lambda x: x["group"])  # groupby는 정렬이 필요함
    grouped = groupby(data, key=lambda x: x["group"])

    comp_results: dict[str, dict] = {}
    competency_scores: dict[str, List[int]] = {}
    competency_reasons: dict[str, List[str]] = {}

    for group_id, items in grouped:
        items = list(items)
        competency = items[0]["competency"]
        combined_question = " / ".join([it["question"] for it in items])
        combined_answer = " ".join([it["answer_raw"] for it in items])

        rewritten, _ = await rewrite_answer(combined_answer)
        _, total_score, _ = await evaluate_answer(competency, combined_question, rewritten)

        competency_scores.setdefault(competency, []).append(total_score)
        competency_reasons.setdefault(competency, []).append(f"[{group_id}] {combined_question} → {total_score}점")

    for comp in competency_scores:
        avg_score = round(sum(competency_scores[comp]) / len(competency_scores[comp]))
        comp_results[comp] = {
            "avg_score": avg_score,
            "reasons": "\n".join(competency_reasons[comp])
        }

    create_radar_chart(comp_results, chart_path)
    generate_pdf(comp_results, chart_path, output_pdf)
    print(f"✅ PDF 리포트 생성 완료: {output_pdf}")
