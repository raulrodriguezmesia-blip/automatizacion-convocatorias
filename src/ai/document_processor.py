"""
Document Processor for Convocatoria AI Engine
Extracts structured data from convocatoria documents (PDF, DOCX, plain text).
"""

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports to avoid hard dependency at import time
try:
    import docx
    import pdfminer.high_level
    import spacy

    _NLP_AVAILABLE = True
except ImportError:
    _NLP_AVAILABLE = False
    logger.warning("pdfminer/docx/spacy not installed - document processing limited to .txt")


def _load_nlp():
    if not _NLP_AVAILABLE:
        return None
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download

        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


_nlp = None


def extract_text_from_pdf(file_path: str) -> str:
    if not _NLP_AVAILABLE:
        return ""
    try:
        return pdfminer.high_level.extract_text(file_path)
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    if not _NLP_AVAILABLE:
        return ""
    try:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX {file_path}: {e}")
        return ""


def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".doc", ".docx"]:
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    logger.warning(f"Unsupported file type: {ext}")
    return ""


def extract_entities(text: str) -> dict[str, Any]:
    global _nlp
    if _nlp is None:
        _nlp = _load_nlp()

    entities: dict[str, Any] = {
        "title": None,
        "date": None,
        "time": None,
        "location": None,
        "organizer": None,
        "attendees": [],
        "description": None,
        "requirements": [],
    }

    date_patterns = [
        r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b",
        r"\b(\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})\b",
    ]
    time_pattern = r"\b(\d{1,2}:\d{2}\s*(?:AM|PM)?)\b"
    email_pattern = r"\b[\w\.-]+@[\w\.-]+\.\w+\b"

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            entities["date"] = match.group(0)
            break

    time_match = re.search(time_pattern, text, re.IGNORECASE)
    if time_match:
        entities["time"] = time_match.group(0)

    emails = re.findall(email_pattern, text)
    if emails:
        entities["attendees"] = list(set(emails))

    if _nlp is not None:
        doc = _nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG" and not entities["organizer"]:
                entities["organizer"] = ent.text
            elif ent.label_ == "GPE" and not entities["location"]:
                entities["location"] = ent.text
            elif ent.label_ == "DATE" and not entities["date"]:
                entities["date"] = ent.text
            elif ent.label_ == "TIME" and not entities["time"]:
                entities["time"] = ent.text

    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for line in lines[:10]:
        if (
            len(line) < 120
            and not re.search(date_patterns[0], line, re.I)
            and not re.search(time_pattern, line, re.I)
        ):
            entities["title"] = line
            break

    desc_keywords = ["objective", "purpose", "description", "about", "aim"]
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in desc_keywords):
            entities["description"] = " ".join(lines[i : i + 3]).strip()
            break

    req_lines = [
        line.strip()
        for line in lines
        if re.search(r"\bmust\b|\bshould\b|\brequire\b|\bobligatorio\b", line, re.I)
    ]
    if req_lines:
        entities["requirements"] = req_lines[:5]

    return entities


def process_document(file_path: str) -> dict[str, Any]:
    """Main entry point: extract text and entities."""
    text = extract_text_from_file(file_path)
    if not text:
        return {"error": "Could not extract text from document"}
    entities = extract_entities(text)
    return {
        "raw_text": text[:500],
        "entities": entities,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python document_processor.py <path_to_document>")
        sys.exit(1)
    result = process_document(sys.argv[1])
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
