from __future__ import annotations

from dataclasses import dataclass

from dance_generator_rebuilt.domain.models import COLLECTIVE_DANCES, DanceList
from dance_generator_rebuilt.services.scanner import get_distribution


@dataclass(slots=True)
class RuleIssue:
    level: str
    message: str
    song_md5: str | None = None
    field: str | None = None


def validate_dance_list(dance_list: DanceList) -> list[RuleIssue]:
    issues: list[RuleIssue] = []
    distribution = get_distribution(dance_list)

    for index, count in enumerate(distribution.collective):
        if count > 1:
            issues.append(RuleIssue("error", f"{COLLECTIVE_DANCES[index]} 重复", field="dance"))

    songs = dance_list.songs
    md5s = [song.md5 for song in songs]
    previous = None

    for song in songs:
        if song.speed == "quick" and song.duration >= 240:
            issues.append(RuleIssue("error", f"{song.title} 时长超过 4 分钟", song.md5, "duration"))
        elif song.duration >= 270:
            issues.append(RuleIssue("error", f"{song.title} 时长超过 4 分 30 秒", song.md5, "duration"))
        elif song.duration >= 240:
            issues.append(RuleIssue("warn", f"{song.title} 时长超过 4 分钟", song.md5, "duration"))

        if not song.dancetype:
            issues.append(RuleIssue("error", f"{song.title} 无法识别舞种", song.md5, "dance"))
        elif previous is not None:
            if song.dancetype == previous.dancetype and song.dancetype != "collective":
                issues.append(RuleIssue("error", f"{song.title} 违反舞种相间规则", song.md5, "dance"))
            if song.speed == previous.speed and song.speed is not None:
                level = "error" if song.speed == "quick" else "warn"
                issues.append(RuleIssue(level, f"{song.title} 违反快慢相间规则", song.md5, "dance"))

        if md5s.count(song.md5) > 1:
            issues.append(RuleIssue("error", f"{song.title} 重复", song.md5, "md5"))
        previous = song

    return issues
