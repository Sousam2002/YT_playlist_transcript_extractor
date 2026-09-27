"""Markdown rendering and output file writing."""

from collections.abc import Sequence
from pathlib import Path

from playlist import Playlist
from transcript import TranscriptResult


UNAVAILABLE_MESSAGE = "> Transcript unavailable for this video."


def _single_line(value: str) -> str:
    return " ".join(value.split())


def render_markdown(
    playlist: Playlist,
    transcripts: Sequence[TranscriptResult],
) -> str:
    if len(playlist.videos) != len(transcripts):
        raise ValueError("Each video must have one transcript result.")

    sections = [f"# {_single_line(playlist.title)}"]
    for number, (video, transcript) in enumerate(
        zip(playlist.videos, transcripts), start=1
    ):
        url_line = (
            f"URL: {video.url}" if video.url else "URL: Unavailable"
        )
        body = transcript.text if transcript.available else UNAVAILABLE_MESSAGE
        sections.append(
            "\n".join(
                [
                    f"## {number}. {_single_line(video.title)}",
                    "",
                    url_line,
                    "",
                    body or UNAVAILABLE_MESSAGE,
                ]
            )
        )

    return "\n\n---\n\n".join(sections) + "\n"


def write_markdown(
    playlist: Playlist,
    transcripts: Sequence[TranscriptResult],
    output_path: Path = Path("output/playlist_transcript.md"),
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_markdown(playlist, transcripts),
        encoding="utf-8",
    )
    return output_path
