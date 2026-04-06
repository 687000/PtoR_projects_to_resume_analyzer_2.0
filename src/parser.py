import os
import re
import uuid
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


def _make_segment(text: str, page: int = 1, section: str = "", offset_start: int = 0) -> dict:
    return {
        "segment_id": str(uuid.uuid4()),
        "text": text,
        "location": {
            "page": page,
            "section": section,
            "offset_start": offset_start,
            "offset_end": offset_start + len(text),
        },
    }


def _result(raw_text: str, source_type: str, source_reference: str, metadata: dict, segments: list) -> dict:
    return {
        "source_type": source_type,
        "raw_text": raw_text,
        "source_reference": source_reference,
        "metadata": metadata,
        "provenance": {"segments": segments},
    }


def parse_text(text: str) -> dict:
    segments = [_make_segment(text)]
    return _result(text, "text", "", {}, segments)


def parse_files(paths: list) -> dict:
    """Parse multiple files and merge into a single source dict."""
    if len(paths) == 1:
        return parse_file(paths[0])
    all_texts = []
    all_segments = []
    all_filenames = []
    for path in paths:
        result = parse_file(path)
        all_texts.append(result["raw_text"])
        all_segments.extend(result["provenance"]["segments"])
        all_filenames.append(result["metadata"].get("filename", Path(path).name))
    raw_text = "\n\n---\n\n".join(all_texts)
    return _result(
        raw_text,
        "file",
        ", ".join(all_filenames),
        {"filenames": all_filenames, "file_count": len(paths)},
        all_segments,
    )


def parse_file(path: str) -> dict:
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(path)
    if suffix in (".txt", ".md"):
        text = p.read_text(encoding="utf-8", errors="replace")
        return _result(text, "file", p.name, {"filename": p.name}, [_make_segment(text)])
    if suffix in (".html", ".htm"):
        html = p.read_text(encoding="utf-8", errors="replace")
        return _parse_html_text(html, p.name, "file")
    if suffix in (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"):
        return _parse_image(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _parse_pdf(path: str) -> dict:
    import pdfplumber

    p = Path(path)
    segments = []
    pages_text = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append(text)
            if text.strip():
                segments.append(_make_segment(text, page=i))
    raw_text = "\n\n".join(pages_text)
    return _result(raw_text, "file", p.name, {"filename": p.name, "pages": len(pages_text)}, segments)


def _parse_image(path: str) -> dict:
    import pytesseract
    from PIL import Image

    p = Path(path)
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return _result(text, "file", p.name, {"filename": p.name, "ocr": True}, [_make_segment(text)])


def _parse_html_text(html: str, reference: str, source_type: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    container = soup.find("article") or soup.find("main") or soup.body or soup
    text = container.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return _result(text, source_type, reference, {}, [_make_segment(text)])


def parse_url(url: str) -> dict:
    _validate_url(url)
    resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return _parse_html_text(resp.text, url, "url")


def parse_notion(url: str, token: Optional[str] = None) -> dict:
    token = token or os.environ.get("NOTION_TOKEN", "")
    if not token:
        raise RuntimeError("NOTION_TOKEN not set")
    page_id = _extract_notion_page_id(url)
    headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}
    blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    resp = requests.get(blocks_url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    texts = []
    for block in data.get("results", []):
        bt = block.get("type", "")
        rich = block.get(bt, {}).get("rich_text", [])
        line = "".join(r.get("plain_text", "") for r in rich)
        if line.strip():
            texts.append(line)
    raw_text = "\n".join(texts)
    segments = [_make_segment(t, section=str(i)) for i, t in enumerate(texts)]
    return _result(raw_text, "notion", url, {"page_id": page_id}, segments)


def _extract_notion_page_id(url: str) -> str:
    match = re.search(r"([a-f0-9]{32})", url.replace("-", ""))
    if not match:
        raise ValueError(f"Cannot extract Notion page ID from URL: {url}")
    raw = match.group(1)
    return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"


def _validate_url(url: str) -> None:
    if not re.match(r"^https?://", url):
        raise ValueError(f"Invalid URL: {url}")
