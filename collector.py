"""
collector.py - Jeju Data Hub Periodic Report Collector
Fetches periodic spending analysis reports (PDF) and metadata from Jeju Data Hub API.
"""

import os
import json
import ssl
import time
import urllib.request
import urllib.parse
from typing import List, Dict, Any

API_BASE_URL = "https://jejudatahub.net/api"
DEFAULT_OUTPUT_DIR = "data/reports"
METADATA_FILE = "data/reports_metadata.json"


def _create_ssl_context():
    """Create unverified SSL context to prevent macOS certificate verification errors."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_report_list(length: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch recent periodic reports metadata from Jeju Data Hub API.
    """
    params = {
        "selection": "title + contents",
        "keyword": "",
        "isPaging": "true",
        "start": 0,
        "pageNumber": 1,
        "length": length,
        "openYn": "true",
    }
    url = f"{API_BASE_URL}/report/list?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )

    ctx = _create_ssl_context()
    print(f"[*] Requesting report list from {url}...")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed to fetch report list: HTTP {resp.status}")
        data = json.loads(resp.read().decode("utf-8"))
        records = data.get("data", [])
        print(f"[+] Found {len(records)} reports in current page (Total available: {data.get('recordsTotal')})")
        return records


def fetch_report_detail(report_id: int) -> Dict[str, Any]:
    """
    Fetch single report detail including file attachments.
    """
    url = f"{API_BASE_URL}/report/view?id={report_id}&user="
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )
    ctx = _create_ssl_context()
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed to fetch report view {report_id}: HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


def download_file(file_info_id: int, file_parent_id: int, target_path: str) -> bool:
    """
    Download PDF file from Jeju Data Hub file API.
    """
    url = f"{API_BASE_URL}/file?id={file_info_id}&fileId={file_parent_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
    )
    ctx = _create_ssl_context()
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                if resp.status == 200:
                    content = resp.read()
                    if content.startswith(b"%PDF"):
                        with open(target_path, "wb") as f:
                            f.write(content)
                        return True
                    else:
                        print(f"[-] Warning: downloaded content for {file_info_id} is not valid PDF (size={len(content)})")
        except Exception as e:
            print(f"[-] Retry {attempt}/3 downloading {file_info_id}: {e}")
            time.sleep(1)
    return False


def fetch_and_download_reports(output_dir: str = DEFAULT_OUTPUT_DIR, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Collect metadata and PDF files from recent Jeju Data Hub periodic reports (5-10 reports).
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

    items = fetch_report_list(length=limit)
    collected = []

    for idx, item in enumerate(items[:limit], 1):
        report_id = item.get("id")
        title = item.get("title", f"Report_{report_id}")
        print(f"\n[{idx}/{limit}] Fetching Report #{report_id}: {title}")

        try:
            detail = fetch_report_detail(report_id)
            file_section = detail.get("file", {})
            file_infos = file_section.get("fileInfos", []) if file_section else []

            if not file_infos:
                print(f"[-] No attached file for report {report_id}")
                continue

            first_file = file_infos[0]
            f_id = first_file.get("id")
            f_parent_id = first_file.get("fileId")
            f_name = first_file.get("fileName")
            create_at = detail.get("createAt") or item.get("regDate") or ""

            target_filename = f"{report_id}_{f_name}"
            target_path = os.path.join(output_dir, target_filename)

            if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                print(f"[=] PDF already exists: {target_filename} ({os.path.getsize(target_path)} bytes)")
                download_success = True
            else:
                print(f"[+] Downloading PDF: {f_name} (File ID: {f_id})...")
                download_success = download_file(f_id, f_parent_id, target_path)

            if download_success:
                record = {
                    "report_id": report_id,
                    "title": title,
                    "date": create_at,
                    "file_name": target_filename,
                    "file_path": target_path,
                    "file_size": os.path.getsize(target_path) if os.path.exists(target_path) else 0,
                    "view_count": detail.get("viewCount", 0),
                    "summary_html": detail.get("contents", "")
                }
                collected.append(record)
                print(f"[✓] Saved: {target_filename} ({record['file_size']} bytes)")
            else:
                print(f"[✗] Failed to download PDF for report {report_id}")

        except Exception as e:
            print(f"[✗] Error processing report {report_id}: {e}")

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] Successfully collected {len(collected)} reports to '{output_dir}'.")
    print(f"[✓] Metadata saved to '{METADATA_FILE}'.")
    return collected


if __name__ == "__main__":
    fetch_and_download_reports()
