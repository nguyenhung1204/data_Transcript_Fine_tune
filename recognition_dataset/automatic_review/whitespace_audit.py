"""Find suspicious spacing in confirmed invoice crop transcripts for human review."""
from __future__ import annotations

import csv
import ast
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
DATA_PATH = OUT / "review_data.json"
ANNOTATIONS_PATH = OUT / "manual_review_progress.json"
REPORT_JSON = OUT / "whitespace_audit_report.json"
REPORT_CSV = OUT / "whitespace_audit_report.csv"
AUDIT_PROGRESS = OUT / "whitespace_audit_progress.json"

_LETTER = r"[^\W\d_]"
_PATTERNS = (
    ("split_inside_word", re.compile(rf"(?<![\w])({_LETTER})[ \t]+({_LETTER}{{2,}})(?![\w])", re.UNICODE)),
    ("space_after_opening", re.compile(r"[([{][ \t]+(?=\S)")),
    ("space_before_closing", re.compile(r"[ \t]+(?=[)\]}])")),
    # A space before ':' is common in invoice labels ("MST :"), so avoid
    # flooding the review queue with this template style.
    ("space_before_punctuation", re.compile(r"[ \t]+(?=[,.;!?])")),
    ("repeated_whitespace", re.compile(r" {2,}|\t+")),
    ("nonstandard_whitespace", re.compile(r"[\u00a0\u2000-\u200b\u202f\u205f\u3000\ufeff]")),
)
_MESSAGES = {
    "split_inside_word": "Có một chữ cái đứng riêng trước một mảnh từ; có thể là từ bị chèn khoảng trắng.",
    "space_after_opening": "Có khoảng trắng ngay sau dấu ngoặc mở.",
    "space_before_closing": "Có khoảng trắng ngay trước dấu ngoặc đóng.",
    "space_before_punctuation": "Có khoảng trắng ngay trước dấu câu.",
    "repeated_whitespace": "Có nhiều khoảng trắng liên tiếp hoặc tab.",
    "nonstandard_whitespace": "Có ký tự khoảng trắng đặc biệt hoặc vô hình.",
}


def _token(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def analyze_transcript(text: str, vocabulary: Iterable[str] | None = None) -> dict[str, Any]:
    """Return spacing evidence and a conservative join suggestion, never a correction."""
    text = str(text or "")
    vocabulary = {_token(word) for word in (vocabulary or ())}
    issues: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int]] = set()
    join_matches: list[tuple[int, int, str]] = []

    for category, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            if category == "split_inside_word" and match.start() and text[match.start() - 1] in "/\\":
                # Keep common abbreviations such as A/C No. out of the triage queue.
                continue
            key = (category, match.start(), match.end())
            if key in seen:
                continue
            seen.add(key)
            issue = {
                "category": category,
                "message": _MESSAGES[category],
                "start": match.start(),
                "end": match.end(),
                "text": match.group(0),
            }
            issues.append(issue)
            if category == "split_inside_word":
                left, right = match.group(1), match.group(2)
                joined = left + right
                if _token(joined) in vocabulary and not (_token(left) in vocabulary and _token(right) in vocabulary):
                    join_matches.append((match.start(), match.end(), joined))

    issues.sort(key=lambda item: (item["start"], item["end"], item["category"]))
    suggestion = None
    if join_matches:
        result = text
        for start, end, joined in reversed(join_matches):
            result = result[:start] + joined + result[end:]
        if result != text:
            suggestion = result
    return {"issues": issues, "categories": list(dict.fromkeys(x["category"] for x in issues)), "suggested_transcript": suggestion}


def confirmed_gallery_rows(
    data: list[dict[str, Any]],
    saved_annotations: list[dict[str, Any]],
    *,
    excluded_invoices: set[str] | frozenset[str] = frozenset(),
) -> list[dict[str, Any]]:
    """Mirror confirmed_gallery.html: source states, then persisted decisions, then invoice exclusion."""
    state: dict[str, dict[str, Any]] = {}
    for row in data:
        crop_id = str(row.get("id") or row.get("crop_id") or "")
        if crop_id and row.get("status") in {"verified", "rejected"}:
            state[crop_id] = {"status": row["status"], "transcript": row.get("text") or ""}
    for annotation in saved_annotations:
        crop_id = str(annotation.get("crop_id") or "")
        if crop_id:
            state[crop_id] = {**state.get(crop_id, {}), **annotation}

    rows = []
    for row in data:
        crop_id = str(row.get("id") or row.get("crop_id") or "")
        current = state.get(crop_id, {})
        invoice = str(row.get("invoice") or "")
        if current.get("status") != "verified" or invoice in excluded_invoices:
            continue
        rows.append({
            "id": crop_id,
            "crop_id": str(row.get("crop_id") or crop_id),
            "invoice": invoice,
            "pdf": str(row.get("pdf") or ""),
            "page": row.get("page"),
            "coords": row.get("coords") or [],
            "image": str(row.get("image") or ""),
            "page_image": str(row.get("page_image") or ""),
            "pdf_path": str(row.get("pdf_path") or ""),
            "split": str(row.get("split") or ""),
            "transcript": str(current.get("transcript") or row.get("text") or ""),
            "confirmation_method": str(current.get("confirmation_method") or ""),
        })
    return rows


