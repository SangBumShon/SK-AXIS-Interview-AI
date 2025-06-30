# app/services/interview/report_service.py

import os
from fpdf import FPDF
from datetime import datetime
import json

def generate_json_pdf(
    json_data: dict,
    output_path: str,
    applicant_id: str = None,
    interview_datetime: str = None,
    report_title: str = None
) -> float:
    """
    전달받은 json_data를 PDF에 그대로(중괄호 포함, key/value 모두) 텍스트로 출력합니다.
    """
    from time import perf_counter
    start = perf_counter()

    # PDF 생성
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 폰트 설정 (한글 지원)
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'NanumGothic-Regular.ttf'))
    if os.path.exists(font_path):
        pdf.add_font("Korean", "", font_path, uni=True)
        pdf.set_font("Korean", size=12)
    else:
        pdf.set_font("Arial", size=12)

    # 제목
    if report_title:
        pdf.set_font_size(16)
        pdf.cell(0, 10, report_title, ln=True, align="C")
        pdf.ln(5)
        pdf.set_font_size(12)
    # 지원자 ID, 면접 일시
    if applicant_id:
        pdf.cell(0, 10, f"지원자 ID: {applicant_id}", ln=True)
    if interview_datetime:
        pdf.cell(0, 10, f"면접 일시: {interview_datetime}", ln=True)
    pdf.ln(5)

    # JSON 전체를 pretty print로 출력
    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
    pdf.set_font_size(10)
    pdf.multi_cell(0, 7, json_str)

    elapsed = perf_counter() - start
    pdf.set_font_size(8)
    pdf.cell(0, 10, f"PDF 생성 시간: {elapsed:.2f}초", ln=True, align="R")
    pdf.output(output_path)
    return elapsed
