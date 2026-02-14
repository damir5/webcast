---
name: webcast
description: Convert URLs and local files to MP3 audio, markdown, or DOCX using local TTS. Use when asked to convert articles, web pages, or documents to audio or other formats.
---

# Webcast

Convert URLs and local files (txt/md/docx) to MP3 audio, markdown, or DOCX using local TTS on Apple Silicon.

## Commands

```bash
# Convert URL or local file to MP3 (Chatterbox by default)
webcast convert <url>                          # URL → MP3, auto-named in ./output/
webcast convert article.md                     # markdown → MP3
webcast convert notes.txt                      # plain text → MP3
webcast convert report.docx                    # DOCX → MP3
webcast convert <url> --model kokoro           # use Kokoro TTS
webcast convert <url> --ref-audio voice.wav    # clone a voice (Chatterbox)
webcast convert <url> -o episode.mp3           # custom output path

# Convert to other formats
webcast convert <url> --format md              # rich markdown (links, images, tables)
webcast convert <url> --format docx            # DOCX via pandoc
webcast convert <url> --format txt             # plain text extraction
webcast convert article.md --format docx       # markdown → DOCX

# Raw text-to-speech (stdin support)
webcast tts article.txt -o output.mp3          # from file
echo "Hello world" | webcast tts -o hello.mp3  # from stdin
webcast tts article.txt --ref-audio voice.wav  # clone a voice
webcast tts article.txt --model kokoro --voice af_bella  # use Kokoro
```

## Input Sources

| Type | Examples |
|------|----------|
| URL | `https://example.com/article` |
| Markdown | `article.md` |
| Plain text | `notes.txt` |
| Word doc | `report.docx` |
| stdin | `echo "text" \| webcast tts` (tts command only) |

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
| `--format` | `mp3` | Output: mp3, md, txt, docx |

## Agent Usage

Convert a blog post to MP3:
```
webcast convert https://example.com/blog-post
```

Convert a local markdown file to MP3:
```
webcast convert article.md
```

Convert with Kokoro and a specific voice:
```
webcast convert article.md --model kokoro --voice af_heart
```

Convert between document formats:
```
webcast convert https://example.com/blog-post --format md
webcast convert article.md --format docx
```

## Requirements

- macOS with Apple Silicon
- `ffmpeg` installed (`brew install ffmpeg`)
- `pandoc` installed (`brew install pandoc`) — for DOCX output and local file conversion
- First run downloads Chatterbox Turbo model (~1GB) or Kokoro model (~170MB)
