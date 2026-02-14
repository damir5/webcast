"""Record a reference audio sample for Chatterbox voice cloning.

Usage: uv run python record_voice.py [-o output.wav] [-d 15]

Read the displayed text clearly in a quiet room. Press Ctrl+C to stop early.
"""

import argparse
import re
import subprocess
import sys


SAMPLE_TEXT = """
The morning light filtered through the tall windows, casting long shadows
across the wooden floor. She picked up her coffee and walked to the balcony,
watching the city slowly come alive below. The streets were still quiet, but
she could hear the distant hum of traffic building, a familiar rhythm that
marked the start of another day.
""".strip()


def list_audio_devices() -> list[tuple[int, str]]:
    """List available audio input devices via ffmpeg."""
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True,
        text=True,
    )
    devices = []
    in_audio = False
    for line in result.stderr.splitlines():
        if "audio devices" in line.lower():
            in_audio = True
            continue
        if in_audio:
            m = re.search(r"\[(\d+)] (.+)", line)
            if m:
                devices.append((int(m.group(1)), m.group(2).strip()))
            else:
                break
    return devices


def select_microphone() -> int:
    """Show mic selection menu and return device index."""
    devices = list_audio_devices()
    if not devices:
        print("No audio devices found.")
        sys.exit(1)

    if len(devices) == 1:
        print(f"Using: {devices[0][1]}\n")
        return devices[0][0]

    print("Microphones:")
    for i, (idx, name) in enumerate(devices, 1):
        print(f"  {i}) {name}")
    print()

    while True:
        try:
            choice = input(f"Select microphone [1-{len(devices)}]: ").strip()
            n = int(choice)
            if 1 <= n <= len(devices):
                print(f"Using: {devices[n - 1][1]}\n")
                return devices[n - 1][0]
        except (ValueError, EOFError):
            pass
        print(f"Enter a number between 1 and {len(devices)}")


def main():
    parser = argparse.ArgumentParser(description="Record reference audio for voice cloning")
    parser.add_argument("-o", "--output", default="ref_voice.wav", help="Output WAV path")
    parser.add_argument("-d", "--duration", type=int, default=15, help="Recording duration in seconds")
    args = parser.parse_args()

    print("=== Voice Reference Recording ===\n")

    device_idx = select_microphone()

    print("Read this text clearly and naturally:\n")
    print(f"  \"{SAMPLE_TEXT}\"\n")
    print(f"Recording {args.duration}s to {args.output}")
    print("Press Enter to start, Ctrl+C to cancel...")

    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)

    print(f"Recording for {args.duration} seconds...")

    # Try sox first, fall back to ffmpeg
    recorded = False
    for cmd in [
        ["sox", "-d", "-r", "24000", "-c", "1", "-b", "16", args.output, "trim", "0", str(args.duration)],
        ["ffmpeg", "-y", "-f", "avfoundation", "-i", f":{device_idx}", "-ar", "24000", "-ac", "1", "-t", str(args.duration), args.output],
    ]:
        try:
            subprocess.run(cmd, check=True)
            recorded = True
            break
        except FileNotFoundError:
            continue
        except subprocess.CalledProcessError:
            continue

    if not recorded:
        print("Recording failed. Install sox (`brew install sox`) or check ffmpeg audio input.")
        print(f"Or record manually and convert:\n  ffmpeg -i recording.m4a -ar 24000 -ac 1 {args.output}")
        sys.exit(1)

    print(f"Saved to {args.output}")
    print(f"\nUsage: ./webcast convert <url> --ref-audio {args.output}")


if __name__ == "__main__":
    main()
