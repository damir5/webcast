# Webcast

Convert web articles to MP3 audio, markdown, or DOCX using local TTS on Apple Silicon.

## Commands

```bash
# Extract article text from a URL
webcast extract <url>                          # stdout (plain text)
webcast extract <url> -o article.txt           # to file
webcast extract <url> --format md              # as markdown
webcast extract <url> --format json            # as JSON

# Convert text to speech (Chatterbox by default)
webcast tts article.txt -o output.mp3          # from file
echo "Hello world" | webcast tts -o hello.mp3  # from stdin
webcast tts article.txt --ref-audio voice.wav  # clone a voice
webcast tts article.txt --model kokoro --voice af_bella  # use Kokoro

# One-step: URL to MP3/markdown/DOCX
webcast convert <url>                          # MP3 (Chatterbox), auto-named in ./output/
webcast convert <url> --model kokoro           # MP3 with Kokoro
webcast convert <url> --format md              # rich markdown (links, images, tables)
webcast convert <url> --format docx            # DOCX via pandoc
webcast convert <url> -o episode.mp3           # custom output path

# Pipe: extract then speak
webcast extract <url> | webcast tts -o out.mp3
```

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
| `--format` (extract) | `txt` | Extract format: txt, json, md |
| `--format` (convert) | `mp3` | Convert format: mp3, md, docx |

## Agent Usage

To convert a blog post (uses Chatterbox by default):
```
webcast convert https://example.com/blog-post
```

To use Kokoro with a specific voice:
```
webcast convert https://example.com/blog-post --model kokoro --voice af_heart
```

To save as markdown or DOCX:
```
webcast convert https://example.com/blog-post --format md
webcast convert https://example.com/blog-post --format docx
```

## Requirements

- macOS with Apple Silicon
- `ffmpeg` installed (`brew install ffmpeg`)
- `pandoc` installed (`brew install pandoc`) — for DOCX output
- First run downloads Chatterbox Turbo model (~1GB) or Kokoro model (~170MB)
