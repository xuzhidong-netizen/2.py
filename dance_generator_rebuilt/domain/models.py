from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


HANDLE_DANCES = ["伦巴", "平四", "吉特巴"]
FRAME_DANCES = ["慢四", "慢三", "并四", "快三", "中三", "中四"]
BALLROOM_DANCES = ["华尔兹", "探戈", "维也纳", "狐步", "快步", "国标伦巴", "国标恰恰", "桑巴", "牛仔", "斗牛", "阿根廷探戈"]
COLLECTIVE_DANCES = ["青春16步", "花火16步", "32步", "64步", "兔子舞", "集体恰恰", "阿拉伯之夜", "马卡琳娜", "玛卡琳娜", "蒙古舞"]
OTHER_DANCES = ["开场曲", "结束曲"]

ALL_KNOWN_DANCES = HANDLE_DANCES + FRAME_DANCES + BALLROOM_DANCES + COLLECTIVE_DANCES + OTHER_DANCES


@dataclass(slots=True)
class Song:
    num: int | None
    dance: str
    title: str
    choose: bool
    duration: int
    other: str | None
    speed: str | None
    dancetype: str | None
    md5: str
    filepath: Path
    filename: str
    folder_name: str | None = None
    is_change: bool = False


@dataclass(slots=True)
class Part:
    part_title: str | None
    music: list[Song] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.music)

    @property
    def duration(self) -> int:
        return sum(song.duration for song in self.music)


@dataclass(slots=True)
class Distribution:
    handle: list[int]
    frame: list[int]
    ballroom: list[int]
    collective: list[int]


@dataclass(slots=True)
class DanceList:
    title: str = "青春舞会舞曲"
    name: str = "Guokr"
    date: str = ""
    club: str = "华中大国际标准交谊舞俱乐部"
    place: str = "老年活动中心"
    time: list[str] = field(default_factory=list)
    path: Path | None = None
    parts: list[Part] = field(default_factory=list)
    distribution_cache: Distribution | None = None

    @property
    def count(self) -> int:
        return sum(part.count for part in self.parts)

    @property
    def duration(self) -> int:
        return sum(part.duration for part in self.parts)

    @property
    def songs(self) -> list[Song]:
        return [song for part in self.parts for song in part.music]
