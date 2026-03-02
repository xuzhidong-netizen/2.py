from __future__ import annotations

import datetime
from pathlib import Path

from mutagen import File
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TALB, TCON, TDRC, TIT2, TPE1


DEFAULT_ALBUM = "华中科技大学国标舞俱乐部曲库"
DEFAULT_ARTIST = "HBDC"


def read_tag(file_path: str | Path) -> dict:
    path = Path(file_path)
    audio = File(path)
    if audio is None:
        return {"title": None, "artist": None, "year": None, "genre": None, "album": None}
    if path.suffix.lower() == ".mp3":
        tag = ID3(str(path))
        return {
            "title": tag["TIT2"].text[0] if "TIT2" in tag else None,
            "artist": tag["TPE1"].text[0] if "TPE1" in tag else None,
            "year": tag["TDRC"].text[0] if "TDRC" in tag else None,
            "genre": tag["TCON"].text[0] if "TCON" in tag else None,
            "album": tag["TALB"].text[0] if "TALB" in tag else None,
        }
    return {
        "title": audio.get("title", [None])[0],
        "artist": audio.get("artist", [None])[0],
        "year": audio.get("date", [None])[0] or audio.get("year", [None])[0],
        "genre": audio.get("genre", [None])[0],
        "album": audio.get("album", [None])[0],
    }


def write_tag(file_path: str | Path, title: str, genre: str) -> None:
    path = Path(file_path)
    year = str(datetime.date.today().year)
    if path.suffix.lower() == ".mp3":
        tag = ID3(str(path))
        tag["TIT2"] = TIT2(encoding=3, text=title)
        tag["TPE1"] = TPE1(encoding=3, text=DEFAULT_ARTIST)
        tag["TALB"] = TALB(encoding=3, text=DEFAULT_ALBUM)
        tag["TDRC"] = TDRC(encoding=3, text=year)
        tag["TCON"] = TCON(encoding=3, text=genre)
        tag.save()
        return

    audio = File(path)
    if audio is None:
        return
    if isinstance(audio, FLAC):
        audio["year"] = year
    else:
        audio["date"] = year
    audio["title"] = title
    audio["artist"] = DEFAULT_ARTIST
    audio["album"] = DEFAULT_ALBUM
    audio["genre"] = genre
    audio.save()
