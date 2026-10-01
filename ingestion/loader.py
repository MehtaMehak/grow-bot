"""Load source documents (web pages and PDFs) and extract raw text."""

import io
import os
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def load_web_page(url):
    """Load a web page and extract text content.

    Returns (text, error). On success error is None.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = "\n".join(line for line in lines if line)

        if not text:
            return None, "No text content extracted from web page"

        return text, None
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def load_pdf(url):
    """Load a PDF and extract text content.

    Returns (text, error). On success error is None.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        text = "\n".join(text_parts).strip()

        if not text:
            return None, "No text content extracted from PDF"

        return text, None
    except requests.exceptions.RequestException as e:
        return None, f"Request failed: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def load_source(source_config):
    """Load a source based on its type.

    Args:
        source_config: dict with keys: url, source_type, scheme_name,
                       source_title, document_date (optional)

    Returns:
        (source_data, error). On success error is None.
        source_data contains: raw_text, source_url, source_type, scheme_name,
                             source_title, document_date
    """
    url = source_config["url"]
    source_type = source_config["source_type"]

    if source_type == "web_page":
        text, error = load_web_page(url)
    elif source_type == "pdf":
        text, error = load_pdf(url)
    else:
        text, error = None, f"Unknown source type: {source_type}"

    if error:
        return None, error

    return {
        "raw_text": text,
        "source_url": url,
        "source_type": source_type,
        "scheme_name": source_config["scheme_name"],
        "source_title": source_config["source_title"],
        "document_date": source_config.get("document_date"),
    }, None
