"""
app.py - Streamlit Web Dashboard for Jeju Data Hub Multimodal AI Chart & Image Search
Matches the reference architecture and UI design specified in the midterm project guidelines.
"""

import os
import re
import io
import json
import base64
from typing import List, Dict, Any, Optional
import streamlit as st
import numpy as np
from PIL import Image
import qrcode

# Import multimodal search engine
from searcher import JejuMultimodalSearcher, DEFAULT_DATA_DIR

DEFAULT_APP_URL = "https://jeju-datahub-clip-search.streamlit.app"


@st.cache_resource(show_spinner="AI 멀티모달 검색 엔진 로딩 중...")
def get_searcher() -> JejuMultimodalSearcher:
    """
    Cache searcher instance with precomputed vector index.
    """
    searcher = JejuMultimodalSearcher(data_dir=DEFAULT_DATA_DIR)
    return searcher


def resolve_image_path(path: str) -> str:
    """
    Ensure relative image path exists and can be loaded.
    """
    if os.path.exists(path):
        return path
    alt = os.path.join(".", path)
    if os.path.exists(alt):
        return alt
    return path


def highlight_text(text: str, terms: List[str]) -> str:
    """
    Highlight matched query terms with yellow background.
    """
    if not text or not terms:
        return text
    highlighted = text
    for term in terms:
        if len(term.strip()) >= 2:
            pattern = re.compile(f"({re.escape(term.strip())})", re.IGNORECASE)
            highlighted = pattern.sub(r'<mark style="background-color: #ffeb3b; color: #000; padding: 2px 4px; border-radius: 3px; font-weight: bold;">\1</mark>', highlighted)
    return highlighted


def get_chart_title(item: Dict[str, Any]) -> str:
    """
    Extract or format chart title for card header.
    """
    title = item.get("chart_title", "")
    if not title or title.strip() == "소비동향 분석 차트":
        return f"{item.get('report_title', '소비동향 보고서')} (p.{item.get('page_num', 1)})"
    return title


