"""Conservative PDF text + OCR1 transcript auto-confirmation policy."""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

POLICY_VERSION = "pdf_ocr_agreement_v1"
MIN_OCR_CONFIDENCE = 0.90
MAX_TRANSCRIPT_LENGTH = 90
SUPPORTED_OCR_MODELS = {"cached_paddleocr_baseline", "PaddleOCR PP-OCRv6"}


def agreement_key(value: str) -> str:
    """Compare only harmless whitespace differences; preserve all visible characters."""
    value = unicodedata.normalize("NFC", value or "")
    value = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s*([:;,!?()])\s*", r"\1", value)


def _truth(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def evaluate_candidate(
    row: dict[str, Any], *, source_pdf_status: str, crop_exists: bool,
    prior: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return eligibility and evidence without changing any data."""
    prior = prior or {}
    reasons: list[str] = []
    pdf_text = str(row.get("pdf_text") or "")
    ocr_text = str(row.get("ocr1_text", row.get("ocr1", "")) or "")
    model = str(row.get("ocr_model", row.get("ocr_engine", "")) or "")

    if prior.get("status") in {"verified", "rejected"}:
        reasons.append("already_auto_confirmed" if prior.get("confirmation_method") == POLICY_VERSION else "manual_decision_preserved")
    if prior.get("status") == "needs_review" and str(prior.get("transcript") or "").strip():
        if unicodedata.normalize("NFC", str(prior["transcript"])) != unicodedata.normalize("NFC", pdf_text):
            reasons.append("pending_draft_differs")

    if source_pdf_status == "missing":
        reasons.append("source_pdf_missing")
    elif source_pdf_status != "verified":
        reasons.append("source_pdf_sha_mismatch")
    if not crop_exists:
        reasons.append("crop_image_missing")
    if not _truth(row.get("geometry_valid")):
        reasons.append("geometry_invalid")
    try:
        x0, y0, x1, y1 = (float(row.get(k, 0)) for k in ("x0", "y0", "x1", "y1"))
        if not all(math.isfinite(v) for v in (x0, y0, x1, y1)) or x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
            reasons.append("coordinates_invalid")
    except (TypeError, ValueError):
        reasons.append("coordinates_invalid")

    if not pdf_text.strip() or not _truth(row.get("pdf_text_found", row.get("pdf_found"))):
        reasons.append("pdf_text_missing")
    try:
        line_count = int(row.get("pdf_text_line_count", 0))
    except (TypeError, ValueError):
        line_count = 0
    if line_count > 1:
        reasons.append("multiple_lines")
    elif pdf_text.strip() and line_count != 1:
        reasons.append("line_count_unknown")
    if len(pdf_text) > MAX_TRANSCRIPT_LENGTH:
        reasons.append("overlength")
    if "\ufffd" in pdf_text:
        reasons.append("replacement_character")
    if any(unicodedata.category(c).startswith("C") for c in pdf_text):
        reasons.append("control_character")

    if not ocr_text.strip():
        reasons.append("ocr1_missing")
    elif agreement_key(pdf_text) != agreement_key(ocr_text):
        reasons.append("pdf_ocr_disagree")

    if model not in SUPPORTED_OCR_MODELS:
        reasons.append("confidence_source_unknown")
    try:
        confidence = float(row.get("confidence"))
        if not math.isfinite(confidence) or not 0 <= confidence <= 1:
            reasons.append("confidence_invalid")
        elif confidence < MIN_OCR_CONFIDENCE:
            reasons.append("confidence_below_threshold")
    except (TypeError, ValueError):
        reasons.append("confidence_missing")

    reasons = list(dict.fromkeys(reasons))
    return {
        "eligible": not reasons,
        "reasons": reasons,
        "transcript": pdf_text if not reasons else "",
        "method": POLICY_VERSION,
        "evidence": {
            "pdf_text": pdf_text,
            "ocr1_text": ocr_text,
            "ocr_model": model,
            "confidence": row.get("confidence"),
            "source_pdf_sha256": row.get("source_pdf_sha256", ""),
            "geometry": {k: row.get(k) for k in ("page", "x0", "y0", "x1", "y1")},
            "policy_version": POLICY_VERSION,
            "ocr2_available": False,
        },
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_under(root: Path, relative: str) -> Path | None:
    path = (root / relative.lstrip("/\\")).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path


def load_annotations(progress_path: Path) -> dict[str, dict[str, Any]]:
    if not progress_path.is_file():
        return {}
    payload = json.loads(progress_path.read_text(encoding="utf-8"))
    return {str(a["crop_id"]): a for a in payload.get("annotations", []) if a.get("crop_id")}


def build_preview(root: Path, out: Path) -> dict[str, Any]:
    """Read current inputs and generate deterministic preview; never writes progress."""
    manifest_path = out / "automatic_review_manifest.csv"
    progress_path = out / "manual_review_progress.json"
    manifest_rows: dict[str, dict[str, str]] = {}
    import csv
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            manifest_rows[row["crop_id"]] = row
    annotations = load_annotations(progress_path)
    data = json.loads((out / "review_data.json").read_text(encoding="utf-8"))
    source_hashes: dict[Path, str] = {}
    candidates: list[dict[str, Any]] = []
    reasons = Counter()
    protected = 0
    already_auto = 0
    missing_manifest = 0
    for item in data:
        crop_id = str(item.get("id") or item.get("crop_id") or "")
        row = manifest_rows.get(crop_id)
        if not row:
            missing_manifest += 1
            reasons.update(["manifest_row_missing"])
            continue
        pdf = _safe_under(root, item.get("pdf_path", ""))
        source_status = "missing"
        if pdf and pdf.is_file():
            if pdf not in source_hashes:
                source_hashes[pdf] = _sha256(pdf)
            source_status = "verified" if source_hashes[pdf].lower() == row.get("source_pdf_sha256", "").lower() else "sha256_mismatch"
        crop = _safe_under(root, row.get("crop_path", ""))
        crop_exists = bool(crop and crop.is_file())
        policy_row = dict(row)
        policy_row["pdf_text"] = item.get("pdf_text", row.get("pdf_text", ""))
        policy_row["pdf_text_found"] = item.get("pdf_found", row.get("pdf_text_found", "false"))
        policy_row["ocr1_text"] = item.get("ocr1", row.get("ocr1_text", ""))
        policy_row["confidence"] = item.get("confidence", row.get("confidence", ""))
        policy_row["ocr_model"] = row.get("ocr_model", "")
        prior = annotations.get(crop_id)
        if prior is None and item.get("status") in {"verified", "rejected"}:
            prior = {
                "status": item["status"],
                "transcript": item.get("text", ""),
                "confirmation_method": item.get("confirmation_method", "source_human_verified"),
            }
        if prior and prior.get("status") in {"verified", "rejected"}:
            if prior.get("confirmation_method") == POLICY_VERSION:
                already_auto += 1
            else:
                protected += 1
            continue
        result = evaluate_candidate(policy_row, source_pdf_status=source_status, crop_exists=crop_exists, prior=prior)
        reasons.update(result["reasons"])
        if result["eligible"]:
            candidates.append({"crop_id": crop_id, **result})
    manifest_hash = _sha256(manifest_path)
    progress_hash = _sha256(progress_path) if progress_path.is_file() else "missing"
    source_set = hashlib.sha256("\n".join(f"{path.name}:{digest}" for path, digest in sorted(source_hashes.items(), key=lambda pair: str(pair[0]))).encode("utf-8")).hexdigest()
    token_payload = f"{manifest_hash}:{progress_hash}:{source_set}:{POLICY_VERSION}"
    token = hashlib.sha256(token_payload.encode("ascii")).hexdigest()
    return {
        "policy_version": POLICY_VERSION,
        "token": token,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total": len(data),
        "eligible_count": sum(1 for c in candidates if c["eligible"]),
        "candidates": candidates,
        "pending_count": sum(1 for item in data if annotations.get(str(item.get("id")), {}).get("status", item.get("status")) == "needs_review"),
        "manual_preserved_count": protected,
        "already_auto_confirmed_count": already_auto,
        "missing_manifest_count": missing_manifest,
        "warning_counts": dict(reasons),
        "inputs": {"manifest_sha256": manifest_hash, "progress_sha256": progress_hash, "source_pdf_set_sha256": source_set},
        "ocr2_available": False,
    }


def write_preview_artifacts(out: Path, preview: dict[str, Any], *, applied_count: int = 0, backup_path: str = "") -> None:
    """Write preview/report only; the annotation progress file is never touched here."""
    summary = {k: v for k, v in preview.items() if k != "candidates"}
    summary["candidate_ids"] = [c["crop_id"] for c in preview.get("candidates", [])]
    (out / "auto_confirm_preview.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = preview.get("warning_counts", {})
    warnings = "\n".join(f"- `{key}`: {value}" for key, value in sorted(counts.items())) or "- Không có lý do cần rà thêm."
    history_path = out / "auto_confirm_history.json"
    try:
        history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.is_file() else []
    except (OSError, json.JSONDecodeError):
        history = []
    latest = history[-1] if history else {}
    last_apply = f"{latest.get('applied', applied_count)} transcript lúc {latest.get('applied_at_utc', 'không rõ thời điểm')}" if latest or applied_count else "chưa áp dụng"
    last_backup = latest.get('backup', backup_path or 'chưa áp dụng')
    report = f"""# Báo cáo tự xác nhận transcript\n\n- Chính sách: `{POLICY_VERSION}`\n- Tạo lúc UTC: {preview.get('created_at')}\n- Tổng crop: {preview.get('total')}\n- Đủ điều kiện theo dry-run hiện tại: {preview.get('eligible_count')}\n- Đợt áp dụng gần nhất: {last_apply}\n- Ngưỡng OCR1: confidence ≥ {MIN_OCR_CONFIDENCE:.2f}; transcript tối đa {MAX_TRANSCRIPT_LENGTH} ký tự, đúng một dòng.\n- Nhãn thủ công được giữ nguyên: {preview.get('manual_preserved_count')}\n- OCR thứ hai: không có; đây chỉ là đồng thuận lớp chữ PDF + OCR1 PaddleOCR.\n- Token xem trước hiện tại: `{preview.get('token')}`\n- Sao lưu trước đợt áp dụng gần nhất: {last_backup}\n\n## Lý do giữ lại để rà tay\n\n{warnings}\n\nChỉ giá trị PDF text được giữ nguyên khi so khớp an toàn với OCR1. Bất đồng ký tự, dấu tiếng Việt, thiếu nguồn, confidence thấp hoặc hình học không hợp lệ sẽ không được tự sửa hay xác nhận.\n"""
    (out / "AUTO_CONFIRM_REPORT.md").write_text(report, encoding="utf-8")
