from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import ReplayDownloadConfig
from .downloader import download_replay as run_download

DOWNLOAD_ROOT_ENV = "WARTHUNDER_REPLAY_DOWNLOAD_ROOT"
LOGIN_COOKIE_ENV = "WARTHUNDER_LOGIN_COOKIE"
_SESSION_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{8,32}$")
_USER_ID_PATTERN = re.compile(r"^[0-9]+$")

mcp = FastMCP(
    "War Thunder Replay Downloader",
    instructions=(
        "Download authenticated War Thunder server replay parts. "
        "Files are written only below WARTHUNDER_REPLAY_DOWNLOAD_ROOT."
    ),
    json_response=True,
)


def get_download_base() -> Path:
    configured = os.environ.get(DOWNLOAD_ROOT_ENV, "").strip()
    return Path(configured).expanduser().resolve() if configured else (Path.cwd() / "Downloads").resolve()


def build_download_config(
    user_id: str,
    session_id: str,
    max_workers: int,
) -> ReplayDownloadConfig:
    normalized_user_id = user_id.strip()
    normalized_session_id = session_id.strip().lower()

    if not _USER_ID_PATTERN.fullmatch(normalized_user_id):
        raise ValueError("user_id must contain digits only.")
    if not _SESSION_ID_PATTERN.fullmatch(normalized_session_id):
        raise ValueError("session_id must be 8-32 hexadecimal characters.")
    if not 1 <= max_workers <= 8:
        raise ValueError("max_workers must be between 1 and 8.")

    login_cookie = os.environ.get(LOGIN_COOKIE_ENV, "").strip()
    return ReplayDownloadConfig(
        user_id=normalized_user_id,
        session_id=normalized_session_id,
        download_root=get_download_base() / normalized_session_id,
        login_cookie=login_cookie,
        use_edge_cookies=not bool(login_cookie),
        max_workers=max_workers,
    )


@mcp.tool()
def get_mcp_status() -> dict[str, Any]:
    """Return local output and authentication settings without exposing cookie values."""
    return {
        "download_root": str(get_download_base()),
        "authentication": (
            "WARTHUNDER_LOGIN_COOKIE environment variable"
            if os.environ.get(LOGIN_COOKIE_ENV, "").strip()
            else "Microsoft Edge cookies"
        ),
        "transport": "stdio",
    }


@mcp.tool()
def download_replay(
    user_id: str,
    session_id: str,
    max_workers: int = 3,
) -> dict[str, Any]:
    """Download every .wrpl part for one user/session pair.

    Args:
        user_id: Numeric War Thunder player ID used by replay search.
        session_id: Hexadecimal replay session ID.
        max_workers: Parallel downloads from 1 through 8.
    """
    config = build_download_config(user_id, session_id, max_workers)
    downloaded_files = run_download(config)
    total_bytes = sum(path.stat().st_size for path in downloaded_files)
    return {
        "ok": True,
        "user_id": config.user_id,
        "session_id": config.session_id,
        "download_directory": str(config.download_root),
        "file_count": len(downloaded_files),
        "total_bytes": total_bytes,
        "files": [path.name for path in downloaded_files],
    }


def main() -> int:
    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
