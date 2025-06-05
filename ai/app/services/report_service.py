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
            # 시스템별 폰트 경로 설정
            if platform.system() == "Windows":
                font_paths = [
                    "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
                    "C:/Windows/Fonts/NanumGothic.ttf",  # 나눔고딕
                    "fonts/NanumGothic-Regular.ttf"  # 프로젝트 내 폰트
                ]
            elif platform.system() == "Darwin":  # macOS
                font_paths = [
                    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                    "/Library/Fonts/NanumGothic.ttf",
                    "fonts/NanumGothic-Regular.ttf"
                ]
            else:  # Linux
                font_paths = [
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                    "fonts/NanumGothic-Regular.ttf"
                ]

            # 사용 가능한 폰트 찾기
            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.add_font("Korean", "", font_path, uni=True)
                    print(f"✅ 폰트 로드 성공: {font_path}")
                    return

            # 폰트를 찾지 못한 경우 경고
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
    """matplotlib 한글 폰트 설정"""
    try:
        if platform.system() == "Windows":
            # Windows용 폰트 설정
            font_candidates = ['Malgun Gothic', 'NanumGothic', 'Arial Unicode MS']
        elif platform.system() == "Darwin":  # macOS
            font_candidates = ['AppleGothic', 'NanumGothic', 'Arial Unicode MS']
        else:  # Linux
            font_candidates = ['NanumGothic', 'DejaVu Sans']

        # 사용 가능한 폰트 찾기
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        for font_name in font_candidates:
            if font_name in available_fonts:
                plt.rcParams['font.family'] = font_name
                print(f"✅ Matplotlib 한글 폰트 설정: {font_name}")
                break
        else:
            print("⚠️  Matplotlib 한글 폰트를 찾지 못했습니다.")

        # 마이너스 폰트 깨짐 방지
        plt.rcParams['axes.unicode_minus'] = False

    except Exception as e:
        print(f"❌ Matplotlib 폰트 설정 오류: {e}")


def create_radar_chart(
        comp_results: dict[str, dict],
        chart_path: str
) -> None:
    """레이더 차트 생성 (한글 지원)"""
    # 한글 폰트 설정
    setup_matplotlib_korean()

    labels = list(comp_results.keys())
    values = [comp_results[c]["avg_score"] for c in labels]

    # 각도 계산
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]  # 첫 번째 값을 마지막에 추가 (닫힌 도형)
    angles += angles[:1]

    # 차트 생성
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, marker='o', linewidth=2, color='#1f77b4')
    ax.fill(angles, values, alpha=0.25, color='#1f77b4')

    # 축 설정
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.grid(True)

    # 제목 설정
    plt.title("역량별 평가 점수", size=16, pad=20)

    # 차트 저장
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()  # 메모리 정리
    print(f"✅ 차트 저장 완료: {chart_path}")


def generate_pdf(
        comp_results: dict[str, dict],
        chart_path: str,
        output_path: str
) -> float:
    """PDF 리포트 생성"""
    start = time.perf_counter()

    try:
        # 레이더 차트 생성
        create_radar_chart(comp_results, chart_path)

        # PDF 생성
        pdf = PDFReport()
        pdf.add_page()

        # 역량별 평가 추가
        for comp, res in comp_results.items():
            pdf.add_comp(comp, res["avg_score"], res["reasons"])

        # 차트 추가
        pdf.add_chart(chart_path)

        # 생성 시간 추가
        generation_time = time.perf_counter() - start
        try:
            pdf.set_font("Korean", "", 10)
        except:
            pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"PDF 생성 시간: {generation_time:.2f}초", ln=True, align="R")

        # PDF 저장
        pdf.output(output_path)
        print(f"✅ PDF 생성 완료: {output_path}")

        return generation_time

    except Exception as e:
        print(f"❌ PDF 생성 오류: {e}")
        raise


# 테스트용 함수
def test_korean_support():
    """한글 지원 테스트"""
    test_data = {
        "커뮤니케이션": {"avg_score": 85, "reasons": "명확하고 논리적인 답변을 제시했습니다."},
        "문제 해결": {"avg_score": 75, "reasons": "창의적인 접근 방식을 보여주었습니다."},
        "리더십": {"avg_score": 90, "reasons": "팀워크와 협업 능력이 우수합니다."},
        "전문성": {"avg_score": 80, "reasons": "해당 분야의 깊은 이해를 보여주었습니다."}
    }

    chart_path = "test_radar_chart.png"
    pdf_path = "test_report.pdf"

    try:
        generation_time = generate_pdf(test_data, chart_path, pdf_path)
        print(f"✅ 테스트 완료! 생성 시간: {generation_time:.2f}초")
        return True
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    test_korean_support()