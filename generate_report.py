"""
generate_report.py - Generates the official Project Report PDF for submission
Includes Antigravity prompt usage, system architecture, search result screenshots, and QR code.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Korean TrueType Font
FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

pdfmetrics.registerFont(TTFont("KoreanFont", FONT_PATH))
pdfmetrics.registerFont(TTFont("KoreanFontBold", FONT_PATH))


def build_pdf_report(output_filename="project_report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Korean Styles
    title_style = ParagraphStyle(
        "KTitle",
        fontName="KoreanFontBold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f3460"),
        alignment=1,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "KSubtitle",
        fontName="KoreanFont",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#333333"),
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        "KH1",
        fontName="KoreanFontBold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=10,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        "KH2",
        fontName="KoreanFontBold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0f3460"),
        spaceBefore=6,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "KBody",
        fontName="KoreanFont",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#222222"),
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        "KBodyBold",
        fontName="KoreanFontBold",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#222222")
    )

    code_style = ParagraphStyle(
        "KCode",
        fontName="KoreanFont",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1b262c"),
        backColor=colors.HexColor("#f0f4f8"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=4,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        "KCallout",
        fontName="KoreanFont",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#3b82f6"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=6
    )

    story = []

    # ================= PAGE 1 =================
    # Document Header
    story.append(Paragraph("제주데이터허브 인포그래픽 & 차트 AI 멀티모달(CLIP) 검색 시스템 구축 보고서", title_style))
    story.append(Paragraph("중간고사 대체과제 (Midterm Exam Replacement Project) | Google DeepMind Antigravity 2.0 활용", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0f3460"), spaceAfter=10))

    # Meta Info Table
    meta_data = [
        [Paragraph("<b>과제명</b>", body_bold), Paragraph("제주데이터허브 AI 멀티모달(CLIP) 이미지 검색 시스템 구축 및 클라우드 배포", body_style),
         Paragraph("<b>소속/학과</b>", body_bold), Paragraph("제주대학교 컴퓨터공학과", body_style)],
        [Paragraph("<b>공개 배포 URL</b>", body_bold), Paragraph("<font color='#0066cc'><u>https://samirwagle91-jeju-datahub.streamlit.app</u></font>", body_style),
         Paragraph("<b>제출일자</b>", body_bold), Paragraph("2026년 11월", body_style)],
        [Paragraph("<b>GitHub 저장소</b>", body_bold), Paragraph("<font color='#0066cc'><u>https://github.com/Samirwagle91/jeju-datahub-web</u></font>", body_style),
         Paragraph("<b>개발 도구</b>", body_bold), Paragraph("Google DeepMind Antigravity 2.0, Streamlit Cloud", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[85, 230, 70, 135])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: 프로젝트 배경 및 목적
    story.append(Paragraph("1. 프로젝트 배경 및 목적 (Background & Objectives)", h1_style))
    story.append(Paragraph(
        "<b>[AS-IS 문제점]</b> 제주데이터허브(jejudatahub.net)는 풍부한 빅데이터 소비동향 정기 분석 보고서를 제공하지만, 사용자가 원하는 "
        "특정 소비 트렌드 차트를 찾으려면 수십 페이지의 개별 PDF를 일일이 열어 확인해야 하는 비효율이 존재했습니다. "
        "또한 일상적 검색어('렌터카', '외식', '골프장')와 공공기관의 한국표준산업분류(KSIC) 행정 명칭('자동차 임대업', '한식음식점업', '골프장운영업') "
        "사이의 용어 격차로 인해 검색 누락이 빈번했습니다.", body_style
    ))
    story.append(Paragraph(
        "<b>[TO-BE 구축 목표]</b> Google DeepMind Antigravity 2.0을 페어 프로그래밍 AI로 활용하여, 한국어 일상 질의와 고해상도 차트 이미지를 "
        "하나의 512차원 잠재 벡터 공간에서 매핑하는 <b>AI 멀티모달(Multilingual CLIP) 검색 웹 서비스</b>를 개발하였습니다. "
        "KSIC 동의어 확장 알고리즘과 하이브리드 스코어링을 적용하여 일치율(%), 일치 사유(XAI), 원본 PDF/이미지 다운로드 및 "
        "실시간 유사도 슬라이더 필터링을 완비하고, Streamlit Community Cloud에 무료 공개 배포하였습니다.", body_style
    ))

    # Section 2: Antigravity 2.0 프롬프트 활용 과정
    story.append(Paragraph("2. Antigravity 2.0 프롬프트 활용 과정 (Antigravity Prompt Usage)", h1_style))
    story.append(Paragraph(
        "본 프로젝트는 Google DeepMind Antigravity 2.0과의 단계별 프롬프트 인터랙션을 통해 전 과정을 애자일하게 완성하였습니다:", body_style
    ))
    
    prompt_p1 = "<b>[프롬프트 1 - 데이터 파이프라인 및 추출기 구현]</b><br/>" \
                "<i>\"제주데이터허브 API(/api/report/list, /api/report/view, /api/file)를 연동하여 최근 10개 정기 소비동향 PDF를 자동 수집하고, " \
                "PyMuPDF를 활용해 전 페이지를 150 DPI 고해상도 PNG 차트 이미지와 구조화된 텍스트 메타데이터로 변환하는 collector.py와 extractor.py를 작성해줘.\"</i>"
    story.append(Paragraph(prompt_p1, callout_style))

    prompt_p2 = "<b>[프롬프트 2 - 멀티모달 임베딩 및 KSIC 동의어 하이브리드 엔진 설계]</b><br/>" \
                "<i>\"sentence-transformers의 clip-ViT-B-32-multilingual-v1 텍스트 모델과 clip-ViT-B-32 비전 모델을 결합하여, " \
                "사전 연산 512차원 벡터 캐시(embeddings.npz)를 구축해줘. '렌터카' 검색 시 KSIC '자동차 임대업'을 연계하고 일치율(%)과 일치 이유를 도출하는 searcher.py를 구현해줘.\"</i>"
    story.append(Paragraph(prompt_p2, callout_style))

    prompt_p3 = "<b>[프롬프트 3 - Streamlit 반응형 웹 대시보드 및 클라우드 배포 최적화]</b><br/>" \
                "<i>\"Pinterest 스타일의 4열 반응형 카드 갤러리 피드, 최소 일치율(%) 슬라이더, 라이트박스 상세 모달, 모바일 접속용 QR 코드를 갖춘 " \
                "Streamlit app.py를 개발하고 Streamlit Community Cloud 배포용 requirements.txt를 구성해줘.\"</i>"
    story.append(Paragraph(prompt_p3, callout_style))

    story.append(PageBreak())

    # ================= PAGE 2 =================
    # Section 3: 시스템 아키텍처 및 상세 구현
    story.append(Paragraph("3. 시스템 아키텍처 및 구현 결과 (System Architecture & Pipeline)", h1_style))
    
    arch_data = [
        [Paragraph("<b>계층 (Layer)</b>", body_bold), Paragraph("<b>주요 모듈 및 파일</b>", body_bold), Paragraph("<b>핵심 기술 및 세부 구현 내용</b>", body_bold)],
        [Paragraph("<b>1. Ingestion & ETL</b>", body_style), Paragraph("collector.py<br/>extractor.py", body_style), Paragraph("• 제주데이터허브 API 기반 10개 소비동향 보고서 자동 수집<br/>• PyMuPDF 150 DPI 고해상도 렌더링 (총 124개 차트 이미지 생성)", body_style)],
        [Paragraph("<b>2. Storage Layer</b>", body_style), Paragraph("data/images/<br/>embeddings.npz<br/>industries.json", body_style), Paragraph("• 124개 150 DPI PNG 차트 이미지 및 metadata.json 저장<br/>• 512차원 정규화 멀티모달 임베딩 벡터 사전 연산 캐싱 (초고속 응답)<br/>• 8대 주요 소비업종 KSIC 한국표준산업분류 동의어 사전", body_style)],
        [Paragraph("<b>3. AI Search Engine</b>", body_style), Paragraph("searcher.py<br/>(Multimodal)", body_style), Paragraph("• Multilingual CLIP 텍스트-비전 교차 모달 코사인 유사도 연산<br/>• KSIC 동의어 확장 + 어휘 문맥 스코어 결합 하이브리드 랭킹<br/>• 설명 가능한 AI(XAI): 일치율(%) 및 일치 이유 자동 생성", body_style)],
        [Paragraph("<b>4. Web Dashboard</b>", body_style), Paragraph("app.py<br/>(Streamlit UI)", body_style), Paragraph("• Pinterest 스타일 4열 차트 갤러리 피드 및 카테고리 퀵 버튼<br/>• 최소 일치율(%) 필터 슬라이더 (실시간 필터링)<br/>• 라이트박스 확대 모달, 고해상도 PNG 및 원본 PDF 1-클릭 다운로드", body_style)]
    ]
    t_arch = Table(arch_data, colWidths=[95, 95, 330])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f3460")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    # Section 4: 실제 검색 결과 및 슬라이더 동작 화면
    story.append(Paragraph("4. 실제 검색 결과 및 유사도 슬라이더 동작 검증 (Search Demo & Screenshots)", h1_style))
    story.append(Paragraph(
        "구축된 시스템에서 '렌터카' 키워드 검색 시, KSIC '자동차 임대업' 및 '차량용가스충전업'과의 연계를 통해 "
        "<b>최고 일치율 95.2%</b>의 고연관도 차트들이 갤러리 피드로 즉시 정렬되며, 50% 슬라이더 필터링이 정상 동작합니다.", body_style
    ))

    # Embed Search Results Screenshot
    if os.path.exists("search_results_demo.png"):
        story.append(Image("search_results_demo.png", width=520, height=180))
        story.append(Paragraph("<font size='7.5' color='#666'>[그림 1] '렌터카' 검색 결과: 50% 슬라이더 필터링, 일치율 95.2% 카드, KSIC 연계 일치 이유 및 본문 하이라이트</font>", subtitle_style))

    story.append(Spacer(1, 4))

    # Section 5: 배포 및 QR 코드
    story.append(Paragraph("5. 공개 웹 배포 및 제출 정보 (Public Deployment & QR Access)", h1_style))
    
    qr_data = [
        [
            Paragraph(
                "<b>[Streamlit Community Cloud 공개 배포]</b><br/>"
                "• <b>웹 서비스 접속 URL</b>: <font color='#0066cc'><u>https://samirwagle91-jeju-datahub.streamlit.app</u></font><br/>"
                "• <b>GitHub 저장소 URL</b>: <font color='#0066cc'><u>https://github.com/Samirwagle91/jeju-datahub-web</u></font><br/>"
                "• <b>제출 항목 완료 여부</b>: 공개 URL, QR 코드, GitHub URL, 프로젝트 보고서 일체 완료<br/>"
                "• <b>모바일 최적화</b>: 우측 QR 코드를 스마트폰 카메라로 스캔하여 즉시 모바일 웹앱 탐색 가능",
                body_style
            ),
            Image("qrcode.png", width=80, height=80) if os.path.exists("qrcode.png") else Paragraph("QR Code", body_style)
        ]
    ]
    t_qr = Table(qr_data, colWidths=[430, 90])
    t_qr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_qr)
    story.append(Spacer(1, 6))

    # Section 6: 추가 아이디어 및 향후 발전 방향
    story.append(Paragraph("6. 추가 기능 제안 및 향후 발전 방향 (Additional Ideas)", h1_style))
    story.append(Paragraph(
        "1) <b>LLM 기반 차트 인사이트 자동 생성</b>: 검색된 시계열 차트의 수치(전년 대비 증감율 등)를 OCR로 추출하고, Gemini/Antigravity LLM과 연계하여 3줄 요약 인사이트 자동 제공.<br/>"
        "2) <b>사용자 맞춤형 차트 즐겨찾기 및 PDF 리포트 재생성</b>: 검색된 개별 차트들을 장바구니에 담아 나만의 맞춤형 분석 보고서(PDF)로 일괄 다운로드하는 기능 확장.<br/>"
        "3) <b>도민 vs 관광객(내국인/외국인) 비교 필터</b>: 소비 주체별 필터를 세분화하여 제주 상권 분석 및 정책 수립 지원 고도화.",
        body_style
    ))

    doc.build(story)
    print(f"[✓] Official project report generated successfully: '{output_filename}'")
    return output_filename


if __name__ == "__main__":
    build_pdf_report()
