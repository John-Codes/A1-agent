from pathlib import Path


def read_document(path_text):
    path = Path(path_text).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    if path.suffix.lower() in {".txt", ".md"}:
        return path, path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        return path, _read_pdf(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _read_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("Install pypdf to ingest PDFs.") from exc
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()
