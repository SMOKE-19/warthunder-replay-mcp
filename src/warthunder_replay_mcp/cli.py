from __future__ import annotations

from .server import main as server_main


def main() -> int:
    return server_main()


if __name__ == "__main__":
    raise SystemExit(main())
