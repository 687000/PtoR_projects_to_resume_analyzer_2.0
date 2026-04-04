import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.parser import parse_input, _extract_notion_page_id


def test_plain_text_passthrough():
    text = "This is a software project about building a Vue 3 dashboard."
    result = parse_input(text)
    assert result["raw_text"] == text
    assert result["source_type"] == "text"
    assert result["metadata"] == {}


def test_text_file(tmp_path: Path):
    content = "Project: Internal tooling platform\nStack: Vue 3, FastAPI"
    f = tmp_path / "project.txt"
    f.write_text(content, encoding="utf-8")

    result = parse_input(str(f))
    assert result["raw_text"] == content
    assert result["source_type"] == "text_file"
    assert result["metadata"]["filename"] == "project.txt"


def test_markdown_file(tmp_path: Path):
    content = "# My Project\n\nBuilt a state management system."
    f = tmp_path / "notes.md"
    f.write_text(content, encoding="utf-8")

    result = parse_input(str(f))
    assert result["raw_text"] == content
    assert result["source_type"] == "text_file"


def test_html_file(tmp_path: Path):
    html = "<html><body><main><p>Built a Vue dashboard for internal ops.</p></main></body></html>"
    f = tmp_path / "page.html"
    f.write_text(html, encoding="utf-8")

    result = parse_input(str(f))
    assert result["source_type"] == "html_file"
    assert "Vue dashboard" in result["raw_text"]
    assert result["metadata"]["filename"] == "page.html"


def test_html_file_strips_scripts(tmp_path: Path):
    html = "<html><body><script>alert('x')</script><p>Actual content here.</p></body></html>"
    f = tmp_path / "page.html"
    f.write_text(html, encoding="utf-8")

    result = parse_input(str(f))
    assert "alert" not in result["raw_text"]
    assert "Actual content" in result["raw_text"]


def test_html_file_empty_raises(tmp_path: Path):
    html = "<html><body><script>alert('x')</script></body></html>"
    f = tmp_path / "empty.html"
    f.write_text(html, encoding="utf-8")

    with pytest.raises(ValueError, match="No readable text"):
        parse_input(str(f))


def test_url_scraping():
    mock_response = MagicMock()
    mock_response.text = "<html><body><article><p>Project description from web.</p></article></body></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("src.parser.requests.get", return_value=mock_response):
        result = parse_input("https://example.com/project")

    assert result["source_type"] == "url"
    assert "Project description from web" in result["raw_text"]
    assert result["metadata"]["url"] == "https://example.com/project"


def test_url_request_failure_raises():
    import requests as req_lib
    with patch("src.parser.requests.get", side_effect=req_lib.RequestException("timeout")):
        with pytest.raises(ValueError, match="Failed to fetch URL"):
            parse_input("https://example.com/project")


def test_notion_url_dispatched(monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "secret-token")

    mock_blocks = {
        "results": [
            {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Notion page content."}]}, "has_children": False, "id": "block-1"}
        ]
    }
    mock_response = MagicMock()
    mock_response.json.return_value = mock_blocks
    mock_response.raise_for_status = MagicMock()

    with patch("src.parser.requests.get", return_value=mock_response):
        result = parse_input("https://www.notion.so/My-Project-abc123def456abc123def456abc123de")

    assert result["source_type"] == "notion"
    assert "Notion page content" in result["raw_text"]


def test_notion_no_token_raises(monkeypatch):
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    with pytest.raises(ValueError, match="NOTION_TOKEN"):
        parse_input("https://www.notion.so/My-Project-abc123def456abc123def456abc123de")


def test_image_ocr(tmp_path: Path):
    f = tmp_path / "screenshot.png"
    f.write_bytes(b"fake png bytes")

    mock_image = MagicMock()
    mock_image.size = (800, 600)

    with patch("PIL.Image.open", return_value=mock_image):
        with patch("pytesseract.image_to_string", return_value="Vue 3 project overview"):
            result = parse_input(str(f))

    assert result["source_type"] == "image_ocr"
    assert result["raw_text"] == "Vue 3 project overview"
    assert result["metadata"]["filename"] == "screenshot.png"


def test_image_ocr_empty_result_raises(tmp_path: Path):
    f = tmp_path / "blank.png"
    f.write_bytes(b"fake png bytes")

    mock_image = MagicMock()
    with patch("PIL.Image.open", return_value=mock_image):
        with patch("pytesseract.image_to_string", return_value="   "):
            with pytest.raises(ValueError, match="OCR produced no text"):
                parse_input(str(f))


def test_empty_text_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_input("   ")


def test_empty_text_file_raises(tmp_path: Path):
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        parse_input(str(f))


def test_unsupported_file_type_raises(tmp_path: Path):
    f = tmp_path / "doc.docx"
    f.write_bytes(b"fake docx content")
    with pytest.raises(ValueError, match="Unsupported file type"):
        parse_input(str(f))


def test_nonexistent_path_treated_as_text():
    text = "/path/that/does/not/exist.txt"
    result = parse_input(text)
    assert result["source_type"] == "text"
    assert result["raw_text"] == text


# Notion page ID extraction
def test_extract_notion_page_id_standard_url():
    url = "https://www.notion.so/My-Project-abc123def456abc123def456abc123de"
    page_id = _extract_notion_page_id(url)
    assert page_id == "abc123de-f456-abc1-23de-f456abc123de"


def test_extract_notion_page_id_no_match():
    assert _extract_notion_page_id("https://www.notion.so/short") is None
