"""
run_pipeline.py - End-to-End Ingestion, Extraction, and Multimodal Indexing Pipeline
Orchestrates:
1. Data collection from Jeju Data Hub API (collector.py)
2. PDF text extraction & 150 DPI chart image rendering (extractor.py)
3. Multimodal CLIP embedding generation & vector indexing (searcher.py)
4. Summary status report generation (counts.txt)
"""

import os
import sys
import time
from datetime import datetime

import collector
import extractor
import searcher


def main():
    start_time = time.time()
    print("=" * 70)
    print(" 제주데이터허브 AI 멀티모달(CLIP) 검색 파이프라인 시작")
    print(f" 시작 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1단계: 데이터 수집 (collector.py)
    print("\n[단계 1/3] 제주데이터허브 정기 소비동향 분석 보고서 수집 (collector.py)")
    reports = collector.fetch_and_download_reports(output_dir="data/reports", limit=10)
    print(f"[✓] 1단계 완료: 총 {len(reports)}개 PDF 보고서 수집 완료")

    # 2단계: PDF 텍스트 추출 & 150 DPI 고화질 차트 렌더링 (extractor.py)
    print("\n[단계 2/3] PDF 페이지별 텍스트 추출 및 150 DPI 차트 이미지 렌더링 (extractor.py)")
    pages = extractor.extract_pages_and_render_images(
        pdf_dir="data/reports",
        image_dir="data/images",
        dpi=150
    )
    print(f"[✓] 2단계 완료: 총 {len(pages)}개 페이지 렌더링 및 텍스트 추출 완료")

    # 3단계: 멀티모달 임베딩 계산 및 인덱싱 (searcher.py)
    print("\n[단계 3/3] Multilingual CLIP 멀티모달 임베딩 벡터 생성 및 인덱싱 (searcher.py)")
    emb_path = searcher.build_embeddings(
        metadata_path="data/metadata.json",
        embeddings_path="data/embeddings.npz"
    )
    print(f"[✓] 3단계 완료: 멀티모달 벡터 캐시 생성 완료 ({emb_path})")

    elapsed = time.time() - start_time

    # counts.txt 생성
    counts_content = f"""======================================================================
Jeju Data Hub Multimodal AI Image Search - Pipeline Summary Report
======================================================================
Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Pipeline Elapsed Time: {elapsed:.2f} seconds

1. Collected Reports (PDF):
   - Total Reports: {len(reports)}
   - Target Source: Jeju Data Hub (https://jejudatahub.net)
   - Category: BC Card Jeju Spending Trend Periodic Analysis

2. Rendered Chart Images (150 DPI PNG):
   - Total Pages Indexed: {len(pages)}
   - Image Directory: data/images/
   - Resolution: High-Resolution 150 DPI (.png)

3. Multimodal Vector Index:
   - Text Model: sentence-transformers/clip-ViT-B-32-multilingual-v1
   - Vision Model: clip-ViT-B-32
   - Embedding Dimensions: 512 dimensions
   - Precomputed Cache: data/embeddings.npz
   - Industry Classifier: industries.json (KSIC Synonym Expansion)

4. Web Application Status:
   - Streamlit Application: app.py
   - Ready for Local & Cloud Deployment
======================================================================
"""
    with open("counts.txt", "w", encoding="utf-8") as f:
        f.write(counts_content)

    print("\n" + counts_content)
    print("[✓] 파이프라인 전체 완료 및 counts.txt 저장 성공!")


if __name__ == "__main__":
    main()
