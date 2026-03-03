from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from urllib.parse import unquote

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from dance_generator_rebuilt.domain.models import Part
from dance_generator_rebuilt.services.exporter import export_html, export_pdf_and_png, export_txt
from dance_generator_rebuilt.services.file_manager import save_music_files
from dance_generator_rebuilt.services.rules import validate_dance_list
from dance_generator_rebuilt.services.scanner import parse_song, scan_music_directory
from dance_generator_rebuilt.services.serialization import dance_list_from_dict, dance_list_to_dict, default_date_string


PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_ROOT = PACKAGE_ROOT / "web_static"
WORKSPACE_ROOT = PACKAGE_ROOT.parent


class AppState:
    def __init__(self) -> None:
        self.dance_list = dance_list_from_dict({"date": default_date_string(), "parts": []})


STATE = AppState()


async def json_body(request: Request) -> dict:
    return json.loads(await request.body() or b"{}")


async def home(_: Request) -> HTMLResponse:
    html = (PACKAGE_ROOT / "standalone.html").read_text(encoding="utf-8")
    html = (
        html
        .replace("./web_static/示范舞曲-top3.zip", "/static/示范舞曲-top3.zip")
        .replace("./cloud_sample.json", "/static/cloud_sample.json")
        .replace("./cloud_full.json", "/static/cloud_full.json")
    )
    return HTMLResponse(html)


async def get_state(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "dance_list": dance_list_to_dict(STATE.dance_list)})


async def load_directory(request: Request) -> JSONResponse:
    payload = await json_body(request)
    path = payload.get("path", "").strip()
    if not path:
        return JSONResponse({"ok": False, "error": "缺少舞曲目录路径"}, status_code=400)
    try:
        dance_list = scan_music_directory(path)
        meta = payload.get("meta") or {}
        dance_list.title = meta.get("title") or dance_list.title
        dance_list.name = meta.get("name") or dance_list.name
        dance_list.date = meta.get("date") or default_date_string()
        dance_list.club = meta.get("club") or dance_list.club
        dance_list.place = meta.get("place") or dance_list.place
        dance_list.time = list(meta.get("time") or [])
        STATE.dance_list = dance_list
        return JSONResponse({"ok": True, "dance_list": dance_list_to_dict(dance_list)})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


async def update_state(request: Request) -> JSONResponse:
    payload = await json_body(request)
    try:
        STATE.dance_list = dance_list_from_dict(payload.get("dance_list") or {})
        return JSONResponse({"ok": True, "dance_list": dance_list_to_dict(STATE.dance_list)})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


async def check_rules(request: Request) -> JSONResponse:
    payload = await json_body(request)
    try:
        STATE.dance_list = dance_list_from_dict(payload.get("dance_list") or {})
        issues = [asdict(issue) for issue in validate_dance_list(STATE.dance_list)]
        return JSONResponse({"ok": True, "dance_list": dance_list_to_dict(STATE.dance_list), "issues": issues})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


async def export_outputs(request: Request) -> JSONResponse:
    payload = await json_body(request)
    output_dir = Path(payload.get("output_dir") or ".")
    try:
        STATE.dance_list = dance_list_from_dict(payload.get("dance_list") or {})
        html_path = export_html(STATE.dance_list, output_dir)
        txt_path = export_txt(STATE.dance_list, output_dir)
        pdf_path, png_path = export_pdf_and_png(html_path, STATE.dance_list, output_dir / "song-list")
        return JSONResponse(
            {
                "ok": True,
                "dance_list": dance_list_to_dict(STATE.dance_list),
                "files": {
                    "html": str(html_path),
                    "txt": str(txt_path),
                    "pdf": str(pdf_path),
                    "png": str(png_path),
                    "preview_url": f"/api/file?path={png_path.as_posix()}",
                },
            }
        )
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


async def save_files(request: Request) -> JSONResponse:
    payload = await json_body(request)
    method = payload.get("method") or "copy"
    destination = payload.get("destination")
    try:
        STATE.dance_list = dance_list_from_dict(payload.get("dance_list") or {})
        if not destination:
            compact_date = STATE.dance_list.date.replace("年", "").replace("月", "").replace("日", "")
            destination = str(WORKSPACE_ROOT / f"{compact_date} {STATE.dance_list.title}by{STATE.dance_list.name}")
        STATE.dance_list = save_music_files(STATE.dance_list, destination, method)
        return JSONResponse({"ok": True, "dance_list": dance_list_to_dict(STATE.dance_list), "destination": destination})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


async def add_song(request: Request) -> JSONResponse:
    payload = await json_body(request)
    try:
        STATE.dance_list = dance_list_from_dict(payload.get("dance_list") or {})
        file_path = payload.get("file_path", "").strip()
        if not file_path:
            return JSONResponse({"ok": False, "error": "缺少舞曲文件路径"}, status_code=400)
        song = parse_song(Path(file_path))
        if not STATE.dance_list.parts:
            STATE.dance_list.parts = [Part(part_title=None)]
        STATE.dance_list.parts[-1].music.append(song)
        STATE.dance_list = dance_list_from_dict(dance_list_to_dict(STATE.dance_list))
        return JSONResponse({"ok": True, "dance_list": dance_list_to_dict(STATE.dance_list)})
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


async def serve_file(request: Request) -> Response:
    file_path = request.query_params.get("path", "")
    if not file_path:
        return Response(status_code=404)
    path = Path(unquote(file_path))
    if not path.exists() or not path.is_file():
        return Response(status_code=404)
    return FileResponse(path)


def create_app() -> Starlette:
    routes = [
        Route("/", home),
        Route("/api/state", get_state, methods=["GET"]),
        Route("/api/load", load_directory, methods=["POST"]),
        Route("/api/update", update_state, methods=["POST"]),
        Route("/api/check", check_rules, methods=["POST"]),
        Route("/api/export", export_outputs, methods=["POST"]),
        Route("/api/save", save_files, methods=["POST"]),
        Route("/api/add-song", add_song, methods=["POST"]),
        Route("/api/file", serve_file, methods=["GET"]),
        Mount("/static", app=StaticFiles(directory=STATIC_ROOT), name="static"),
    ]
    return Starlette(routes=routes)


app = create_app()


def main() -> int:
    uvicorn.run("dance_generator_rebuilt.web:app", host="127.0.0.1", port=8000, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
