from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PACKAGE_ROOT.parent
LEGACY_CSS_DIR = WORKSPACE_ROOT / "css"
LEGACY_WKHTMLTOPDF = WORKSPACE_ROOT / "wkhtmltopdf" / "bin" / "wkhtmltopdf.exe"


def css_path_for_club(club_name: str) -> tuple[Path, Path]:
    if club_name == "华中大国际标准交谊舞俱乐部":
        return LEGACY_CSS_DIR / "wuqu_phone.css", LEGACY_CSS_DIR / "HBDC.png"
    return LEGACY_CSS_DIR / "wuqu_phone_other.css", LEGACY_CSS_DIR / "other.png"
