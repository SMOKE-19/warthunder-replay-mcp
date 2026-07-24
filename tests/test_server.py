from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session

from warthunder_replay_mcp.server import (
    DOWNLOAD_ROOT_ENV,
    LOGIN_COOKIE_ENV,
    build_download_config,
    get_download_base,
    mcp,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client_session() -> AsyncGenerator[ClientSession]:
    async with create_connected_server_and_client_session(mcp, raise_exceptions=True) as session:
        yield session


@pytest.mark.anyio
async def test_mcp_lists_expected_tools(client_session: ClientSession) -> None:
    result = await client_session.list_tools()
    assert {tool.name for tool in result.tools} == {"download_replay", "get_mcp_status"}


@pytest.mark.anyio
async def test_mcp_status_tool_returns_structured_result(
    client_session: ClientSession,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv(DOWNLOAD_ROOT_ENV, str(tmp_path))
    monkeypatch.delenv(LOGIN_COOKIE_ENV, raising=False)

    result = await client_session.call_tool("get_mcp_status", {})

    assert result.isError is False
    assert result.structuredContent == {
        "download_root": str(tmp_path.resolve()),
        "authentication": "Microsoft Edge cookies",
        "transport": "stdio",
    }


def test_build_download_config_normalizes_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv(DOWNLOAD_ROOT_ENV, str(tmp_path))
    monkeypatch.setenv(LOGIN_COOKIE_ENV, "session=value")

    config = build_download_config(" 1234567 ", " ABCDEF1234567890 ", 3)

    assert config.user_id == "1234567"
    assert config.session_id == "abcdef1234567890"
    assert config.download_root == tmp_path.resolve() / "abcdef1234567890"
    assert config.login_cookie == "session=value"
    assert config.use_edge_cookies is False


@pytest.mark.parametrize(
    ("user_id", "session_id", "workers"),
    [
        ("abc", "abcdef1234567890", 3),
        ("123", "../abcdef12", 3),
        ("123", "abcdef1234567890", 0),
        ("123", "abcdef1234567890", 9),
    ],
)
def test_build_download_config_rejects_invalid_input(
    user_id: str,
    session_id: str,
    workers: int,
) -> None:
    with pytest.raises(ValueError):
        build_download_config(user_id, session_id, workers)


def test_default_download_base_is_local_downloads(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv(DOWNLOAD_ROOT_ENV, raising=False)
    monkeypatch.chdir(tmp_path)
    assert get_download_base() == (tmp_path / "Downloads").resolve()
