import unittest

from document import UNAVAILABLE_MESSAGE, render_markdown
from playlist import Playlist, Video
from transcript import TranscriptResult


class RenderMarkdownTests(unittest.TestCase):
    def test_renders_ordered_sections_and_unavailable_placeholder(self) -> None:
        playlist = Playlist(
            title="Example Playlist",
            videos=[
                Video("one", "First Video", "https://youtu.be/one"),
                Video("two", "Second Video", "https://youtu.be/two"),
            ],
        )
        results = [
            TranscriptResult("First transcript."),
            TranscriptResult(None, "Captions disabled"),
        ]

        markdown = render_markdown(playlist, results)

        self.assertIn("# Example Playlist", markdown)
        self.assertIn("## 1. First Video", markdown)
        self.assertIn("URL: https://youtu.be/one", markdown)
        self.assertIn("First transcript.", markdown)
        self.assertIn("## 2. Second Video", markdown)
        self.assertIn(UNAVAILABLE_MESSAGE, markdown)
        self.assertIn("\n\n---\n\n", markdown)
        self.assertLess(
            markdown.index("## 1. First Video"),
            markdown.index("## 2. Second Video"),
        )


if __name__ == "__main__":
    unittest.main()