def load_excluded_invoices(gallery_path: Path | None = None) -> set[str]:
    """Read the gallery's existing exclusion list so audit scope cannot silently drift."""
    gallery_path = gallery_path or OUT / "confirmed_gallery.html"
    html = gallery_path.read_text(encoding="utf-8")
    match = re.search(r"const\s+EXCLUDED_INVOICES\s*=\s*new\s+Set\((\[[^\]]*\])\)", html)
    if not match:
        raise ValueError("Không đọc được EXCLUDED_INVOICES từ confirmed_gallery.html")
    raw_values = match.group(1)
    try:
        values = json.loads(raw_values)
    except json.JSONDecodeError:
        # The existing page uses JavaScript single-quoted strings, not JSON.
        # literal_eval accepts only Python literals and does not execute code.
        values = ast.literal_eval(raw_values)
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError("EXCLUDED_INVOICES không đúng định dạng danh sách chuỗi")
    return set(values)


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_json(path: Path, payload: Any) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def build_report(
    data: list[dict[str, Any]],
    saved_annotations: list[dict[str, Any]],
    *,
    excluded_invoices: set[str] | frozenset[str],
    audit_progress: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    gallery_rows = confirmed_gallery_rows(data, saved_annotations, excluded_invoices=excluded_invoices)
    vocabulary = {
        _token(word)
        for row in gallery_rows
        for word in re.findall(r"[^\W\d_]+", unicodedata.normalize("NFC", row["transcript"]), re.UNICODE)
    }
    progress_items = (audit_progress or {}).get("items", {})
    candidates: dict[str, dict[str, Any]] = {}
    category_counts: Counter[str] = Counter()
    current_anomaly_count = 0
    for row in gallery_rows:
        analysis = analyze_transcript(row["transcript"], vocabulary)
        if not analysis["issues"]:
            continue
        current_anomaly_count += 1
        crop_id = row["crop_id"]
        state = progress_items.get(crop_id, {})
        candidate = {
            **row,
            "original_transcript": str(state.get("original_transcript") or row["transcript"]),
            "current_transcript": row["transcript"],
            "suggested_transcript": analysis["suggested_transcript"],
            "categories": analysis["categories"],
            "issues": analysis["issues"],
            "review_status": str(state.get("status") or "pending"),
            "reviewed_at": str(state.get("reviewed_at") or ""),
        }
        candidates[crop_id] = candidate
        category_counts.update(analysis["categories"])

    # Keep corrected items visible in the audit history even when their new transcript no longer matches a heuristic.
    by_id = {row["crop_id"]: row for row in gallery_rows}
    for crop_id, state in progress_items.items():
        if state.get("status") != "corrected" or crop_id in candidates:
            continue
        snapshot = state.get("snapshot") or {}
        base = by_id.get(crop_id, snapshot)
        if not base:
            continue
        candidate = {
            **base,
            "original_transcript": str(state.get("original_transcript") or snapshot.get("transcript") or ""),
            "current_transcript": str(base.get("transcript") or state.get("corrected_transcript") or ""),
            "suggested_transcript": str(state.get("corrected_transcript") or "") or None,
            "categories": list(snapshot.get("categories") or []),
            "issues": list(snapshot.get("issues") or []),
            "review_status": "corrected",
            "reviewed_at": str(state.get("reviewed_at") or ""),
        }
        candidates[crop_id] = candidate
        category_counts.update(candidate["categories"])

    ordered = sorted(candidates.values(), key=lambda row: (row.get("invoice", ""), int(row.get("page") or 0), row["crop_id"]))
    status_counts = Counter(row["review_status"] for row in ordered)
    visually_reviewed = status_counts.get("no_issue", 0) + status_counts.get("corrected", 0)
    return {
        "version": 1,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source": {
            "review_data": str(DATA_PATH),
            "annotations": str(ANNOTATIONS_PATH),
            "gallery": str(OUT / "confirmed_gallery.html"),
            "excluded_invoices": sorted(excluded_invoices),
        },
        "total_gallery_confirmed": len(gallery_rows),
        "total_scanned": len(gallery_rows),
        "candidate_count": len(ordered),
        "current_anomaly_count": current_anomaly_count,
        "historical_corrected_count": sum(1 for row in ordered if row["review_status"] == "corrected" and not row["issues"]),
        "finding_count": sum(len(row["issues"]) for row in ordered),
        "category_counts": dict(sorted(category_counts.items())),
        "review_status_counts": dict(sorted(status_counts.items())),
        "scan_method": "automatic_spacing_heuristics_for_triage_only",
        "automatic_scan_is_visual_confirmation": False,
        "visually_reviewed_count": visually_reviewed,
        "uncertain_count": status_counts.get("uncertain", 0),
        "unprocessed_candidate_count": status_counts.get("pending", 0),
        "candidates": ordered,
    }


