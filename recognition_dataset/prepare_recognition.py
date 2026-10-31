"""Prepare invoice line crops and reviewable PaddleOCR transcript candidates.

Verified labels are imported only from confirmed manual crops in the existing
labeler database. PaddleOCR output remains pseudo-labeled until a person checks it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import shutil
import sqlite3
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from review_workflow import MAX_LABEL_LENGTH, apply_review_annotations, build_review_html

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
sys.path.insert(0, str(PROJECT))
SOURCE = ROOT / "source_300_invoices"
PDF_DIR = SOURCE / "pdfs"
BASELINE = PROJECT / "baseline"
LABEL_DB = PROJECT / "ocr_labeler" / "state" / "labeler.sqlite3"
LABEL_CROPS = PROJECT / "ocr_labeler" / "state" / "crops"
DICT = PROJECT / "ocr_labeler" / "assets" / "ppocrv6_dict.txt"
DPI = 300

CSV_FIELDS = [
    "crop_id", "document_id", "invoice_id", "filename", "source_pdf_sha256",
    "page", "x0", "y0", "x1", "y1", "crop_path", "split", "field_type",
    "transcript", "raw_ocr_text", "confidence", "label_status", "label_source",
    "ocr_model", "notes",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_active():
    with (SOURCE / "source_manifest.csv").open(encoding="utf-8-sig", newline="") as f:
        manifest = list(csv.DictReader(f))
    with (SOURCE / "source_copy_manifest.csv").open(encoding="utf-8-sig", newline="") as f:
        copies = list(csv.DictReader(f))
    copy_by_id = {r["document_id"]: r for r in copies}
    active = []
    for row in manifest:
        if row.get("review_status") != "included":
            continue
        copy = copy_by_id.get(row["document_id"])
        if not copy:
            raise RuntimeError(f"Missing copy manifest row for {row['document_id']}")
        pdf = PDF_DIR / Path(copy["copy_path"]).name
        if not pdf.is_file():
            raise FileNotFoundError(pdf)
        digest = sha256(pdf)
        if digest != row["sha256"].lower() or digest != copy["sha256"].lower():
            raise RuntimeError(f"Source-copy SHA-256 mismatch: {row['document_id']}")
        row["_pdf"] = pdf
        row["_sha256"] = digest
        active.append(row)
    actual = {p.resolve() for p in PDF_DIR.glob("*.pdf")}
    expected = {r["_pdf"].resolve() for r in active}
    if actual != expected:
        raise RuntimeError(f"PDF copy inventory mismatch: extra={len(actual-expected)}, missing={len(expected-actual)}")
    if len({r["_sha256"] for r in active}) != len(active):
        raise RuntimeError("Duplicate PDF SHA-256 values exist in active set")
    return active


def split_by_supplier(rows):
    """Deterministic approximate 80/10/10 split without supplier leakage."""
    label_supplier = {}
    labels = PROJECT / "data" / "unpacked" / "40HD.json"
    if labels.is_file():
        try:
            dataset = json.loads(labels.read_text(encoding="utf-8-sig"))
            for invoice in dataset.get("invoices", []):
                header = invoice.get("header", {})
                tax_obj = header.get("seller_tax_code", {})
                name_obj = header.get("seller_name", {})
                tax = "".join(ch for ch in str(tax_obj.get("normalized") or tax_obj.get("raw") or "") if ch.isdigit())
                name = "".join(ch.lower() for ch in str(name_obj.get("normalized") or name_obj.get("raw") or "") if ch.isalnum())
                key = "mst:" + tax if len(tax) >= 9 else "name:" + (name or invoice["pdf"])
                label_supplier[Path(invoice["pdf"]).name] = key
        except (ValueError, OSError):
            label_supplier = {}
    groups = defaultdict(list)
    group_map = {}
    for r in rows:
        tax = "".join(ch for ch in (r.get("seller_tax_code") or "") if ch.isdigit())
        key = "mst:" + tax if len(tax) >= 9 else label_supplier.get(r["_pdf"].name, "invoice:" + r["document_id"])
        groups[key].append(r)
        group_map[r["document_id"]] = key
    targets = {"train": round(len(rows) * 0.8), "val": round(len(rows) * 0.1)}
    targets["test"] = len(rows) - targets["train"] - targets["val"]
    counts = Counter()
    mapping = {}
    ordered = sorted(groups.items(), key=lambda p: (-len(p[1]), hashlib.sha256(p[0].encode()).hexdigest()))
    for key, members in ordered:
        n = len(members)
        split = min(("train", "val", "test"), key=lambda s: ((counts[s] + n - targets[s]) / max(targets[s], 1)) ** 2)
        counts[split] += n
        for r in members:
            mapping[r["document_id"]] = split
    return mapping, targets, counts, len(groups), group_map


def write_csv(path: Path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def render_pages(pdf_path: Path, invoice_id: str):
    import pypdfium2 as pdfium

    out_dir = ROOT / "rendered_pages" / invoice_id
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(pdf_path))
    paths = []
    try:
        for i in range(len(doc)):
            page = doc[i]
            image_path = out_dir / f"page_{i+1:03d}.png"
            if not image_path.exists():
                bitmap = page.render(scale=DPI / 72)
                image = bitmap.to_pil().convert("RGB")
                image.save(image_path, format="PNG")
                image.close()
                bitmap.close()
            paths.append(image_path)
            page.close()
    finally:
        doc.close()
    return paths


def get_baseline_records():
    result = {}
    checkpoint_dir = BASELINE / "checkpoints"
    for p in checkpoint_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        result[Path(data.get("pdf", "")).name] = data
    return result


def verified_manual_rows(split_map):
    rows = []
    if not LABEL_DB.is_file():
        return rows
    con = sqlite3.connect(LABEL_DB)
    con.row_factory = sqlite3.Row
    try:
        query = """SELECT c.*, i.pdf FROM crops c JOIN invoices i ON i.id=c.invoice_id
                   WHERE c.confirmed=1 AND trim(c.label)<>''"""
        for item in con.execute(query):
            pdf = PDF_DIR / item["pdf"]
            if not pdf.is_file():
                continue
            original = PROJECT / "data" / "unpacked" / "pdfs" / item["pdf"]
            if not original.is_file() or sha256(original) != sha256(pdf):
                continue
            image = LABEL_CROPS / item["image_name"]
            if not image.is_file():
                continue
            # Match by active PDF basename; never import labels from another PDF.
            active = next((r for r in load_active() if r["_pdf"].name == item["pdf"]), None)
            if not active:
                continue
            crop_id = "manual_" + item["id"]
            split = split_map[active["document_id"]]
            dest_rel = Path("verified") / "images" / split / f"{crop_id}.png"
            dest = ROOT / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                shutil.copy2(image, dest)
            rows.append({
                "crop_id": crop_id, "document_id": active["document_id"], "invoice_id": item["invoice_id"],
                "filename": item["pdf"], "source_pdf_sha256": sha256(pdf), "page": item["page"] + 1,
                "x0": item["x0"], "y0": item["y0"], "x1": item["x1"], "y1": item["y1"],
                "crop_path": dest_rel.as_posix(), "split": split, "field_type": item["field_type"],
                "transcript": item["label"], "raw_ocr_text": "", "confidence": "",
                "label_status": "verified", "label_source": "user_confirmed_labeler_crop",
                "ocr_model": "", "notes": "Imported only after source PDF checksum matched and labeler confirmed=1.",
            })
    finally:
        con.close()
    return rows


def normalize_regions(raw_results):
    from src.reference.run_40hd_benchmark import normalize_engine_regions

    regions = []
    for result in raw_results:
        regions.extend(normalize_engine_regions("paddleocr", result))
    return sorted(regions, key=lambda r: (r["bbox"][1], r["bbox"][0]))


def extract_one(ocr, row, split, baseline):
    import numpy as np
    from PIL import Image

    pdf = row["_pdf"]
    invoice_id = row["document_id"]
    pages = render_pages(pdf, invoice_id)
    sha = row["_sha256"]
    cached = baseline.get(pdf.name)
    use_cache = bool(cached and cached.get("source_pdf_sha256") == sha and cached.get("dpi") == DPI)
    page_results = cached.get("pages", []) if use_cache else []
    records = []
    ocr_seconds = 0.0
    if use_cache and len(page_results) != len(pages):
        use_cache = False
    for page_idx, page_path in enumerate(pages, start=1):
        started = time.perf_counter()
        if use_cache:
            regions = page_results[page_idx - 1].get("regions", [])
            engine = "cached_paddleocr_baseline"
        else:
            raw = list(ocr.predict(str(page_path)))
            regions = normalize_regions(raw)
            engine = "PaddleOCR PP-OCRv6"
            ocr_seconds += time.perf_counter() - started
        image = Image.open(page_path).convert("RGB")
        page_w, page_h = image.size
        for idx, region in enumerate(regions):
            text = str(region.get("text") or "").strip()
            box = region.get("bbox") or []
            if not text or len(box) < 4:
                continue
            x0, y0, x1, y1 = [int(round(float(v))) for v in box[:4]]
            x0, y0 = max(0, x0 - 4), max(0, y0 - 4)
            x1, y1 = min(page_w, x1 + 4), min(page_h, y1 + 4)
            if x1 - x0 < 3 or y1 - y0 < 6:
                continue
            crop = image.crop((x0, y0, x1, y1))
            seed = f"{invoice_id}|{page_idx}|{x0}|{y0}|{x1}|{y1}|{text}"
            crop_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
            rel = Path("crops") / invoice_id / f"{crop_id}.png"
            out = ROOT / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if not out.exists():
                crop.save(out, format="PNG")
            crop.close()
            score = region.get("confidence")
            records.append({
                "crop_id": crop_id, "document_id": invoice_id, "invoice_id": invoice_id,
                "filename": pdf.name, "source_pdf_sha256": sha, "page": page_idx,
                "x0": x0, "y0": y0, "x1": x1, "y1": y1, "crop_path": rel.as_posix(),
                "split": split, "field_type": "other", "transcript": "",
                "raw_ocr_text": text, "confidence": score if score is not None else "",
                "label_status": "needs_review", "label_source": "ocr_pseudo_label",
                "ocr_model": engine,
                "notes": "OCR transcript is a candidate only; verify visually before training.",
            })
        image.close()
    return pages, records, ocr_seconds, "cached" if use_cache else "fresh"


def make_review_html(rows):
    (ROOT/"review"/"review_queue.html").write_text(build_review_html(rows),encoding="utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--limit-invoices",type=int,default=0,help="Process only first N invoices (resume-safe).")
    args=parser.parse_args()
    for name in ("rendered_pages","crops","verified/images/train","verified/images/val","verified/images/test","review/train","review/val","review/test","reports","exports","logs","checkpoints"):
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    log_path=ROOT/"logs"/"run.log"
    log_path.parent.mkdir(parents=True,exist_ok=True)
    def log(msg):
        line=f"{datetime.now(timezone.utc).isoformat()} {msg}"
        print(line,flush=True)
        with log_path.open("a",encoding="utf-8") as f: f.write(line+"\n")

    rows=load_active()
    split_map,targets,split_counts,group_count,group_map=split_by_supplier(rows)
    split_rows=[]
    for r in rows:
        split_rows.append({"document_id":r["document_id"],"filename":r["filename"],"seller_tax_code_manifest":r.get("seller_tax_code",""),"supplier_group_key":group_map[r["document_id"]],"split":split_map[r["document_id"]],"sha256":r["_sha256"],"split_method":"deterministic_supplier_group_approx_80_10_10; invoices without tax/name metadata grouped individually"})
    write_csv(ROOT/"invoice_split_manifest.csv",list(split_rows[0]),split_rows)

    # Inventory PDFs and searchable text counts before OCR starts.
    import pypdfium2 as pdfium
    inventory=[]
    for r in rows:
        doc=pdfium.PdfDocument(str(r["_pdf"]))
        chars=0
        try:
            for i in range(len(doc)):
                page=doc[i]; tp=page.get_textpage(); chars+=tp.count_chars(); tp.close(); page.close()
        finally: doc.close()
        inventory.append({"document_id":r["document_id"],"filename":r["_pdf"].name,"sha256":r["_sha256"],"page_count":int(r.get("page_count") or 0),"pdf_text_layer_chars":chars,"cached_paddleocr_available":False,"manual_verified_crops":0,"processing_status":"pending"})
    baseline=get_baseline_records()
    for item in inventory:
        row=next(r for r in rows if r["document_id"]==item["document_id"])
        cached=baseline.get(row["_pdf"].name)
        if cached and cached.get("source_pdf_sha256")==row["_sha256"] and cached.get("dpi")==DPI:
            item["cached_paddleocr_available"]=True
    write_csv(ROOT/"inventory.csv",list(inventory[0]),inventory)

    (ROOT/"README.md").write_text("""# PaddleOCR recognition data preparation\n\nThis folder contains copied active invoice PDFs, OCR line-crop candidates, confirmed manual labels, split manifests, review files, and exports. OCR transcripts are pseudo-labels until visually verified. Only rows explicitly marked verified may be used as supervised ground truth.\n\nOpen `review/review_queue.html` locally to review each crop beside its rendered PDF page. Filter by invoice, split, confidence, review status, or OCR text length; coordinates are shown for source lookup. Correct the transcript and choose **Xác nhận đúng** only after visual comparison. The recognition label limit is 90 characters; do not truncate text to pass the limit. Progress is saved in the browser; periodically click **Tải tiến độ JSON** for a backup.\n\nTo rebuild the verified dataset, save the downloaded file as `review/annotations.json`, then run:\n\n```powershell\n& """ + str(PROJECT / ".venv" / "Scripts" / "python.exe") + """ """ + str(ROOT / "prepare_recognition.py") + """\n```\n\nExisting OCR checkpoints are reused, so OCR inference is not repeated. The ZIP contains only human-confirmed crops. This folder prepares data; it does not train a model.\n""",encoding="utf-8")
    (ROOT/"COLAB_UPLOAD_GUIDE.md").write_text("""# Colab upload guide\n\n1. Finish visual review in `review/review_queue.html`; save its download as `review/annotations.json` and rerun `prepare_recognition.py` with the project `.venv`.\n2. Upload only `exports/verified_recognition_dataset.zip` to Google Drive. It contains only human-confirmed transcripts.\n3. In Colab, unzip the archive and inspect `verified/train.txt`, `verified/val.txt`, `verified/test.txt` and `verified_manifest.csv`.\n4. Confirm dataset paths and PaddleOCR dictionary/config before training.\n\nA ZIP with very few verified crops is not a useful fine-tuning set; see `FINETUNE_READINESS.md`.\n""",encoding="utf-8")

    selected=rows[:args.limit_invoices] if args.limit_invoices else rows
    completed=set()
    all_candidates=[]
    active_hashes = {r["document_id"]: r["_sha256"] for r in rows}
    for checkpoint in (ROOT/"checkpoints").glob("*.json"):
        try:
            data=json.loads(checkpoint.read_text(encoding="utf-8"))
            if data.get("source_pdf_sha256")==active_hashes.get(data.get("document_id")):
                completed.add(data["document_id"])
                all_candidates.extend(data.get("crops",[]))
        except (StopIteration,ValueError,KeyError):
            continue
    manual=verified_manual_rows(split_map)
    manual_counts=Counter(r["document_id"] for r in manual)
    # Inference is initialized only if at least one invoice lacks a verified cached checkpoint.
    needs_ocr=any(r["document_id"] not in completed and not (baseline.get(r["_pdf"].name) and baseline[r["_pdf"].name].get("source_pdf_sha256")==r["_sha256"] and baseline[r["_pdf"].name].get("dpi")==DPI) for r in selected)
    ocr=None
    if needs_ocr:
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME",str(PROJECT/"cache"/"paddlex"))
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK","True")
        os.environ.setdefault("OMP_NUM_THREADS","4")
        import paddle
        from paddleocr import PaddleOCR
        paddle.set_device("cpu")
        ocr=PaddleOCR(lang="vi",device="cpu",enable_mkldnn=False,use_doc_orientation_classify=False,use_doc_unwarping=False,use_textline_orientation=False)
    page_total=0
    for idx,row in enumerate(selected,1):
        invoice_id=row["document_id"]
        if invoice_id in completed:
            log(f"SKIP checkpoint {idx}/{len(selected)} {invoice_id}")
            continue
        checkpoint=ROOT/"checkpoints"/f"{invoice_id}.json"
        start=time.perf_counter()
        pages,crops,seconds,origin=extract_one(ocr,row,split_map[invoice_id],baseline)
        data={"document_id":invoice_id,"filename":row["_pdf"].name,"source_pdf_sha256":row["_sha256"],"dpi":DPI,"pages":len(pages),"ocr_seconds":round(seconds,3),"regions":len(crops),"ocr_source":origin,"crops":crops}
        checkpoint.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        all_candidates.extend(crops); page_total+=len(pages)
        log(f"DONE {idx}/{len(selected)} {invoice_id}: {len(pages)} pages, {len(crops)} candidates, source={origin}, inference={seconds:.1f}s, elapsed={time.perf_counter()-start:.1f}s")

    # Combine resumable checkpoints and re-import only confirmed manual labels.
    all_candidates=[]; ocr_times=[]
    valid_checkpoints=[]
    for p in (ROOT/"checkpoints").glob("*.json"):
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("source_pdf_sha256") != active_hashes.get(d.get("document_id")):
            continue
        valid_checkpoints.append(d)
        all_candidates.extend(d.get("crops",[])); ocr_times.append(d.get("ocr_seconds",0))
    by_checkpoint={d["document_id"]:d for d in valid_checkpoints}
    for item in inventory:
        done=by_checkpoint.get(item["document_id"])
        if done:
            item["page_count"]=done.get("pages",item["page_count"])
            item["ocr_candidate_crops"]=done.get("regions",0)
            item["manual_verified_crops"]=manual_counts[item["document_id"]]
            item["processing_status"]="processed"
            item["ocr_source"]=done.get("ocr_source","")
        else:
            item["manual_verified_crops"]=manual_counts[item["document_id"]]
            item["processing_status"]="pending"
    annotation_file=ROOT/"review"/"annotations.json"
    if annotation_file.exists():
        review_data=json.loads(annotation_file.read_text(encoding="utf-8-sig"))
        all_candidates=apply_review_annotations(all_candidates,review_data)
    reviewed_counts=Counter(r["document_id"] for r in all_candidates if r["label_status"]=="verified")
    for item in inventory:
        item["manual_verified_crops"]=manual_counts[item["document_id"]]+reviewed_counts[item["document_id"]]
    write_csv(ROOT/"inventory.csv",list(inventory[0]),inventory)
    rows_all=manual+all_candidates
    # Write master and per-split review tables.
    write_csv(ROOT/"crop_manifest.csv",CSV_FIELDS,rows_all)
    verified_rows=manual+[r for r in all_candidates if r["label_status"]=="verified"]
    for row in manual:
        row["training_image_path"]=row["crop_path"]
    for row in all_candidates:
        if row["label_status"]!="verified":
            continue
        source_image=ROOT/row["crop_path"]
        if not source_image.is_file():
            raise FileNotFoundError(source_image)
        target=ROOT/"verified"/"images"/row["split"]/(row["crop_id"]+".png")
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            shutil.copy2(source_image,target)
        row["training_image_path"]=target.relative_to(ROOT).as_posix()
    for split in ("train","val","test"):
        candidates=[r for r in all_candidates if r["split"]==split]
        write_csv(ROOT/"review"/split/"candidates.csv",CSV_FIELDS,candidates)
        verified=[r for r in verified_rows if r["split"]==split]
        lines=[]
        for r in verified:
            lines.append(f"images/{split}/{Path(r['training_image_path']).name}\t{r['transcript']}")
        (ROOT/"verified"/f"{split}.txt").write_text("\n".join(lines)+("\n" if lines else ""),encoding="utf-8")
    write_csv(ROOT/"verified"/"verified_manifest.csv",CSV_FIELDS+["training_image_path"],verified_rows)
    make_review_html(all_candidates)

    # Zip only confirmed labels; this may be too small to train and is not promoted as ready.
    export=ROOT/"exports"/"verified_recognition_dataset.zip"
    with zipfile.ZipFile(export,"w",zipfile.ZIP_DEFLATED) as z:
        for name in ("train.txt","val.txt","test.txt","verified_manifest.csv"):
            p=ROOT/"verified"/name
            z.write(p,p.relative_to(ROOT).as_posix())
        for r in verified_rows:
            p=ROOT/r["training_image_path"]
            z.write(p,p.relative_to(ROOT).as_posix())
        z.writestr("VERIFICATION_NOTICE.txt","Only human-confirmed crops are included. Check FINETUNE_READINESS.md; a small dataset is not necessarily suitable for training.\n")

    dict_chars=set(DICT.read_text(encoding="utf-8").splitlines()) if DICT.exists() else set()
    ood=Counter(ch for r in all_candidates for ch in r["raw_ocr_text"] if dict_chars and ch not in dict_chars and not ch.isspace())
    split_crop=Counter(r["split"] for r in all_candidates)
    pending=[r for r in all_candidates if r["label_status"]=="needs_review"]
    rejected=[r for r in all_candidates if r["label_status"]=="rejected"]
    overlength=[r for r in all_candidates if len(r.get("raw_ocr_text", ""))>MAX_LABEL_LENGTH]
    summary={"source_invoice_count":len(rows),"processed_invoice_count":len(valid_checkpoints),"source_page_count":sum(d.get("pages",0) for d in valid_checkpoints),"ocr_candidate_crop_count":len(all_candidates),"ocr_candidates_over_max_label_length":len(overlength),"max_label_length":MAX_LABEL_LENGTH,"verified_crop_count":len(verified_rows),"pending_review_crop_count":len(pending),"rejected_crop_count":len(rejected),"verified_by_split":dict(Counter(r["split"] for r in verified_rows)),"candidate_by_split":dict(split_crop),"invoice_split_counts":dict(split_counts),"invoice_split_targets":targets,"supplier_group_count":group_count,"unknown_dictionary_characters":ood.most_common(100),"fine_tune_ready":False,"reason":"Recognition export contains only human-confirmed labels; suitability for fine-tuning still requires enough verified crops and non-empty splits."}
    (ROOT/"reports"/"dataset_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"reports"/"quality_report.md").write_text(
        "# Crop data quality status\n\n"
        f"- Active PDFs: {len(rows)}\n- Processed PDFs: {summary['processed_invoice_count']}\n"
        f"- OCR crop candidates: {len(all_candidates)}\n- Confirmed crops (including imported manual labels): {len(verified_rows)}\n- Pending review: {len(pending)}\n- Rejected crops: {len(rejected)}\n"
        f"- OCR suggestions longer than {MAX_LABEL_LENGTH} characters: {len(overlength)} (inspect for multi-line/oversized regions)\n"
        f"- Candidate crops with confidence below 0.80: {sum(1 for r in all_candidates if r.get('confidence') not in ('',None) and float(r['confidence']) < 0.8)}\n"
        f"- Candidate crops with empty OCR transcript: {sum(1 for r in all_candidates if not r.get('raw_ocr_text','').strip())}\n"
        "\nOCR outputs are suggestions only until a human confirms them against the source page.\n",
        encoding="utf-8")
    (ROOT/"FINETUNE_READINESS.md").write_text(
        "# Fine-tune readiness\n\n"
        f"Current state: **not ready for supervised fine-tuning**. {len(verified_rows)} crop(s) have confirmed transcripts; by split: train={sum(r['split']=='train' for r in verified_rows)}, val={sum(r['split']=='val' for r in verified_rows)}, test={sum(r['split']=='test' for r in verified_rows)}. {len(pending)} candidate(s) still need review and {len(rejected)} were rejected. {len(overlength)} OCR suggestions exceed the {MAX_LABEL_LENGTH}-character recognition label limit and need visual inspection for oversized or multi-line regions.\n\n"
        "Verified training target: `PP-OCRv6_medium_rec` (`SVTR_LCNet`), using PaddleOCR 3.7.0 / PaddlePaddle 3.2.0, UTF-8 dictionary at `ocr_labeler/assets/ppocrv6_dict.txt`, input shape `[3, 48, 1152]`, and max label length 90 from `ocr_labeler/train_local.py`. The runner expects PaddleOCR source tag `v3.7.0` and config `configs/rec/PP-OCRv6/PP-OCRv6_medium_rec.yml`; those training source files are not currently present. The expected pretrained checkpoint is `PP-OCRv6_medium_rec_pretrained.pdparams`; it is also absent. Obtain/verify these before training.\n\n"
        "Edit and confirm crops in `review/review_queue.html`, download `review_annotations.json`, place it at `review/annotations.json`, then rerun `python prepare_recognition.py`. Existing OCR checkpoints are reused; inference is not repeated. The ZIP contains only confirmed labels. No training was run.\n",
        encoding="utf-8")
    metadata={"generated_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,"paddleocr":"3.7.0" if ocr is not None else "reused outputs; baseline metadata 3.7.0","paddlepaddle":"3.2.0; CPU inference" if ocr is not None else "reused outputs; baseline metadata 3.2.0","dpi":DPI,"device":"cpu","inference_model":"PP-OCRv6_medium_rec","training_model":"PP-OCRv6_medium_rec","training_config":"PaddleOCR v3.7.0 configs/rec/PP-OCRv6/PP-OCRv6_medium_rec.yml (expected; source absent locally)","training_checkpoint":"PP-OCRv6_medium_rec_pretrained.pdparams (expected; absent locally)","dictionary":str(DICT),"dictionary_sha256":sha256(DICT) if DICT.is_file() else None,"max_label_length":MAX_LABEL_LENGTH,"recognition_image_shape":[3,48,1152],"source_directory":str(PDF_DIR),"source_invoice_count":len(rows),"processed_invoice_count":summary['processed_invoice_count'],"ocr_candidate_crops":len(all_candidates),"verified_manual_crops":len(verified_rows),"source_checksums_verified":True,"training_run":False}
    (ROOT/"metadata.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    log(f"SUMMARY: PDFs={len(rows)}, processed={summary['processed_invoice_count']}, candidates={len(all_candidates)}, verified={len(verified_rows)}, pending={len(pending)}, rejected={len(rejected)}")


if __name__ == "__main__":
    main()
