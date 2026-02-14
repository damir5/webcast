"""Text-to-speech using mlx-audio (Chatterbox or Kokoro)."""

import re
import tempfile
from collections.abc import Iterator
from pathlib import Path

import numpy as np

CHATTERBOX_MODEL_ID = "mlx-community/chatterbox-turbo-fp16"
KOKORO_MODEL_ID = "mlx-community/Kokoro-82M-bf16"

DEFAULT_VOICE = "af_heart"
DEFAULT_SPEED = 1.0
MAX_CHUNK_CHARS = 500


def chunk_text(text: str) -> list[str]:
    """Split text into chunks on sentence boundaries, up to ~MAX_CHUNK_CHARS each."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks = []
    current = ""

    for sentence in sentences:
        if not sentence:
            continue
        if current and len(current) + len(sentence) + 1 > MAX_CHUNK_CHARS:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


class ChatterboxTTS:
    """Wrapper around mlx-audio Chatterbox Turbo model."""

    def __init__(self, ref_audio: str | None = None):
        self._model = None
        self._sample_rate = 24000
        self._ref_audio = ref_audio

    def _load(self):
        if self._model is None:
            from mlx_audio.tts.utils import load_model

            self._model = load_model(CHATTERBOX_MODEL_ID)

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    def generate_chunks(self, text: str) -> Iterator[np.ndarray]:
        """Generate audio arrays for each text chunk."""
        self._load()
        chunks = chunk_text(text)

        for chunk in chunks:
            for result in self._model.generate(
                text=chunk,
                ref_audio=self._ref_audio,
                lang_code="en",
            ):
                audio = np.array(result.audio, dtype=np.float32)
                self._sample_rate = result.sample_rate
                yield audio

    def text_to_mp3(self, text: str, output_path: Path) -> Path:
        """Full pipeline: text -> chunked TTS -> concat -> wav -> mp3."""
        import soundfile as sf

        from webcast.audio import wav_to_mp3

        segments = list(self.generate_chunks(text))
        if not segments:
            raise RuntimeError("No audio generated")

        audio = np.concatenate(segments)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)
            sf.write(str(wav_path), audio, self.sample_rate)

        try:
            wav_to_mp3(wav_path, output_path)
        finally:
            wav_path.unlink(missing_ok=True)

        return output_path


class KokoroTTS:
    """Wrapper around mlx-audio Kokoro model."""

    def __init__(self):
        self._model = None
        self._sample_rate = 24000

    def _load(self):
        if self._model is None:
            from mlx_audio.tts.utils import load_model

            self._model = load_model(KOKORO_MODEL_ID)

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    def generate_chunks(
        self,
        text: str,
        voice: str = DEFAULT_VOICE,
        speed: float = DEFAULT_SPEED,
    ) -> Iterator[np.ndarray]:
        """Generate audio arrays for each text chunk."""
        self._load()
        chunks = chunk_text(text)

        for chunk in chunks:
            for result in self._model.generate(
                text=chunk, voice=voice, speed=speed, lang_code="a"
            ):
                audio = np.array(result.audio, dtype=np.float32)
                self._sample_rate = result.sample_rate
                yield audio

    def text_to_mp3(
        self,
        text: str,
        output_path: Path,
        voice: str = DEFAULT_VOICE,
        speed: float = DEFAULT_SPEED,
    ) -> Path:
        """Full pipeline: text -> chunked TTS -> concat -> wav -> mp3."""
        import soundfile as sf

        from webcast.audio import wav_to_mp3

        segments = list(self.generate_chunks(text, voice, speed))
        if not segments:
            raise RuntimeError("No audio generated")

        audio = np.concatenate(segments)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)
            sf.write(str(wav_path), audio, self.sample_rate)

        try:
            wav_to_mp3(wav_path, output_path)
        finally:
            wav_path.unlink(missing_ok=True)

        return output_path
