from __future__ import annotations

from pathlib import Path

from dance_generator_rebuilt.assets import LEGACY_WKHTMLTOPDF, css_path_for_club
from dance_generator_rebuilt.domain.models import BALLROOM_DANCES, COLLECTIVE_DANCES, DanceList, FRAME_DANCES, HANDLE_DANCES
from dance_generator_rebuilt.services.scanner import get_distribution
from dance_generator_rebuilt.services.utils import seconds_to_clock


def distribution_lines(dance_list: DanceList) -> list[str]:
    distribution = get_distribution(dance_list)
    groups = [
        (HANDLE_DANCES, distribution.handle, False),
        (FRAME_DANCES, distribution.frame, False),
        (BALLROOM_DANCES, distribution.ballroom, False),
        (COLLECTIVE_DANCES, distribution.collective, True),
    ]
    lines: list[str] = []
    for labels, counts, collective in groups:
        if collective:
            once = [labels[idx] for idx, count in enumerate(counts) if count == 1]
            multi = [f"{labels[idx]}{count}首" for idx, count in enumerate(counts) if count > 1]
            text = ""
            if once:
                text = "、".join(once) + ("各1首" if len(once) > 1 else "1首")
            if multi:
                if text:
                    text += "、"
                text += "、".join(multi)
            if text:
                lines.append(text)
            continue
        items = [f"{labels[idx]}{count}首" for idx, count in enumerate(counts) if count]
        if items:
            lines.append("、".join(items))
    return lines


def export_txt(dance_list: DanceList, output_dir: str | Path, filename: str = "舞曲列表.txt") -> Path:
    target = Path(output_dir) / filename
    songs = dance_list.songs
    lines = [
        f"本次舞曲由 {dance_list.name} 编排，共{len(songs)}首曲子（包括清场与开场曲目），总时长为{dance_list.duration // 3600}小时{(dance_list.duration % 3600) // 60}分{dance_list.duration % 60}秒。",
        "",
    ]
    lines.extend(distribution_lines(dance_list))
    lines.append("")
    for part in dance_list.parts:
        if part.part_title:
            lines.append(f"====={part.part_title}=====")
        for song in part.music:
            lines.append(f"{song.num:02d}-{song.dance}-{song.title} ({seconds_to_clock(song.duration)})")
    lines.extend(["", dance_list.date])
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def export_html(dance_list: DanceList, output_dir: str | Path, filename: str = "song-list.html") -> Path:
    target = Path(output_dir) / filename
    title_space = max(0, 3 * (11 - len(dance_list.title)) // max(1, len(dance_list.title) - 1))
    spread_title = "&nbsp;" * title_space
    pretty_title = spread_title.join(list(dance_list.title)) if len(dance_list.title) > 1 else dance_list.title
    rows: list[str] = []
    for part in dance_list.parts:
        if part.part_title:
            rows.append(f"<div class='sessions'>{part.part_title}</div><div class='sessdur'>{seconds_to_clock(part.duration)}</div><table>")
        else:
            rows.append("<table>")
        for song in part.music:
            classes = "music choose" if song.choose else "music"
            rows.append(
                f"<tr><td class='no'>{song.num:02d}</td><td class='{classes}'>{song.dance}-{song.title}</td><td class='dur'>{seconds_to_clock(song.duration)}</td><td class='timestamp'></td></tr>"
            )
        rows.append("</table>")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{dance_list.title}</title>
</head>
<body>
  <div id="bg">
    <header><h2>{pretty_title}</h2></header>
    <section class="info">本次舞曲由<strong class="name">{dance_list.name}</strong>编排，共<strong class="num">{dance_list.count}</strong>首曲子，总时长为<strong class="time">{dance_list.duration // 3600}小时{(dance_list.duration % 3600) // 60}分{dance_list.duration % 60}秒。</strong></section>
    <div class="clearfix"><div class="center party_info"><table><tr><td id="place">{dance_list.place}</td><td id="startTime">{' '.join(dance_list.time)}</td></tr></table></div></div>
    <nav class="clearfix"><div class="center"><h3>舞曲分布</h3><div class="dis"><table>{''.join(f'<tr><td>{line}</td></tr>' for line in distribution_lines(dance_list))}</table></div></div></nav>
    <section class="list"><div class="center"><h3>舞曲列表</h3><div class="cont">{''.join(rows)}<footer class="right"><p class="hbdc">{dance_list.club}</p><p class="date">{dance_list.date}</p></footer></div></div></section>
  </div>
</body>
</html>
"""
    target.write_text(html, encoding="utf-8")
    return target


def export_pdf_and_png(html_path: str | Path, dance_list: DanceList, output_stem: str | Path) -> tuple[Path, Path]:
    from format_conversion import corp_margin, html2pdf, pdf2png

    html_path = Path(html_path)
    output_stem = Path(output_stem)
    css_path, bg_path = css_path_for_club(dance_list.club)
    pdf_path = output_stem.with_suffix(".pdf")
    png_path = output_stem.with_suffix(".png")
    html2pdf(
        str(html_path),
        str(css_path),
        str(bg_path),
        str(LEGACY_WKHTMLTOPDF),
        width="103",
        height="700",
        filename=str(output_stem),
    )
    pdf2png(str(pdf_path), filename=str(output_stem))
    corp_margin(str(png_path))
    return pdf_path, png_path
