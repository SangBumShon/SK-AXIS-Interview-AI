# app/services/interview/report_service.py
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF
import os
import platform
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self, interviewee_id: str, interview_time: str):
        super().__init__()
        self.interviewee_id = interviewee_id
        self.interview_time = interview_time
        self.setup_fonts()

    def setup_fonts(self):
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
                    print(f"✅ 폰트 로드 성공: {font_path}")
                    return

            print("⚠️  한글 폰트를 찾지 못했습니다. 기본 폰트 사용 (한글 깨질 수 있음)")

        except Exception as e:
            print(f"❌ 폰트 설정 오류: {e}")

    def header(self):
        try:
            self.set_font("Korean", "", 12)
        except:
            self.set_font("Arial", "", 12)
        self.cell(0, 10, f"지원자 ID: {self.interviewee_id}", ln=False, align="L")
        self.cell(0, 10, f"면접 일시: {self.interview_time}", ln=True, align="R")
        self.ln(5)
        try:
            self.set_font("Korean", "", 16)
        except:
            self.set_font("Arial", "B", 16)
        self.cell(0, 10, "면접 종합 평가 리포트", ln=True, align="C")
        self.ln(5)

    def add_qa_blocks(self, qa_text: str):
        try:
            self.set_font("Korean", "", 12)
        except:
            self.set_font("Arial", "", 12)
        self.cell(0, 10, "질문-답변 정리", ln=True)
        self.ln(3)
        self.set_font("Korean", "", 10)
        self.multi_cell(0, 7, qa_text)
        self.ln(5)

    def add_keyword(self, keyword: str, score: int, reason: str):
        try:
            self.set_font("Korean", "", 14)
        except:
            self.set_font("Arial", "B", 14)
        self.cell(0, 8, f"{keyword} 종합 점수: {score}점 / 15점", ln=True)
        try:
            self.set_font("Korean", "", 11)
        except:
            self.set_font("Arial", "", 11)
        self.multi_cell(0, 7, f"평가 사유:\n{reason}")
        self.ln(3)

    def add_chart(self, img_path: str):
        if os.path.exists(img_path):
            self.image(img_path, x=50, w=110)
        else:
            self.cell(0, 10, "차트 파일을 찾을 수 없습니다.", ln=True, align="C")
        self.ln(5)

    def add_total_score(self, score: int):
        try:
            self.set_font("Korean", "", 13)
        except:
            self.set_font("Arial", "B", 13)
        self.cell(0, 10, f"총합 점수 (150점 만점 기준): {score}점", ln=True)
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
                print(f"✅ Matplotlib 한글 폰트 설정: {font_name}")
                break
        else:
            print("⚠️  Matplotlib 한글 폰트를 찾지 못했습니다.")

        plt.rcParams['axes.unicode_minus'] = False

    except Exception as e:
        print(f"❌ Matplotlib 폰트 설정 오류: {e}")


def create_radar_chart(
        keyword_results: dict[str, dict],
        chart_path: str
) -> None:
    setup_matplotlib_korean()
    labels = list(keyword_results.keys())
    values = [keyword_results[k]["score"] for k in labels]  # 15점 기준
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, marker='o', linewidth=2, color='#1f77b4')
    ax.fill(angles, values, alpha=0.25, color='#1f77b4')
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 15)
    ax.set_yticks([3, 6, 9, 12, 15])
    ax.grid(True)
    plt.title("키워드별 평가 점수", size=16, pad=20)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ 차트 저장 완료: {chart_path}")


def generate_pdf(
        keyword_results: dict[str, dict],
        chart_path: str, output_path: str,
        interviewee_id: str,
        qa_blocks_text: str,
        total_score: int
) -> float:
    start = time.perf_counter()
    try:
        # 레이더 차트 생성 및 PDF 작성
        create_radar_chart(keyword_results, chart_path)
        interview_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf = PDFReport(interviewee_id=interviewee_id, interview_time=interview_time)
        pdf.add_page()
        
        # 답변 텍스트만 추가
        if qa_blocks_text:
            pdf.add_qa_blocks(qa_blocks_text)
        pdf.add_page()
        for keyword, res in keyword_results.items():
            pdf.add_keyword(keyword, res["score"], res.get("reasons", ""))
        pdf.add_chart(chart_path)
        pdf.add_total_score(total_score)
        generation_time = time.perf_counter() - start
        pdf.set_font("Korean", "", 10)
        pdf.cell(0, 10, f"PDF 생성 시간: {generation_time:.2f}초", ln=True, align="R")
        pdf.output(output_path)
        print(f"✅ PDF 생성 완료: {output_path}")
        return generation_time

    except Exception as e:
        print(f"❌ PDF 생성 오류: {e}")
        raise
