"""Audio utilities: WAV to MP3 conversion, filename generation."""

import re
import subprocess
from pathlib import Path


def wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    """Convert WAV to MP3 using ffmpeg."""
    mp3_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")


def generate_output_filename(title: str | None, output_dir: Path, ext: str = "mp3") -> Path:
    """Generate a sanitized filename from an article title."""
    if not title:
        title = "untitled"
    # Lowercase, replace non-alphanum with hyphens, collapse multiples, strip edges
    name = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not name:
        name = "untitled"
    # Truncate to reasonable length
    name = name[:80].rstrip("-")
    return output_dir / f"{name}.{ext}"
