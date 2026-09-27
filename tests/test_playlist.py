import unittest
from unittest.mock import patch

from playlist import extract_playlist


class FakeYoutubeDL:
    response: dict = {}
    options: dict = {}

    def __init__(self, options: dict) -> None:
        type(self).options = options

    def __enter__(self) -> "FakeYoutubeDL":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def extract_info(self, url: str, download: bool) -> dict:
        return type(self).response


class ExtractPlaylistTests(unittest.TestCase):
    @patch("playlist.yt_dlp.YoutubeDL", FakeYoutubeDL)
    def test_passes_range_to_yt_dlp_and_preserves_selected_order(self) -> None:
        FakeYoutubeDL.response = {
            "title": "Playlist",
            "entries": [
                {"id": "two", "title": "Second", "url": "two"},
                {"id": "three", "title": "Third", "url": "three"},
            ],
        }

        result = extract_playlist("https://youtube.test/playlist", "2:3")

        self.assertEqual(FakeYoutubeDL.options["playlist_items"], "2:3")
        self.assertEqual([video.id for video in result.videos], ["two", "three"])

    @patch("playlist.yt_dlp.YoutubeDL", FakeYoutubeDL)
    def test_accepts_a_standalone_video(self) -> None:
        FakeYoutubeDL.response = {
            "id": "video-id",
            "title": "Standalone",
            "webpage_url": "https://youtube.test/watch?v=video-id",
        }

        result = extract_playlist("https://youtube.test/watch?v=video-id")

        self.assertEqual(result.title, "Standalone")
        self.assertEqual(len(result.videos), 1)
        self.assertEqual(result.videos[0].id, "video-id")

    @patch("playlist.yt_dlp.YoutubeDL", FakeYoutubeDL)
    def test_rejects_range_for_standalone_video(self) -> None:
        FakeYoutubeDL.response = {"id": "video-id", "title": "Standalone"}

        with self.assertRaisesRegex(ValueError, "playlist URL"):
            extract_playlist("https://youtube.test/watch?v=video-id", "1")


if __name__ == "__main__":
    unittest.main()
