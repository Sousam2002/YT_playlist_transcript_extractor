import unittest
from dataclasses import dataclass

from transcript import TranscriptFetcher, join_transcript_segments


@dataclass
class Segment:
    text: str


class FakeTranscript:
    def __init__(self, language_code: str, text: str) -> None:
        self.language_code = language_code
        self._text = text

    def fetch(self) -> list[Segment]:
        return [Segment(self._text)]


class FakeTranscriptList(list[FakeTranscript]):
    def find_transcript(self, language_codes: list[str]) -> FakeTranscript:
        return next(item for item in self if item.language_code in language_codes)


class FakeApi:
    def __init__(self, transcripts: list[FakeTranscript]) -> None:
        self.transcripts = FakeTranscriptList(transcripts)

    def list(self, video_id: str) -> FakeTranscriptList:
        return self.transcripts


class FailingApi:
    def list(self, video_id: str) -> FakeTranscriptList:
        raise RuntimeError("network unavailable")


class JoinTranscriptSegmentsTests(unittest.TestCase):
    def test_joins_object_and_mapping_segments_without_timestamps(self) -> None:
        segments = [
            Segment("Hello\nworld"),
            {"text": "  from   captions  ", "start": 1.5, "duration": 2.0},
            Segment(""),
        ]

        self.assertEqual(
            join_transcript_segments(segments),
            "Hello world from captions",
        )


class TranscriptFetcherTests(unittest.TestCase):
    def test_prefers_english_transcript(self) -> None:
        fetcher = TranscriptFetcher(
            FakeApi(
                [
                    FakeTranscript("es", "Hola"),
                    FakeTranscript("en-US", "Hello"),
                ]
            )
        )

        self.assertEqual(fetcher.fetch("video").text, "Hello")

    def test_falls_back_to_first_available_language(self) -> None:
        fetcher = TranscriptFetcher(FakeApi([FakeTranscript("fr", "Bonjour")]))

        self.assertEqual(fetcher.fetch("video").text, "Bonjour")

    def test_returns_failure_instead_of_raising(self) -> None:
        result = TranscriptFetcher(FailingApi()).fetch("video")

        self.assertFalse(result.available)
        self.assertEqual(result.error, "network unavailable")


if __name__ == "__main__":
    unittest.main()
