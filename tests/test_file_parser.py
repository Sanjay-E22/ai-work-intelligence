
import pytest
import pymupdf
from app.utils.file_parser import parse_text,parse_pdf


def test_parse_valid_text():
    result = parse_text(b"Meeting tomorrow")
    assert result == "Meeting tomorrow"


def test_parse_removes_surrounding_whitespace():
    result = parse_text(b"  Finish API work  ")
    assert result == "Finish API work"


def test_parse_rejects_empty_bytes():
    with pytest.raises(ValueError, match="Content cannot be empty"):
        parse_text(b"")


def test_parse_rejects_whitespace_only():
    with pytest.raises(
        ValueError,
        match="Content cannot contain only whitespace",
    ):
        parse_text(b"   ")


def test_parse_rejects_invalid_utf8():
    with pytest.raises(ValueError, match="Content must be valid UTF-8"):
        parse_text(b"\xff")



def create_test_pdf(text: str) -> bytes:
    """Create a small in-memory PDF for testing."""
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)

    content = document.tobytes()
    document.close()

    return content


def test_parse_pdf_extracts_text():
    pdf_bytes = create_test_pdf("Meeting tomorrow")

    result = parse_pdf(pdf_bytes)

    assert "Meeting tomorrow" in result


def test_parse_pdf_rejects_empty_content():
    with pytest.raises(ValueError, match="PDF content cannot be empty"):
        parse_pdf(b"")


def test_parse_pdf_rejects_invalid_pdf():
    with pytest.raises(ValueError, match="Unable to read the PDF"):
        parse_pdf(b"This is not a PDF")


def test_parse_pdf_rejects_pdf_without_text():
    document = pymupdf.open()
    document.new_page()
    pdf_bytes = document.tobytes()
    document.close()

    with pytest.raises(
        ValueError,
        match="PDF contains no extractable text",
    ):
        parse_pdf(pdf_bytes)