def write_report(report: dict[str, Any], *, out: Path = OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    _atomic_json(out / "whitespace_audit_report.json", report)
    fields = (
        "crop_id", "invoice", "pdf", "page", "coords", "split", "image", "page_image", "pdf_path",
        "original_transcript", "current_transcript", "suggested_transcript", "categories", "issues",
        "review_status", "reviewed_at",
    )
    temp = out / "whitespace_audit_report.csv.tmp"
    with temp.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in report["candidates"]:
            record = dict(row)
            for key in ("coords", "categories", "issues"):
                record[key] = json.dumps(record.get(key, []), ensure_ascii=False)
            writer.writerow(record)
    temp.replace(out / "whitespace_audit_report.csv")


def build_and_write_report(*, out: Path = OUT) -> dict[str, Any]:
    data = _read_json(out / "review_data.json", [])
    saved = _read_json(out / "manual_review_progress.json", {"annotations": []})
    progress = _read_json(out / "whitespace_audit_progress.json", {"version": 1, "items": {}, "history": []})
    report = build_report(
        data,
        saved.get("annotations", []),
        excluded_invoices=load_excluded_invoices(out / "confirmed_gallery.html"),
        audit_progress=progress,
    )
    write_report(report, out=out)
    return report


def save_review_status(
    *,
    crop_id: str,
    status: str,
    out: Path = OUT,
    transcript: str | None = None,
) -> dict[str, Any]:
    if status not in {"no_issue", "uncertain", "corrected"}:
        raise ValueError("Trạng thái rà khoảng trắng không hợp lệ")
    report = build_and_write_report(out=out)
    candidate = next((row for row in report["candidates"] if row["crop_id"] == crop_id), None)
    if candidate is None:
        raise KeyError("Không tìm thấy crop trong danh sách nghi vấn hiện tại")

    now = datetime.now(timezone.utc).isoformat()
    progress_path = out / "whitespace_audit_progress.json"
    progress = _read_json(progress_path, {"version": 1, "items": {}, "history": []})
    if status == "corrected":
        value = str(transcript or "")
        if not value.strip() or len(value) > 90 or any(char in value for char in "\r\n\t"):
            raise ValueError("Transcript sửa phải có nội dung một dòng, tối đa 90 ký tự")
        if value == candidate["current_transcript"]:
            raise ValueError("Transcript mới chưa khác transcript hiện tại")
        annotations_path = out / "manual_review_progress.json"
        saved = _read_json(annotations_path, {"version": 1, "annotations": []})
        annotation_index = next((i for i, item in enumerate(saved.get("annotations", [])) if item.get("crop_id") == crop_id), None)
        if annotation_index is None:
            raise ValueError("Không tìm thấy nhãn đã lưu để sửa an toàn")
        old_annotation = dict(saved["annotations"][annotation_index])
        if old_annotation.get("status") != "verified":
            raise ValueError("Nhãn không còn ở trạng thái đã xác nhận; hãy nạp lại danh sách")
        if not (out / "manual_review_progress.before_whitespace_audit.json").exists():
            import shutil
            shutil.copy2(annotations_path, out / "manual_review_progress.before_whitespace_audit.json")
        saved["annotations"][annotation_index] = {
            **old_annotation,
            "status": "verified",
            "transcript": value,
            "reviewed_at": now,
            "confirmation_method": "manual_visual_review",
            "whitespace_audit_reviewed_at": now,
        }
        _atomic_json(annotations_path, saved)
        progress.setdefault("history", []).append({
            "crop_id": crop_id,
            "at": now,
            "old_transcript": candidate["current_transcript"],
            "new_transcript": value,
            "method": "whitespace_audit_user_edit",
            "previous_confirmation_method": old_annotation.get("confirmation_method", ""),
        })
        corrected_transcript = value
    else:
        corrected_transcript = ""

    progress.setdefault("items", {})[crop_id] = {
        "status": status,
        "reviewed_at": now,
        "original_transcript": candidate["original_transcript"],
        "corrected_transcript": corrected_transcript,
        "snapshot": candidate,
    }
    _atomic_json(progress_path, progress)
    updated = build_and_write_report(out=out)
    return {
        "saved": True,
        "crop_id": crop_id,
        "status": status,
        "reviewed_at": now,
        "candidate_count": updated["candidate_count"],
        "review_status_counts": updated["review_status_counts"],
    }
