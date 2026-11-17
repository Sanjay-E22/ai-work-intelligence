import pymupdf


def parse_text(content: bytes) -> str:
    """
    WHY: Convert uploaded UTF-8 text bytes into clean text.
    ARGS: content - raw bytes from a text file.
    RETURN: Normalized, non-empty text.
    RAISE: ValueError if the content is empty or invalid.
    """
    if not content:
        raise ValueError("Content cannot be empty")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError("Content must be valid UTF-8") from e

    text = text.strip()

    if not text:
        raise ValueError("Content cannot contain only whitespace")

    return text


def parse_pdf(content: bytes) -> str:
    """
    WHY: Extract readable text from an uploaded PDF.
    ARGS: content - raw bytes of the PDF file.
    RETURN: Normalized, non-empty text extracted from the PDF.
    RAISE: ValueError if the PDF is invalid or contains no extractable text.
    """
    if not content:
        raise ValueError("PDF content cannot be empty")

    try:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            text = "\n".join(page.get_text() for page in document)
    except Exception as e:
        raise ValueError("Unable to read the PDF") from e

    text = text.strip()

    if not text:
        raise ValueError("PDF contains no extractable text")

    return text
