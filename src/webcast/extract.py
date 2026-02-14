"""Article extraction from web pages using trafilatura."""

import json
from dataclasses import asdict, dataclass

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


def format_article(article: Article, fmt: str = "txt") -> str:
    """Format article for output."""
    if fmt == "json":
        return json.dumps(asdict(article), indent=2, ensure_ascii=False)
    elif fmt == "md":
        header = _markdown_header(article)
        return header + "\n" + article.text if header else article.text
    else:  # txt
        return article.text
