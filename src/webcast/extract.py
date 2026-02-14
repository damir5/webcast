"""Article extraction from web pages and local files."""

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import trafilatura


@dataclass
class Article:
    title: str | None
    author: str | None
    date: str | None
    text: str
    url: str


def _fetch_and_extract(url: str) -> tuple[str, dict]:
    """Fetch URL and extract metadata via trafilatura JSON output.

    Returns (downloaded_html, metadata_dict).
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded is None:
        raise RuntimeError(f"Failed to fetch URL: {url}")

    result = trafilatura.extract(
        downloaded, output_format="json", include_comments=False, with_metadata=True
    )
    if result is None:
        raise RuntimeError(f"Failed to extract article from: {url}")

    data = json.loads(result)
    if not data.get("text", "").strip():
        raise RuntimeError(f"No text content extracted from: {url}")

    return downloaded, data


def _article_from_data(data: dict, url: str) -> Article:
    return Article(
        title=data.get("title"),
        author=data.get("author"),
        date=data.get("date"),
        text=data.get("text", "").strip(),
        url=url,
    )


def extract_article(url: str) -> Article:
    """Fetch and extract article content from a URL."""
    _, data = _fetch_and_extract(url)
    return _article_from_data(data, url)


def _markdown_header(article: Article) -> str:
    """Build markdown header with title and metadata."""
    parts = []
    if article.title:
        parts.append(f"# {article.title}")
    meta = []
    if article.author:
        meta.append(f"By {article.author}")
    if article.date:
        meta.append(article.date)
    if meta:
        parts.append(" | ".join(meta))
    if parts:
        parts.append("")
    return "\n\n".join(parts)


def extract_markdown(url: str) -> tuple[Article, str]:
    """Fetch and extract article as rich markdown.

    Returns (Article, markdown_string) where markdown preserves
    headings, links, images, tables, and emphasis from the source.
    """
    downloaded, data = _fetch_and_extract(url)
    article = _article_from_data(data, url)

    markdown = trafilatura.extract(
        downloaded,
        output_format="markdown",
        include_comments=False,
        include_links=True,
        include_images=True,
        include_tables=True,
    )
    if not markdown:
        raise RuntimeError(f"Failed to extract markdown from: {url}")

    header = _markdown_header(article)
    if header:
        markdown = header + "\n" + markdown

    return article, markdown


def _title_from_path(path: Path) -> str:
    """Derive a title from a file path."""
    return path.stem.replace("-", " ").replace("_", " ").strip()


def _pandoc_convert(path: Path, to_fmt: str) -> str:
    """Convert a file using pandoc."""
    result = subprocess.run(
        ["pandoc", str(path), "-t", to_fmt],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr}")
    return result.stdout.strip()


def _pandoc_convert_text(text: str, from_fmt: str, to_fmt: str) -> str:
    """Convert text content using pandoc via stdin."""
    result = subprocess.run(
        ["pandoc", "-f", from_fmt, "-t", to_fmt],
        input=text, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr}")
    return result.stdout.strip()


def extract_from_file(path: Path) -> tuple[Article, str | None]:
    """Extract article content from a local file.

    Returns (Article, markdown_or_none). Markdown is returned for .md and .docx
    inputs; None for .txt.
    """
    suffix = path.suffix.lower()

    if suffix == ".txt":
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise RuntimeError(f"File is empty: {path}")
        return Article(
            title=_title_from_path(path), author=None, date=None,
            text=text, url=str(path),
        ), None

    elif suffix == ".md":
        markdown = path.read_text(encoding="utf-8").strip()
        if not markdown:
            raise RuntimeError(f"File is empty: {path}")
        plain = _pandoc_convert_text(markdown, "markdown", "plain")
        return Article(
            title=_title_from_path(path), author=None, date=None,
            text=plain, url=str(path),
        ), markdown

    elif suffix == ".docx":
        text = _pandoc_convert(path, "plain")
        if not text:
            raise RuntimeError(f"No text extracted from: {path}")
        markdown = _pandoc_convert(path, "markdown")
        return Article(
            title=_title_from_path(path), author=None, date=None,
            text=text, url=str(path),
        ), markdown

    else:
        raise RuntimeError(f"Unsupported file type: {suffix} (expected .txt, .md, or .docx)")


def format_article(article: Article, fmt: str = "txt") -> str:
    """Format article for output."""
    if fmt == "json":
        return json.dumps(asdict(article), indent=2, ensure_ascii=False)
    elif fmt == "md":
        header = _markdown_header(article)
        return header + "\n" + article.text if header else article.text
    else:  # txt
        return article.text
