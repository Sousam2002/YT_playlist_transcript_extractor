import argparse
import unittest

from main import _arguments, _clean_url, _parse_range


class ParseRangeTests(unittest.TestCase):
    def test_normalizes_supported_range_forms(self) -> None:
        self.assertEqual(_parse_range("7"), "7")
        self.assertEqual(_parse_range("5-12"), "5:12")
        self.assertEqual(_parse_range("5-"), "5:")
        self.assertEqual(_parse_range("-10"), ":10")

    def test_rejects_invalid_ranges(self) -> None:
        for value in ("0", "0-3", "5-2", "-", "abc"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    _parse_range(value)

    def test_cli_accepts_range_argument(self) -> None:
        url, playlist_range = _arguments(
            ["https://youtube.com/playlist?list=example", "--range", "1-24"]
        )

        self.assertEqual(url, "https://youtube.com/playlist?list=example")
        self.assertEqual(playlist_range, "1:24")


class CleanUrlTests(unittest.TestCase):
    def test_unwraps_markdown_link_and_escaped_ampersand(self) -> None:
        value = "[playlist](https://youtube.com/playlist?list=abc\\&si=def)"

        self.assertEqual(
            _clean_url(value),
            "https://youtube.com/playlist?list=abc&si=def",
        )


if __name__ == "__main__":
    unittest.main()
