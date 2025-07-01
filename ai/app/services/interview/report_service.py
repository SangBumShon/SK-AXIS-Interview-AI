# app/services/interview/report_service.py

import time
import os
import platform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF
from datetime import datetime


def build_answer_blocks_text(answers: list[str]) -> str:
    """
    answers 리스트만 받아서
    A1. …
    A2. …
    형태의 멀티라인 문자열로 반환합니다.
    """
    lines: list[str] = []
    for i, a in enumerate(answers, start=1):
        lines.append(f"A{i}. {a}")
        lines.append("")   # 블록 간 여백
    return "\n".join(lines)


class PDFReport(FPDF):
    def __init__(self, interviewee_id: str, interview_time: str):
        """
        PDFReport 생성자: 지원자 ID와 면접 일시를 보관하고,
        한글 폰트를 설정합니다.
        """
        super().__init__()
        self.interviewee_id = interviewee_id
        self.interview_time = interview_time
        self.setup_fonts()

    def setup_fonts(self):
        """
        프로젝트 내 한글 폰트를 등록합니다.
        """
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'NanumGothic-Regular.ttf'))
        if os.path.exists(font_path):
            self.add_font("Korean", "", font_path, uni=True) # 일반 스타일
            self.add_font("Korean", "B", font_path, uni=True) # 굵은 스타일
            self.set_font("Korean", "", 12) # 기본 폰트로 설정
        else:
            print(f"⚠️ 한글 폰트 파일을 찾을 수 없습니다: {font_path}")
            # 폰트 로드 실패 시에도 진행은 가능하도록 Arial 폰트를 사용하지만, 이 경우에는 한글이 깨질 수 있음
            self.set_font("Arial", "", 12)

    def header(self):
        """
        모든 페이지 상단에 지원자 ID, 면접 일시, 리포트 타이틀을 출력합니다.
        """
        self.set_font("Korean", "", 12)
        self.cell(0, 10, f"지원자 ID: {self.interviewee_id}", ln=False, align="L")
        self.cell(0, 10, f"면접 일시: {self.interview_time}", ln=True, align="R")
        self.ln(5)
        self.set_font("Korean", "B", 16)
        self.cell(0, 10, "면접 종합 평가 리포트", ln=True, align="C")
        self.ln(5)

    def footer(self):
        """
        모든 페이지 하단에 페이지 번호를 센터 정렬로 출력합니다.
        """
        self.set_y(-15)
        self.set_font("Korean", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_chart(self, img_path: str):
        """
        레이더 차트 PNG를 중앙에 삽입합니다.
        """
        if os.path.exists(img_path):
            self.image(img_path, x=(self.w - 110) / 2, w=110)
        else:
            self.cell(0, 10, "차트 파일을 찾을 수 없습니다.", ln=True, align="C")
        self.ln(5)

    def add_area_scores(self, area_scores: dict[str, int], weights: dict[str, str]):
        """
        레이더 차트 옆에 3개 영역별 100점 스케일 점수와 가중치를 출력합니다.
        예) {"언어적 요소": 82}, {"언어적 요소": "45%"}
        """
        # 차트 오른쪽 정렬용 탭
        self.cell(60)
        self.set_font("Korean", "B", 11)
        self.cell(0, 8, "영역별 점수 (100점 만점 기준)", ln=True)
        for area, score in area_scores.items():
            self.cell(60)
            line = f"{area} ({weights[area]}): {score}/100"
            self.set_font("Korean", "", 11)
            self.cell(0, 7, line, ln=True)
        self.ln(5)

    def add_answer_blocks(self, answer_text: str):
        """
        답변만 블록—제목 + 본문을 출력합니다.
        """
        self.set_font("Korean", "B", 12)
        self.cell(0, 10, "답변만 보기", ln=True)
        self.ln(3)
        self.set_font("Korean", "", 10)
        self.multi_cell(0, 7, answer_text)
        self.ln(5)

    def add_score_table(self, keyword_results: dict[str, dict]):
        """
        키워드별 점수를 표 형태로 출력합니다.
        """
        self.set_font("Korean", "B", 12)
        col_count = len(keyword_results)
        page_width = self.w - 2 * self.l_margin
        col_width = page_width / (col_count + 1)

        # 헤더 행
        self.cell(col_width, 10, "키워드", border=1, align="C")
        for kw in keyword_results:
            self.cell(col_width, 10, kw, border=1, align="C")
        self.ln()

        # 점수 행
        self.set_font("Korean", "", 12)
        self.cell(col_width, 10, "점수", border=1, align="C")
        for res in keyword_results.values():
            self.cell(col_width, 10, str(res["score"]), border=1, align="C")
        self.ln(15)

    def add_reasons(self, keyword_results: dict[str, dict]):
        """
        키워드별 평가 사유를 출력합니다.
        """
        self.set_font("Korean", "B", 12)
        self.cell(0, 10, "키워드별 평가 사유", ln=True)
        self.ln(2)
        for kw, res in keyword_results.items():
            self.set_font("Korean", "B", 11)
            self.cell(0, 8, f"- {kw}", ln=True)
            self.set_font("Korean", "", 11)
            self.multi_cell(0, 7, res.get("reasons", ""))
            self.ln(2)

    def add_total_score(self, score: int):
        """
        총합 점수 (100점 만점 기준)를 출력합니다.
        """
        self.set_font("Korean", "B", 13)
        self.cell(0, 10, f"총합 점수 (100점 만점 기준): {score}점", ln=True)
        self.ln(5)


def setup_matplotlib_korean():
    """
    Matplotlib에서 한글을 출력할 수 있도록 폰트를 설정합니다.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        if platform.system() == "Windows":
            candidates = ['Malgun Gothic', 'NanumGothic']
        elif platform.system() == "Darwin":
            candidates = ['AppleGothic', 'NanumGothic']
        else:
            candidates = ['NanumGothic', 'DejaVu Sans']
        for f in fm.fontManager.ttflist:
            if f.name in candidates:
                plt.rcParams['font.family'] = f.name
                plt.rcParams['axes.unicode_minus'] = False
                return
    except Exception:
        pass


def create_radar_chart(keyword_results: dict[str, dict], chart_path: str):
    """
    키워드별 점수를 바탕으로 레이더 차트를 그리고 PNG로 저장합니다.
    """
    setup_matplotlib_korean()
    labels = list(keyword_results.keys())
    values = [keyword_results[k]["score"] for k in labels]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, marker='o', linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, max(15, max(values)))
    ax.set_yticks([3, 6, 9, 12, 15])
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def generate_pdf(
    keyword_results: dict[str, dict],
    chart_path: str,
    output_path: str,
    interviewee_id: str,
    answers: list[str],
    nonverbal_score: int,
    nonverbal_reason: str,
    total_score: int,
    area_scores: dict[str, int],
    weights: dict[str, str],
) -> float:
    """
    PDF 생성:
    1) 레이더 차트
    2) 영역별 100점 스케일 점수 + 가중치
    3) 답변만 보기
    4) 키워드 점수표
    5) 2페이지: 키워드별 평가 사유 + 총합(100점) + 비언어(15점) + 생성시간
    """
    start = time.perf_counter()
    interview_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf = PDFReport(interviewee_id=interviewee_id, interview_time=interview_time)

    # 첫 페이지
    pdf.add_page()
    pdf.add_chart(chart_path)
    pdf.add_area_scores(area_scores, weights)

    answer_text = build_answer_blocks_text(answers)
    pdf.add_answer_blocks(answer_text)

    pdf.add_score_table(keyword_results)

    # 두 번째 페이지
    pdf.add_page()
    pdf.add_reasons(keyword_results)
    pdf.add_total_score(total_score)

    # 비언어 점수 및 사유
    try:
        pdf.set_font("Korean", "", 12)
    except:
        pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"비언어 점수 (15점 만점): {nonverbal_score}", ln=True)
    pdf.multi_cell(0, 7, f"비언어 평가 사유:\n{nonverbal_reason}")

    # 생성 시간
    elapsed = time.perf_counter() - start
    try:
        pdf.set_font("Korean", "", 10)
    except:
        pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"PDF 생성 시간: {elapsed:.2f}초", ln=True, align="R")

    pdf.output(output_path)
    return elapsed