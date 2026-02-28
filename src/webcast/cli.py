"""CLI for webcast: text-to-speech only."""

import sys
from pathlib import Path

import click

from webcast.audio import generate_output_filename
from webcast.tts import DEFAULT_SPEED, DEFAULT_VOICE, ChatterboxTTS, KokoroTTS


@click.group()
def cli():
    """Convert text to listenable audio."""


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


def _run_tts(input_file: str | None, output: str | None, output_dir: str, model: str, ref_audio: str | None, voice: str, speed: float):
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
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output MP3 path")
@click.option("--output-dir", type=click.Path(), default="./output", help="Output directory (default: ./output)")
@click.option("--model", type=click.Choice(["chatterbox", "kokoro"]), default="chatterbox", help="TTS model")
@click.option("--ref-audio", type=click.Path(exists=True), default=None, help="Reference audio for Chatterbox voice cloning")
@click.option("--voice", default=DEFAULT_VOICE, help=f"Kokoro voice preset (default: {DEFAULT_VOICE})")
@click.option("--speed", default=DEFAULT_SPEED, type=float, help="Kokoro speed multiplier (default: 1.0)")
def tts(input_file: str | None, output: str | None, output_dir: str, model: str, ref_audio: str | None, voice: str, speed: float):
    """Convert text from stdin or a local file to MP3 audio."""
    _run_tts(input_file, output, output_dir, model, ref_audio, voice, speed)


@cli.command()
@click.argument("input_file", required=False, type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output MP3 path")
@click.option("--output-dir", type=click.Path(), default="./output", help="Output directory (default: ./output)")
@click.option("--model", type=click.Choice(["chatterbox", "kokoro"]), default="chatterbox", help="TTS model")
@click.option("--ref-audio", type=click.Path(exists=True), default=None, help="Reference audio for Chatterbox voice cloning")
@click.option("--voice", default=DEFAULT_VOICE, help=f"Kokoro voice preset (default: {DEFAULT_VOICE})")
@click.option("--speed", default=DEFAULT_SPEED, type=float, help="Kokoro speed multiplier (default: 1.0)")
def speak(input_file: str | None, output: str | None, output_dir: str, model: str, ref_audio: str | None, voice: str, speed: float):
    """Alias for tts."""
    _run_tts(input_file, output, output_dir, model, ref_audio, voice, speed)
