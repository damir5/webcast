# webcast

Local text-to-speech on Apple Silicon.

## Usage

```bash
./webcast tts article.txt -o output.mp3
echo "Hello world" | ./webcast tts -o hello.mp3
./webcast speak notes.md --model kokoro --voice af_bella -o notes.mp3
```

`webcast` is now TTS-only. Use `source-extract` for article extraction and document normalization.

## Voice sample helper

```bash
uvx yt-dlp --extract-audio --audio-format wav --downloader ffmpeg --downloader-args "ffmpeg:-ss 00:01:00 -to 00:01:20" <url>
```
