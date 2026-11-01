from __future__ import annotations

import sys
from pathlib import Path

from auto_confirm import build_preview, write_preview_artifacts


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    out = Path(__file__).resolve().parent
    root = out.parent
    preview = build_preview(root, out)
    write_preview_artifacts(out, preview)
    print(f"Tổng crop: {preview['total']}")
    print(f"Đủ điều kiện (chưa áp dụng): {preview['eligible_count']}")
    print(f"Nhãn thủ công được bảo vệ: {preview['manual_preserved_count']}")
    print(f"Báo cáo: {out / 'AUTO_CONFIRM_REPORT.md'}")
    print(f"Token dry-run: {preview['token']}")


if __name__ == "__main__":
    main()
