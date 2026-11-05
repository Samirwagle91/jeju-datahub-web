"""
extractor.py - PDF Text Extractor and High-Resolution Chart Image Renderer
Extracts page-level text from PDF documents and renders 150 DPI PNG chart images.
"""

import os
import re
import json
import glob
from typing import List, Dict, Any, Optional
import pymupdf

DEFAULT_PDF_DIR = "data/reports"
DEFAULT_IMAGE_DIR = "data/images"
METADATA_JSON_PATH = "data/metadata.json"
REPORTS_METADATA_PATH = "data/reports_metadata.json"


def extract_chart_title_from_lines(lines: List[str]) -> str:
    """
    Heuristically extract the main chart or section title from page text lines.
    """
    # 1. Look for brackets like [제주도전체], [국내관광객], [중국관광객]
    for line in lines:
        cleaned = line.strip()
        if re.search(r'\[.+?\].*(?:비교|동향|분석|매출|추이|현황|설명|이용)', cleaned):
            return cleaned
        if cleaned.startswith("[") and cleaned.endswith("]") and len(cleaned) < 50:
            return cleaned

    # 2. Look for keywords indicating title
    for line in lines:
        cleaned = line.strip()
        if any(kw in cleaned for kw in ["카드이용금액", "소비동향", "주요업종별", "1인당", "이용금액(BC)", "동향 분석", "비교치"]):
            if len(cleaned) <= 80:
                return cleaned

    # 3. Fallback to first non-empty line that isn't just a page number
    for line in lines:
        cleaned = line.strip()
        if cleaned and not re.match(r'^\d+\s*/\s*\d+$', cleaned) and len(cleaned) > 3:
            return cleaned[:60]

    return "소비동향 분석 차트"


def extract_pages_and_render_images(
    pdf_dir: str = DEFAULT_PDF_DIR,
    image_dir: str = DEFAULT_IMAGE_DIR,
    dpi: int = 150
) -> List[Dict[str, Any]]:
    """
    Render all pages of each PDF to 150 DPI PNG images and extract page text.
    Returns and saves a comprehensive list of page metadata.
    """
    os.makedirs(image_dir, exist_ok=True)

    # Load report metadata if available
    report_meta_map = {}
    if os.path.exists(REPORTS_METADATA_PATH):
        try:
            with open(REPORTS_METADATA_PATH, "r", encoding="utf-8") as f:
                rep_list = json.load(f)
                for item in rep_list:
                    report_meta_map[item["report_id"]] = item
        except Exception as e:
            print(f"[-] Warning: Failed to load {REPORTS_METADATA_PATH}: {e}")

    pdf_files = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    if not pdf_files:
        print(f"[!] No PDF files found in {pdf_dir}. Run collector.py first!")
        return []

    print(f"[*] Found {len(pdf_files)} PDF reports. Extracting text and rendering {dpi} DPI images...")
    pages_metadata = []

    for pdf_idx, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        # Extract report ID if prefixed (e.g., '86_2025-12...')
        m = re.match(r'^(\d+)_', filename)
        report_id = int(m.group(1)) if m else pdf_idx

        rep_info = report_meta_map.get(report_id, {})
        report_title = rep_info.get("title", filename.replace(".pdf", ""))
        report_date = rep_info.get("date", "")

        print(f"\n[{pdf_idx}/{len(pdf_files)}] Processing {filename}...")
        try:
            doc = pymupdf.open(pdf_path)
            total_pages = len(doc)

            for page_idx in range(total_pages):
                page_num = page_idx + 1
                page = doc[page_idx]

                # Extract text
                raw_text = page.get_text()
                lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
                clean_text = " ".join(lines)
                chart_title = extract_chart_title_from_lines(lines)

                # Render page image at specified DPI
                image_filename = f"report_{report_id}_p{page_num}.png"
                image_rel_path = os.path.join(image_dir, image_filename)

                # Check if already rendered
                if not os.path.exists(image_rel_path) or os.path.getsize(image_rel_path) == 0:
                    pix = page.get_pixmap(dpi=dpi)
                    pix.save(image_rel_path)

                has_chart = (page_num > 1) or ("차트" in clean_text or "비교" in clean_text or "금액" in clean_text)

                page_record = {
                    "id": f"report_{report_id}_p{page_num}",
                    "report_id": report_id,
                    "report_title": report_title,
                    "date": report_date,
                    "page_num": page_num,
                    "total_pages": total_pages,
                    "image_path": image_rel_path,
                    "pdf_path": pdf_path,
                    "chart_title": chart_title,
                    "text": clean_text,
                    "raw_lines": lines[:15],
                    "char_count": len(clean_text),
                    "has_chart": has_chart,
                }
                pages_metadata.append(page_record)

            print(f"[✓] Rendered {total_pages} pages for report #{report_id}")
            doc.close()

        except Exception as e:
            print(f"[✗] Error processing {pdf_path}: {e}")

    # Save to metadata.json
    with open(METADATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(pages_metadata, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Successfully processed {len(pages_metadata)} total pages across {len(pdf_files)} reports.")
    print(f"[✓] Metadata saved to '{METADATA_JSON_PATH}'.")
    return pages_metadata


if __name__ == "__main__":
    extract_pages_and_render_images()
