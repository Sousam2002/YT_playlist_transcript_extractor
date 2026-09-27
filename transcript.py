"""Caption retrieval and plain-text conversion."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi


@dataclass(frozen=True)
class TranscriptResult:
    text: str | None
    error: str | None = None

    @property
    def available(self) -> bool:
        return self.text is not None


def join_transcript_segments(segments: Iterable[Any]) -> str:
    """Join caption segments as normalized continuous text."""
    parts: list[str] = []
    for segment in segments:
        if isinstance(segment, Mapping):
            value = segment.get("text", "")
        else:
            value = getattr(segment, "text", "")

        text = " ".join(str(value).split())
        if text:
            parts.append(text)
    return " ".join(parts)


class TranscriptFetcher:
    def __init__(self, api: Any | None = None) -> None:
        self._api = api or YouTubeTranscriptApi()

    def fetch(self, video_id: str | None) -> TranscriptResult:
        if not video_id:
            return TranscriptResult(None, "No video ID is available.")

        try:
            transcript_list = self._api.list(video_id)
            transcripts = list(transcript_list)
            if not transcripts:
                return TranscriptResult(None, "No transcripts are available.")

            english_codes = [
                item.language_code
                for item in transcripts
                if item.language_code.lower() == "en"
                or item.language_code.lower().startswith("en-")
            ]
            selected = (
                transcript_list.find_transcript(english_codes)
                if english_codes
                else transcripts[0]
            )
            text = join_transcript_segments(selected.fetch())
            if not text:
                return TranscriptResult(None, "The transcript is empty.")
            return TranscriptResult(text)
        except Exception as exc:
            return TranscriptResult(None, str(exc) or exc.__class__.__name__)