def generate_qr_image(url: str) -> bytes:
    """
    Generate QR code image bytes for web app deployment URL.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0e1117", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@st.dialog("📊 고해상도 차트 상세 보기", width="large")
def show_image_modal(item: Dict[str, Any], query_terms: List[str]):
    """
    Modal dialog displaying full-screen chart image, source info, and page text.
    """
    st.subheader(item.get("chart_title", "차트 상세 정보"))
    st.caption(f"출처: {item.get('report_title', '')} | 등록일자: {item.get('date', '')} | 페이지: {item.get('page_num')}/{item.get('total_pages')}")

    img_path = resolve_image_path(item.get("image_path", ""))
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"이미지 파일을 찾을 수 없습니다: {img_path}")

    st.markdown(f"**💡 일치 이유**: {item.get('match_reason', '')}")
    st.markdown(f"**🎯 검색 일치율**: `{item.get('similarity_pct', 0)}%`")

    # Action downloads
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                st.download_button(
                    label="💾 고해상도 PNG 다운로드",
                    data=f.read(),
                    file_name=os.path.basename(img_path),
                    mime="image/png",
                    use_container_width=True
                )
    with col_dl2:
        pdf_path = item.get("pdf_path", "")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pf:
                st.download_button(
                    label="📄 원본 PDF 보고서 다운로드",
                    data=pf.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True
                )

    with st.expander("📝 해당 페이지 본문 전체 텍스트 확인 (키워드 하이라이트)"):
        highlighted = highlight_text(item.get("text", ""), query_terms)
        st.markdown(f"<div style='font-size: 13px; line-height: 1.6; color: #e0e0e0;'>{highlighted}</div>", unsafe_allow_html=True)


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="제주데이터허브 차트 & 이미지 검색",
        page_icon="🌴",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Custom CSS Theme matching Slide 8 & 12
    st.markdown("""
    <style>
        /* Modern Dark Theme adjustments */
        .main {
            background-color: #0d1117;
        }
        .main-header-title {
            font-size: 2.1rem;
            font-weight: 800;
            color: #58a6ff;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .main-header-sub {
            font-size: 1.05rem;
            color: #8b949e;
            margin-bottom: 20px;
        }
        .summary-banner {
            background: linear-gradient(90deg, #161b22, #1f2937);
            border-left: 4px solid #58a6ff;
            padding: 10px 16px;
            border-radius: 6px;
            font-size: 0.98rem;
            font-weight: 600;
            color: #e6edf3;
            margin-top: 10px;
            margin-bottom: 18px;
        }
        .result-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .result-card:hover {
            transform: translateY(-2px);
            border-color: #58a6ff;
            box-shadow: 0 4px 12px rgba(88, 166, 255, 0.15);
        }
        .card-title {
            font-size: 0.92rem;
            font-weight: 700;
            color: #f0f6fc;
            margin-top: 8px;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .card-meta {
            font-size: 0.78rem;
            color: #8b949e;
            margin-bottom: 8px;
        }
        .score-badge {
            background-color: #238636;
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 12px;
            float: right;
        }
        .score-badge-yellow {
            background-color: #d29922;
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 12px;
            float: right;
        }
        .score-badge-gray {
            background-color: #484f58;
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 12px;
            float: right;
        }
        .reason-box {
            background-color: #0d1117;
            border: 1px dashed #30363d;
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 0.78rem;
            color: #79c0ff;
            margin-top: 6px;
            margin-bottom: 6px;
        }
        .snippet-box {
            font-size: 0.78rem;
            color: #c9d1d9;
            background-color: #0d1117;
            padding: 6px 8px;
            border-radius: 4px;
            border-left: 2px solid #8b949e;
            margin-top: 4px;
            margin-bottom: 8px;
            line-height: 1.4;
        }
    </style>
    """, unsafe_allow_html=True)

    searcher = get_searcher()

    # Session state initialization
    if "search_query" not in st.session_state:
        st.session_state.search_query = "렌터카"
    if "selected_modal_item" not in st.session_state:
        st.session_state.selected_modal_item = None

    # 3. Sidebar Setup
    with st.sidebar:
        st.markdown("### 🌴 제주데이터허브")
        st.markdown("**AI 멀티모달(CLIP) 이미지 검색**")
        st.caption("Google DeepMind Antigravity 2.0 기반")

        st.markdown("---")
        st.markdown("#### 📱 모바일 웹 서비스 접속 (QR)")
        app_url = st.text_input("Streamlit 배포 URL", value=DEFAULT_APP_URL, help="Streamlit Cloud 배포 후 생성된 URL을 입력하면 QR 코드가 즉시 갱신됩니다.")
        qr_bytes = generate_qr_image(app_url)
        st.image(qr_bytes, caption="스마트폰 카메라로 스캔하여 접속", width=180)

        st.markdown("---")
        st.markdown("#### 📊 시스템 색인 통계")
        total_reports = len(set(m.get("report_id") for m in searcher.metadata))
        total_pages = len(searcher.metadata)
        st.markdown(f"""
        - 📄 **수집 보고서**: `{total_reports}`건 (정기 소비동향)
        - 🖼️ **색인 차트 이미지**: `{total_pages}`장 (150 DPI)
        - 🧠 **벡터 임베딩 차원**: `512`차원 (CLIP ViT-B-32)
        - 🏷️ **KSIC 표준 산업분류**: `{len(searcher.industries)}`개 주요 업종 연계
        """)

        st.markdown("---")
        st.markdown("#### ⚙️ 적용 AI 모델 아키텍처")
        st.markdown("""
        - **Text Model**: `sentence-transformers/clip-ViT-B-32-multilingual-v1`
        - **Vision Model**: `clip-ViT-B-32`
        - **Query Expansion**: 한국표준산업분류(KSIC) 동의어 사전 매핑
        - **Hybrid Ranking**: Multimodal Cosine Similarity + BM25 Context Scoring
        """)

        st.markdown("---")
        st.caption("제주대학교 컴퓨터공학과 / 중간고사 대체과제")

    # 4. Header Title & Subtitle
    st.markdown('<div class="main-header-title">🌴 제주데이터허브 차트 & 이미지 검색</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header-sub">원하는 키워드를 입력하면 빅데이터 소비 트렌드 차트 및 그래프 이미지만 즉시 찾아드립니다.</div>', unsafe_allow_html=True)

    # 5. Category Quick Buttons
    quick_categories = [
        ("전체보기", ""),
        ("렌터카", "렌터카"),
        ("외식(음식점)", "외식"),
        ("골프장", "골프장"),
        ("숙박(호텔)", "호텔"),
        ("카페·음료", "카페"),
        ("면세점 쇼핑", "면세점"),
        ("주유소", "주유소"),
    ]

    button_cols = st.columns(len(quick_categories))
    for col_idx, (cat_label, cat_query) in enumerate(quick_categories):
        with button_cols[col_idx]:
            if st.button(cat_label, use_container_width=True, key=f"quick_btn_{col_idx}"):
                st.session_state.search_query = cat_query
                st.rerun()

    # 6. Search Bar & Controls
    col_input, col_slider, col_checkbox = st.columns([5, 3, 2])

    with col_input:
        current_input = st.text_input(
            label="검색어 입력",
            value=st.session_state.search_query,
            placeholder="검색어를 입력하세요 (예: 렌터카, 외식, 골프장, 호텔, 면세점...)",
            help="검색어를 입력하고 Enter를 누르면 관련 이미지가 바로 아래에 나타납니다."
        )
        if current_input != st.session_state.search_query:
            st.session_state.search_query = current_input

    with col_slider:
        threshold_val = st.slider(
            label="최소 일치율 필터 (%)",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            help="설정한 일치율 이상의 고연관도 이미지만 우선적으로 표시합니다."
        )

    with col_checkbox:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        show_below_threshold = st.checkbox("50% 미만 보기 (?)", value=False, help="체크 시 최소 일치율 기준 미달 이미지도 함께 탐색할 수 있습니다.")

    st.caption("검색어를 입력하고 **Enter(Enter)**를 누르면 관련 이미지가 바로 아래에 나타납니다.")

    # 7. Execute Multimodal Search
    active_query = st.session_state.search_query.strip()
    search_results = searcher.search(
        query=active_query,
        threshold=threshold_val / 100.0,
        top_k=80
    )

    query_terms, matched_cat, _ = searcher.expand_query_terms(active_query)

    max_pct = search_results["max_similarity_pct"]
    count_high = search_results["count_above_threshold"]
    count_low = search_results["count_below_threshold"]

    # 8. Summary Banner matching Slide 12
    if active_query:
        st.markdown(f"""
        <div class="summary-banner">
            🔍 <b>'{active_query}'</b> 검색 결과 &nbsp;|&nbsp; 
            최고 일치율: <b>{max_pct:.1f}%</b> &nbsp;|&nbsp; 
            {threshold_val}% 이상: <b>{count_high}장</b> &nbsp;|&nbsp; 
            {threshold_val}% 미만: <b>{count_low}장</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="summary-banner">
            🔍 <b>전체 분석 보고서 차트 목록</b> &nbsp;|&nbsp; 총 <b>{len(search_results['results'])}장</b> 인덱싱 완료
        </div>
        """, unsafe_allow_html=True)

    # Determine cards to display based on threshold checkbox
    cards_to_show = search_results["results"] if show_below_threshold else search_results["above_threshold"]

    if not cards_to_show:
        st.info(f"선택하신 일치율 기준({threshold_val}%)을 만족하는 차트가 없습니다. 슬라이더 값을 낮추거나 '50% 미만 보기'를 체크해보세요.")
        return

    # 9. Cards Grid (4 columns responsive feed matching Pinterest/Google Images feed)
    NUM_COLS = 4
    cols = st.columns(NUM_COLS)

    for idx, card in enumerate(cards_to_show):
        target_col = cols[idx % NUM_COLS]
        with target_col:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)

            img_path = resolve_image_path(card["image_path"])
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x250?text=Chart+Image", use_container_width=True)

            # Similarity Badge
            sim_pct = card["similarity_pct"]
            if sim_pct >= 85:
                badge_class = "score-badge"
            elif sim_pct >= 60:
                badge_class = "score-badge-yellow"
            else:
                badge_class = "score-badge-gray"

            st.markdown(f"""
            <div>
                <span class="{badge_class}">일치율 {sim_pct:.0f}%</span>
                <div class="card-title">{get_chart_title(card)}</div>
            </div>
            <div class="card-meta">
                출처: {card.get('report_title', '')[:28]}...<br>
                등록일: {card.get('date', '')} (p.{card.get('page_num')})
            </div>
            <div class="reason-box">
                💡 <b>일치 이유</b>: {card.get('match_reason', '')}
            </div>
            """, unsafe_allow_html=True)

            # Snippet box
            snippet_raw = card.get("snippet", "")
            if snippet_raw:
                snippet_clean = snippet_raw.replace("<mark>", "").replace("</mark>", "")
                highlighted_snip = highlight_text(snippet_clean, query_terms)
                st.markdown(f"""
                <div class="snippet-box">
                    <b>본문 언급</b>: {highlighted_snip}
                </div>
                """, unsafe_allow_html=True)

            # Action Buttons
            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("🔍 크게 보기", key=f"zoom_{card['id']}_{idx}", use_container_width=True):
                    show_image_modal(card, query_terms)
            with btn_col2:
                if os.path.exists(img_path):
                    with open(img_path, "rb") as img_f:
                        st.download_button(
                            label="💾 저장",
                            data=img_f.read(),
                            file_name=os.path.basename(img_path),
                            mime="image/png",
                            key=f"dl_{card['id']}_{idx}",
                            use_container_width=True
                        )

            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
