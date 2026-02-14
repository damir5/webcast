"""Document conversion utilities: markdown to DOCX via pandoc."""

import subprocess
import tempfile
from pathlib import Path


def markdown_to_docx(markdown: str, output_path: Path) -> None:
    """Convert markdown string to DOCX using pandoc."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(markdown)
        md_path = Path(tmp.name)

    try:
        result = subprocess.run(
            ["pandoc", str(md_path), "-f", "markdown", "-t", "docx", "-o", str(output_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pandoc failed: {result.stderr}")
    finally:
        md_path.unlink(missing_ok=True)
