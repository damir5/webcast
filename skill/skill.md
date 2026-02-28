---
name: webcast
description: Convert text from stdin or local files to MP3 audio using local TTS. Use when asked to generate speech audio from prepared text, summaries, notes, or transcripts.
---

# Webcast

Convert text from stdin or local files to MP3 audio using local TTS on Apple Silicon.

## Commands

```bash
webcast tts article.txt -o output.mp3          # from file
echo "Hello world" | webcast tts -o hello.mp3  # from stdin
webcast tts article.txt --ref-audio voice.wav  # clone a voice
webcast tts article.txt --model kokoro --voice af_bella  # use Kokoro
webcast speak article.txt -o output.mp3        # alias for tts
```

## Input Sources

| Type | Examples |
|------|----------|
| Markdown | `article.md` |
| Plain text | `notes.txt` |
| stdin | `echo "text" \| webcast tts` |

## TTS Models

### Chatterbox (default)
- Expressive, natural-sounding speech
- Voice cloning via `--ref-audio <wav>` (5+ seconds of reference audio)
- Uses default voice when no reference audio provided

### Kokoro
- Fast, lightweight (82M params)
- Named voice presets via `--voice`
- Speed control via `--speed`

## Kokoro Voice Presets

American English:
- `af_heart` (default), `af_bella`, `af_nova` — female
- `am_adam`, `am_echo` — male

British English:
- `bf_alice`, `bf_emma` — female
- `bm_daniel`, `bm_george` — male

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `chatterbox` | TTS model: chatterbox, kokoro |
| `--ref-audio` | — | Reference audio for Chatterbox voice cloning |
| `--voice` | `af_heart` | Kokoro voice preset |
| `--speed` | `1.0` | Kokoro speed multiplier (0.5–2.0) |
| `--output-dir` | `./output` | Default output directory |
| `-o, --output` | auto | Output file path |

## Agent Usage

Convert a summary file to MP3:
```
webcast tts summary.txt -o summary.mp3
```

Convert stdin to MP3:
```
echo "hello" | webcast tts -o hello.mp3
```

Convert with Kokoro and a specific voice:
```
webcast tts article.md --model kokoro --voice af_heart
```

## Requirements

- macOS with Apple Silicon
- `ffmpeg` installed (`brew install ffmpeg`)
- First run downloads Chatterbox Turbo model (~1GB) or Kokoro model (~170MB)
