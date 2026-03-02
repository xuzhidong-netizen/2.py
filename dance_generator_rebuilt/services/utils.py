from __future__ import annotations

import hashlib


def seconds_to_clock(seconds: int) -> str:
    hour = seconds // 3600
    remainder = seconds - hour * 3600
    minute = remainder // 60
    sec = remainder % 60
    if hour > 0:
        return f"{hour}:{minute:02d}:{sec:02d}"
    return f"{minute:02d}:{sec:02d}"


def file_md5(file_path: str) -> str:
    digest = hashlib.md5()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(4096), b""):
            digest.update(chunk)
    return digest.hexdigest()
