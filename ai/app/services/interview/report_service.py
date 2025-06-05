# app/services/interview/report_service.py

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF
import os
import platform

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.setup_fonts()

    def setup_fonts(self):
        """한글 폰트 설정"""
        try:
            if platform.system() == "Windows":
                font_paths = [
                    "C:/Windows/Fonts/malgun.ttf",
                    "C:/Windows/Fonts/NanumGothic.ttf",
                    "fonts/NanumGothic-Regular.ttf"
                ]
            elif platform.system() == "Darwin":
                font_paths = [
                    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                    "/Library/Fonts/NanumGothic.ttf",
                    "fonts/NanumGothic-Regular.ttf"
                ]
            else:
                font_paths = [
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                    "fonts/NanumGothic-Regular.ttf"
                ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.add_font("Korean", "", font_path, uni=True)
                    return
            print("⚠️  한글 폰트를 찾지 못했습니다. 기본 폰트 사용 (한글 깨질 수 있음)")
        except Exception as e:
            print(f"❌ 폰트 설정 오류: {e}")

    def header(self):
        try:
            self.set_font("Korean", "", 16)
        except:
            self.set_font("Arial", "B", 16)
        self.cell(0, 10, "면접 종합 평가 리포트", ln=True, align="C")
        self.ln(5)

    def add_meta(self, interview_date: str, applicant_name: str):
        try:
            self.set_font("Korean", "", 12)
        except:
            self.set_font("Arial", "B", 12)
        # 왼쪽: 면접일시, 오른쪽: 지원자명
        self.cell(0, 8, f"면접일시: {interview_date}", ln=False, align="L")
        self.cell(0, 8, f"지원자: {applicant_name}", ln=True, align="R")
        self.ln(3)

    def add_comp(self, comp: str, score: int, reason: str):
        try:
            self.set_font("Korean", "", 14)
        except:
            self.set_font("Arial", "B", 14)
        self.cell(0, 8, f"{comp} 역량 종합 점수: {score}점", ln=True)

        try:
            self.set_font("Korean", "", 11)
        except:
            self.set_font("Arial", "", 11)
        self.multi_cell(0, 7, f"평가 사유:\n{reason}")
        self.ln(3)

    def add_block_summary(self, question: str, summary: str):
        try:
            self.set_font("Korean", "", 12)
        except:
            self.set_font("Arial", "", 12)
        self.cell(0, 7, f"[질문] {question}", ln=True)
        self.multi_cell(0, 7, f"[요약된 평가 사유]\n{summary}")
        self.ln(2)

    def add_chart(self, img_path: str):
        if os.path.exists(img_path):
            self.image(img_path, x=50, w=110)
        else:
            self.cell(0, 10, "차트 파일을 찾을 수 없습니다.", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font("Korean", "", 8)
        except:
            self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def setup_matplotlib_korean():
    try:
        if platform.system() == "Windows":
            font_candidates = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
        elif platform.system() == "Darwin":
            font_candidates = ['AppleGothic', 'NanumGothic', 'Arial Unicode MS']
        else:
            font_candidates = ['NanumGothic', 'DejaVu Sans']

        available_fonts = [f.name for f in fm.fontManager.ttflist]
        for font_name in font_candidates:
            if font_name in available_fonts:
                plt.rcParams['font.family'] = font_name
                break
        else:
            print("⚠️  Matplotlib 한글 폰트를 찾지 못했습니다.")

        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        print(f"❌ Matplotlib 폰트 설정 오류: {e}")


def create_radar_chart(
        comp_results: dict[str, dict],
        chart_path: str
) -> None:
    setup_matplotlib_korean()

    labels = list(comp_results.keys())
    values = [comp_results[c]["avg_score"] for c in labels]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, marker='o', linewidth=2, color='#1f77b4')
    ax.fill(angles, values, alpha=0.25, color='#1f77b4')
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.grid(True)
    plt.title("역량별 평가 점수", size=16, pad=20)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def generate_pdf(
        comp_results: dict[str, dict],
        chart_path: str,
        output_path: str,
        applicant_name: str,
        interview_date: str,
        question_blocks: list[dict]
) -> float:
    start = time.perf_counter()

    create_radar_chart(comp_results, chart_path)

    pdf = PDFReport()
    pdf.add_page()

    # 메타 정보 출력
    pdf.add_meta(interview_date, applicant_name)

    # 역량별 평가
    for comp, res in comp_results.items():
        pdf.add_comp(comp, res["avg_score"], res["reasons"])

    # 질문별 평가 요약
    for qb in question_blocks:
        pdf.add_block_summary(qb["question"], qb["summary"])

    # 차트 추가
    pdf.add_chart(chart_path)

    # PDF 생성 시간
    generation_time = time.perf_counter() - start
    try:
        pdf.set_font("Korean", "", 10)
    except:
        pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"PDF 생성 시간: {generation_time:.2f}초", ln=True, align="R")

    pdf.output(output_path)
    return generation_time
