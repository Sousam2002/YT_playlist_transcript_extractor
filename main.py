"""Command-line entry point for playlist transcript extraction."""

import argparse
import re
import sys

from document import write_markdown
from playlist import extract_playlist
from transcript import TranscriptFetcher, TranscriptResult


def _parse_range(value: str) -> str:
    if value.isdigit():
        if int(value) < 1:
            raise argparse.ArgumentTypeError("range positions must be 1 or greater")
        return value

    match = re.fullmatch(r"(\d*)-(\d*)", value)
    if not match or not any(match.groups()):
        raise argparse.ArgumentTypeError(
            "use N, START-END, START-, or -END (for example, 5-12)"
        )

    start_text, end_text = match.groups()
    start = int(start_text) if start_text else None
    end = int(end_text) if end_text else None
    if start == 0 or end == 0:
        raise argparse.ArgumentTypeError("range positions must be 1 or greater")
    if start is not None and end is not None and start > end:
        raise argparse.ArgumentTypeError("range start cannot be greater than its end")
    return f"{start_text}:{end_text}"


def _clean_url(value: str) -> str:
    value = value.strip()
    markdown_link = re.fullmatch(r"\[[^]]*\]\((https?://[^)]+)\)", value)
    if markdown_link:
        value = markdown_link.group(1)
    return value.replace(r"\&", "&")


def _arguments(arguments: list[str] | None = None) -> tuple[str, str | None]:
    parser = argparse.ArgumentParser(
        description="Export YouTube captions to one Markdown file."
    )
    parser.add_argument(
        "youtube_url",
        nargs="?",
        help="YouTube playlist or video URL",
    )
    parser.add_argument(
        "--range",
        dest="playlist_range",
        type=_parse_range,
        metavar="SELECTION",
        help="playlist positions: N, START-END, START-, or -END",
    )
    args = parser.parse_args(arguments)
    url = args.youtube_url or input("YouTube playlist or video URL: ").strip()
    if not url:
        parser.error("a YouTube playlist or video URL is required")
    return _clean_url(url), args.playlist_range


def run(youtube_url: str, playlist_range: str | None = None) -> int:
    try:
        playlist = extract_playlist(youtube_url, playlist_range)
    except Exception as exc:
        print(f"Error: could not extract YouTube URL: {exc}", file=sys.stderr)
        return 1

    print(f"Found {len(playlist.videos)} video(s) in: {playlist.title}")
    fetcher = TranscriptFetcher()
    results: list[TranscriptResult] = []

    for number, video in enumerate(playlist.videos, start=1):
        print(f"[{number}/{len(playlist.videos)}] {video.title}")
        result = fetcher.fetch(video.id)
        if not result.available:
            print(f"  Transcript unavailable: {result.error}", file=sys.stderr)
        results.append(result)

    try:
        output_path = write_markdown(playlist, results)
    except OSError as exc:
        print(f"Error: could not write output: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote transcript document to {output_path.resolve()}")
    return 0


def main() -> int:
    try:
        youtube_url, playlist_range = _arguments()
        return run(youtube_url, playlist_range)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
