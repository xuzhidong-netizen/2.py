from __future__ import annotations

import shutil
from pathlib import Path

from dance_generator_rebuilt.domain.models import DanceList
from dance_generator_rebuilt.services.scanner import scan_music_directory
from dance_generator_rebuilt.services.tags import read_tag, write_tag


def save_music_files(dance_list: DanceList, destination: str | Path, method: str = "copy") -> DanceList:
    target_root = Path(destination)
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)

    for part_index, part in enumerate(dance_list.parts, start=1):
        part_dir = target_root / f"{part_index} {part.part_title}" if part.part_title else target_root
        part_dir.mkdir(parents=True, exist_ok=True)
        for song in part.music:
            ext = song.filepath.suffix
            suffix = "-点播" if song.choose else ""
            filename = f"{song.num:02d}-{song.dance}-{song.title}{suffix}{ext}"
            target_file = part_dir / filename
            if method == "move":
                shutil.move(str(song.filepath), str(target_file))
            else:
                shutil.copy2(str(song.filepath), str(target_file))
            song.filepath = target_file
            tag = read_tag(target_file)
            if tag.get("title") != f"{song.dance}-{song.title}" or "华中科技大学" not in str(tag.get("album")):
                write_tag(target_file, f"{song.dance}-{song.title}", song.dance)
                song.is_change = True

    rebuilt = scan_music_directory(target_root)
    rebuilt.title = dance_list.title
    rebuilt.name = dance_list.name
    rebuilt.date = dance_list.date
    rebuilt.club = dance_list.club
    rebuilt.place = dance_list.place
    rebuilt.time = list(dance_list.time)
    return rebuilt
