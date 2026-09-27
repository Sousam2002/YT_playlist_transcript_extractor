"""Playlist metadata extraction without downloading media."""

from dataclasses import dataclass

import yt_dlp


@dataclass(frozen=True)
class Video:
    id: str | None
    title: str
    url: str | None


@dataclass(frozen=True)
class Playlist:
    title: str
    videos: list[Video]


def extract_playlist(
    youtube_url: str,
    playlist_range: str | None = None,
) -> Playlist:
    """Return video metadata from a playlist selection or standalone video."""
    options = {
        "extract_flat": "in_playlist",
        "ignoreerrors": True,
        "quiet": True,
        "skip_download": True,
    }
    if playlist_range:
        options["playlist_items"] = playlist_range

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(youtube_url, download=False)

    if not info:
        raise RuntimeError("YouTube returned no video information.")

    entries = info.get("entries")
    if entries is None:
        if playlist_range:
            raise ValueError("--range can only be used with a playlist URL.")

        video_id = info.get("id")
        if not video_id:
            raise ValueError("The URL did not resolve to a YouTube video.")
        title = str(info.get("title") or "Untitled video")
        url = info.get("webpage_url") or info.get("original_url") or youtube_url
        return Playlist(
            title=title,
            videos=[Video(id=str(video_id), title=title, url=str(url))],
        )

    videos: list[Video] = []
    for position, entry in enumerate(entries, start=1):
        if not entry:
            videos.append(
                Video(
                    id=None,
                    title=f"Unavailable video {position}",
                    url=None,
                )
            )
            continue

        video_id = entry.get("id")
        playlist_position = entry.get("playlist_index") or position
        title = entry.get("title") or f"Untitled video {playlist_position}"
        url = entry.get("webpage_url") or entry.get("url")
        if video_id and (not url or not str(url).startswith(("http://", "https://"))):
            url = f"https://www.youtube.com/watch?v={video_id}"

        videos.append(Video(id=video_id, title=str(title), url=str(url) if url else None))

    if not videos:
        if playlist_range:
            raise ValueError("No playlist videos matched the requested --range.")
        raise ValueError("The playlist contains no videos.")

    title = str(info.get("title") or "YouTube Playlist Transcript")
    return Playlist(title=title, videos=videos)
