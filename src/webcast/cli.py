"""CLI for webcast: extract articles and convert to audio/markdown/docx."""

import sys
from pathlib import Path

import click

from webcast.audio import generate_output_filename
from webcast.extract import extract_article, extract_markdown, format_article
from webcast.tts import DEFAULT_SPEED, DEFAULT_VOICE, ChatterboxTTS, KokoroTTS


@click.group()
def cli():
    """Convert web articles to listenable audio."""


@cli.command()
@click.argument("url")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output file (default: stdout)")
@click.option("--format", "fmt", type=click.Choice(["txt", "json", "md"]), default="txt")
def extract(url: str, output: str | None, fmt: str):
    """Extract article text from a URL."""
    article = extract_article(url)
    text = format_article(article, fmt)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        click.echo(f"Saved to {output}", err=True)
    else:
        click.echo(text)


def _make_engine(model: str, ref_audio: str | None, voice: str, speed: float):
    """Create TTS engine and build a status message."""
    if model == "kokoro":
        engine = KokoroTTS()
        msg = f"Generating audio with Kokoro (voice={voice}, speed={speed})..."
        return engine, msg, {"voice": voice, "speed": speed}
    else:
        engine = ChatterboxTTS(ref_audio=ref_audio)
        parts = ["Generating audio with Chatterbox"]
        if ref_audio:
            parts[0] += f" (ref={Path(ref_audio).name})"
        msg = parts[0] + "..."
        return engine, msg, {}


@cli.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output MP3 path")
@click.option("--output-dir", type=click.Path(), default="./output", help="Output directory (default: ./output)")
@click.option("--model", type=click.Choice(["chatterbox", "kokoro"]), default="chatterbox", help="TTS model")
@click.option("--ref-audio", type=click.Path(exists=True), default=None, help="Reference audio for Chatterbox voice cloning")
@click.option("--voice", default=DEFAULT_VOICE, help=f"Kokoro voice preset (default: {DEFAULT_VOICE})")
@click.option("--speed", default=DEFAULT_SPEED, type=float, help="Kokoro speed multiplier (default: 1.0)")
def tts(input_file: str | None, output: str | None, output_dir: str, model: str, ref_audio: str | None, voice: str, speed: float):
    """Convert text to MP3 audio. Reads from file or stdin."""
    if input_file:
        text = Path(input_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        raise click.UsageError("Provide an input file or pipe text via stdin.")

    if not text.strip():
        raise click.UsageError("Input text is empty.")

    if output:
        mp3_path = Path(output)
    else:
        mp3_path = generate_output_filename(None, Path(output_dir))

    engine, msg, kwargs = _make_engine(model, ref_audio, voice, speed)
    click.echo(msg, err=True)
    engine.text_to_mp3(text, mp3_path, **kwargs)
    click.echo(f"Saved to {mp3_path}", err=True)


@cli.command()
@click.argument("url")
@click.option("-o", "--output", type=click.Path(), default=None, help="Output path")
@click.option("--output-dir", type=click.Path(), default="./output", help="Output directory (default: ./output)")
@click.option(
    "--format", "fmt",
    type=click.Choice(["mp3", "md", "docx"]),
    default="mp3",
    help="Output format (default: mp3)",
)
@click.option("--model", type=click.Choice(["chatterbox", "kokoro"]), default="chatterbox", help="TTS model")
@click.option("--ref-audio", type=click.Path(exists=True), default=None, help="Reference audio for Chatterbox voice cloning")
@click.option("--voice", default=DEFAULT_VOICE, help=f"Kokoro voice preset (default: {DEFAULT_VOICE})")
@click.option("--speed", default=DEFAULT_SPEED, type=float, help="Kokoro speed multiplier (default: 1.0)")
def convert(url: str, output: str | None, output_dir: str, fmt: str, model: str, ref_audio: str | None, voice: str, speed: float):
    """Extract article from URL and convert to MP3, markdown, or DOCX."""
    click.echo(f"Extracting article from {url}...", err=True)

    if fmt in ("md", "docx"):
        article, markdown = extract_markdown(url)
    else:
        article = extract_article(url)

    click.echo(f"Title: {article.title}", err=True)

    if fmt == "md":
        if output:
            out_path = Path(output)
        else:
            out_path = generate_output_filename(article.title, Path(output_dir), ext="md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        click.echo(f"Saved to {out_path}", err=True)

    elif fmt == "docx":
        from webcast.document import markdown_to_docx

        if output:
            out_path = Path(output)
        else:
            out_path = generate_output_filename(article.title, Path(output_dir), ext="docx")
        click.echo("Converting to DOCX via pandoc...", err=True)
        markdown_to_docx(markdown, out_path)
        click.echo(f"Saved to {out_path}", err=True)

    else:  # mp3
        if output:
            mp3_path = Path(output)
        else:
            mp3_path = generate_output_filename(article.title, Path(output_dir))
        engine, msg, kwargs = _make_engine(model, ref_audio, voice, speed)
        click.echo(msg, err=True)
        engine.text_to_mp3(article.text, mp3_path, **kwargs)
        click.echo(f"Saved to {mp3_path}", err=True)
