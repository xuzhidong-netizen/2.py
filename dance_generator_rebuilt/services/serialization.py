from __future__ import annotations

import datetime
from pathlib import Path

from dance_generator_rebuilt.domain.models import DanceList, Part, Song
from dance_generator_rebuilt.services.scanner import get_distribution, renumber_dance_list


def default_date_string() -> str:
    return datetime.date.today().strftime("%Y年%m月%d日")


def dance_list_to_dict(dance_list: DanceList) -> dict:
    distribution = get_distribution(dance_list)
    return {
        "title": dance_list.title,
        "name": dance_list.name,
        "date": dance_list.date,
        "club": dance_list.club,
        "place": dance_list.place,
        "time": list(dance_list.time),
        "path": str(dance_list.path) if dance_list.path else "",
        "count": dance_list.count,
        "duration": dance_list.duration,
        "distribution": {
            "handle": distribution.handle,
            "frame": distribution.frame,
            "ballroom": distribution.ballroom,
            "collective": distribution.collective,
        },
        "parts": [
            {
                "part_title": part.part_title or "",
                "count": part.count,
                "duration": part.duration,
                "music": [
                    {
                        "num": song.num,
                        "dance": song.dance,
                        "title": song.title,
                        "choose": song.choose,
                        "duration": song.duration,
                        "other": song.other,
                        "speed": song.speed,
                        "dancetype": song.dancetype,
                        "md5": song.md5,
                        "filepath": str(song.filepath),
                        "filename": song.filename,
                        "folder_name": song.folder_name or "",
                        "is_change": song.is_change,
                    }
                    for song in part.music
                ],
            }
            for part in dance_list.parts
        ],
    }


def dance_list_from_dict(payload: dict) -> DanceList:
    dance_list = DanceList(
        title=payload.get("title") or "青春舞会舞曲",
        name=payload.get("name") or "冬冬",
        date=payload.get("date") or default_date_string(),
        club=payload.get("club") or "华中大国际标准交谊舞俱乐部",
        place=payload.get("place") or "老年活动中心",
        time=list(payload.get("time") or []),
        path=Path(payload["path"]) if payload.get("path") else None,
    )
    parts: list[Part] = []
    for part_payload in payload.get("parts", []):
        part = Part(part_title=part_payload.get("part_title") or None)
        for song_payload in part_payload.get("music", []):
            part.music.append(
                Song(
                    num=song_payload.get("num"),
                    dance=song_payload.get("dance") or "",
                    title=song_payload.get("title") or "",
                    choose=bool(song_payload.get("choose")),
                    duration=int(song_payload.get("duration", 0)),
                    other=song_payload.get("other"),
                    speed=song_payload.get("speed"),
                    dancetype=song_payload.get("dancetype"),
                    md5=song_payload.get("md5") or "",
                    filepath=Path(song_payload.get("filepath") or "."),
                    filename=song_payload.get("filename") or Path(song_payload.get("filepath") or ".").name,
                    folder_name=song_payload.get("folder_name") or None,
                    is_change=bool(song_payload.get("is_change")),
                )
            )
        parts.append(part)
    dance_list.parts = parts or [Part(part_title=None)]
    renumber_dance_list(dance_list)
    return dance_list
