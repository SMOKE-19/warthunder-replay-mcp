# War Thunder Replay MCP

War Thunder 서버 리플레이의 모든 `.wrpl` 조각을 내려받는 독립 로컬 MCP
서버입니다.

`USER_ID`로 리플레이를 검색하고 정확한 `SESSION_ID`를 찾은 뒤, War Thunder
리플레이 API에서 메타데이터를 읽어 세션별 폴더에 병렬로 다운로드합니다.

## 요구 사항

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- `warthunder.com`에 로그인된 Microsoft Edge

Edge 쿠키를 사용할 수 없는 환경에서는 `WARTHUNDER_LOGIN_COOKIE` 환경변수에
쿠키 문자열을 설정할 수 있습니다. 쿠키 값은 MCP 도구의 인자나 결과에 노출되지
않습니다.

## 설치 및 검증

```powershell
cd <warthunder-replay-mcp-directory>
uv sync
uv run pytest
uv run ruff check .
```

## MCP 서버 실행

```powershell
uv run warthunder-replay-mcp
```

서버는 로컬 MCP 클라이언트용 `stdio` 전송을 사용합니다. stdout은 MCP 메시지
전용이며 다운로드 진행 상황은 stderr에 출력됩니다.

제공 도구:

- `get_mcp_status`: 저장 위치와 인증 방식을 확인합니다.
- `download_replay`: `user_id`, `session_id`, `max_workers`를 받아 리플레이를
  다운로드합니다.

파일은 항상 `WARTHUNDER_REPLAY_DOWNLOAD_ROOT\<session_id>\` 아래에 저장됩니다.
환경변수를 생략하면 현재 작업 폴더의 `Downloads\<session_id>\`를 사용합니다.

## MCP 클라이언트 설정 예시

```toml
[mcp_servers.warthunder_replay]
command = "C:\\path\\to\\warthunder-replay-mcp\\.venv\\Scripts\\warthunder-replay-mcp.exe"
cwd = "C:\\path\\to\\warthunder-replay-mcp"

[mcp_servers.warthunder_replay.env]
WARTHUNDER_REPLAY_DOWNLOAD_ROOT = "C:\\path\\to\\replay-downloads"
```

## 인증 참고 사항

- 기본값은 `browser-cookie3`를 이용한 Microsoft Edge 쿠키 자동 로드입니다.
- Edge가 실행 중이거나 Windows 보안 정책이 쿠키 복호화를 막으면 자동 로드가
  실패할 수 있습니다.
- 이때 `WARTHUNDER_LOGIN_COOKIE`를 MCP 서버 프로세스 환경에만 설정하세요.
- 높은 동시 다운로드 수는 연결 초기화를 늘릴 수 있어 2~3개부터 권장합니다.

## 프로젝트 구조

```text
src/warthunder_replay_mcp/
  cli.py
  config.py
  downloader.py
  server.py
tests/
```

`docs/`, `scripts/`, `examples/`는 로컬 보조 자료로 기본 `.gitignore` 대상입니다.
