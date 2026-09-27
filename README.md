# YouTube Playlist Transcript Extractor

Export the available captions from a YouTube playlist or standalone video to
one Markdown document. Playlist videos stay in order. Missing captions are
recorded in the document and do not stop the rest of the run.

## Requirements

- Python 3.10 or newer
- Internet access

## Install

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Pass the playlist URL as an argument:

```powershell
python main.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

Or run without an argument and paste the URL at the prompt:

```powershell
python main.py
```

The program prefers English captions, then falls back to the first available
caption language. It retrieves metadata and captions only; it does not download
video or audio.

Each run overwrites `output/playlist_transcript.md` with UTF-8 Markdown.

## Video Selection

Use `--range` to process selected playlist positions:

```powershell
# Videos 5 through 12, inclusive
python main.py "PLAYLIST_URL" --range 5-12

# One item from a playlist
python main.py "PLAYLIST_URL" --range 7

# The first 10 items or everything from item 5 onward
python main.py "PLAYLIST_URL" --range -10
python main.py "PLAYLIST_URL" --range 5-

# One standalone video
python main.py "VIDEO_URL"
```

Playlist positions will be 1-based and will match the visible YouTube playlist
order. Invalid ranges or ranges that select no videos produce a clear error.
Standalone videos use the same Markdown layout with one numbered section.

## Tests

```powershell
python -m unittest discover -s tests
```
