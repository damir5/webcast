# Webcast

Convert web articles to listenable MP3 audio, markdown, or DOCX using local TTS (Kokoro on Apple Silicon).

## Commands

```bash
# Extract article text from a URL
webcast extract <url>                          # stdout (plain text)
webcast extract <url> -o article.txt           # to file
webcast extract <url> --format md              # as markdown
webcast extract <url> --format json            # as JSON

# Convert text to speech
webcast tts article.txt -o output.mp3          # from file
echo "Hello world" | webcast tts -o hello.mp3  # from stdin
webcast tts article.txt --voice af_bella       # different voice

# One-step: URL to MP3/markdown/DOCX
webcast convert <url>                          # MP3 (default), auto-named in ./output/
webcast convert <url> --format md              # rich markdown (links, images, tables)
webcast convert <url> --format docx            # DOCX via pandoc
webcast convert <url> -o episode.mp3           # custom output path

# Pipe: extract then speak
webcast extract <url> | webcast tts -o out.mp3
```

## Voice Options

American English:
- `af_heart` (default), `af_bella`, `af_nova` — female
- `am_adam`, `am_echo` — male

British English:
- `bf_alice`, `bf_emma` — female
- `bm_daniel`, `bm_george` — male

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--voice` | `af_heart` | Voice preset |
| `--speed` | `1.0` | Speed multiplier (0.5–2.0) |
| `--output-dir` | `./output` | Default output directory |
| `-o, --output` | auto | Output file path |
| `--format` (extract) | `txt` | Extract format: txt, json, md |
| `--format` (convert) | `mp3` | Convert format: mp3, md, docx |

## Agent Usage

To convert a blog post for a user:
```
webcast convert https://example.com/blog-post --voice af_heart
```

To save as markdown or DOCX:
```
webcast convert https://example.com/blog-post --format md
webcast convert https://example.com/blog-post --format docx
```

To extract and review text before converting:
```
webcast extract https://example.com/blog-post -o /tmp/article.txt
# review/edit the text...
webcast tts /tmp/article.txt -o podcast.mp3
```

## Requirements

- macOS with Apple Silicon
- `ffmpeg` installed (`brew install ffmpeg`)
- `pandoc` installed (`brew install pandoc`) — for DOCX output
- First run downloads ~170MB Kokoro model
