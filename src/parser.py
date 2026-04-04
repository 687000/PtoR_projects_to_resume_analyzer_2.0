import os
import re
from pathlib import Path

import pdfplumber
import pytesseract
import requests
from bs4 import BeautifulSoup
from PIL import Image


def parse_input(source: str) -> dict:
    """
    Normalize a source (file path, URL, or plain text) into raw_text + metadata.

    Returns:
        { raw_text: str, source_type: str, metadata: dict }
    """
    # URL — check before file path lookup
    if source.startswith("http://") or source.startswith("https://"):
        if "notion.so" in source or "notion.site" in source:
            return _parse_notion(source)
        return _parse_url(source)

    path = Path(source)

    if len(source) <= 1024 and path.exists() and path.is_file():
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return _parse_pdf(path)
        elif suffix in (".txt", ".md"):
            return _parse_text_file(path)
        elif suffix in (".html", ".htm"):
            return _parse_html_file(path)
        elif suffix in (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"):
            return _parse_image(path)
        else:
            raise ValueError(
                f"Unsupported file type '{suffix}'. Supported: .pdf, .txt, .md, .html, .jpg, .png"
            )

    if not source.strip():
        raise ValueError("Input text is empty.")

    return {
        "raw_text": source,
        "source_type": "text",
        "metadata": {},
    }


def _parse_pdf(path: Path) -> dict:
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]

    raw_text = "\n\n".join(p for p in pages if p.strip())

    if not raw_text.strip():
        raise ValueError(f"No extractable text found in PDF: {path.name}")

    return {
        "raw_text": raw_text,
        "source_type": "pdf",
        "metadata": {"filename": path.name, "pages": len(pages)},
    }


def _parse_text_file(path: Path) -> dict:
    raw_text = path.read_text(encoding="utf-8")

    if not raw_text.strip():
        raise ValueError(f"File is empty: {path.name}")

    return {
        "raw_text": raw_text,
        "source_type": "text_file",
        "metadata": {"filename": path.name},
    }


def _parse_html_file(path: Path) -> dict:
    html = path.read_text(encoding="utf-8")
    raw_text = _extract_text_from_html(html)

    if not raw_text.strip():
        raise ValueError(f"No readable text found in HTML file: {path.name}")

    return {
        "raw_text": raw_text,
        "source_type": "html_file",
        "metadata": {"filename": path.name},
    }


def _parse_image(path: Path) -> dict:
    image = Image.open(path)
    raw_text = pytesseract.image_to_string(image).strip()

    if not raw_text:
        raise ValueError(f"OCR produced no text from image: {path.name}")

    return {
        "raw_text": raw_text,
        "source_type": "image_ocr",
        "metadata": {"filename": path.name, "size": image.size},
    }


def _parse_url(url: str) -> dict:
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")

    raw_text = _extract_text_from_html(response.text)

    if not raw_text.strip():
        raise ValueError(f"No readable text found at URL: {url}")

    return {
        "raw_text": raw_text,
        "source_type": "url",
        "metadata": {"url": url},
    }


def _parse_notion(url: str) -> dict:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError(
            "NOTION_TOKEN environment variable not set. "
            "Create a Notion integration at https://www.notion.so/my-integrations and share the page with it."
        )

    page_id = _extract_notion_page_id(url)
    if not page_id:
        raise ValueError(f"Could not extract page ID from Notion URL: {url}")

    raw_text = _fetch_notion_page_text(page_id, token)

    if not raw_text.strip():
        raise ValueError(f"No readable content found in Notion page: {url}")

    return {
        "raw_text": raw_text,
        "source_type": "notion",
        "metadata": {"url": url, "page_id": page_id},
    }


def _extract_notion_page_id(url: str) -> str | None:
    # Notion page IDs are 32 hex chars, may appear with or without dashes
    match = re.search(r"([0-9a-f]{32})", url.replace("-", ""))
    if match:
        raw = match.group(1)
        # Format as UUID: 8-4-4-4-12
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    return None


def _fetch_notion_page_text(page_id: str, token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
    }

    def get_blocks(block_id: str) -> list[dict]:
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except requests.RequestException:
            return []

    def extract_text(blocks: list[dict]) -> str:
        lines = []
        for block in blocks:
            btype = block.get("type", "")
            content = block.get(btype, {})
            rich_texts = content.get("rich_text", [])
            text = "".join(rt.get("plain_text", "") for rt in rich_texts)
            if text:
                lines.append(text)
            if block.get("has_children"):
                child_blocks = get_blocks(block["id"])
                lines.append(extract_text(child_blocks))
        return "\n".join(lines)

    blocks = get_blocks(page_id)
    return extract_text(blocks)


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Prefer article or main content if available
    main = soup.find("article") or soup.find("main") or soup.find("body") or soup
    return main.get_text(separator="\n", strip=True)
