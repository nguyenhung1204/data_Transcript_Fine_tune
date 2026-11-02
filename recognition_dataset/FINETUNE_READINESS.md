# Current active dataset status — 2026-11-03

At the user’s request, **WEB_242** and all **56** associated crop records were excluded from the active dataset. The original source PDF remains unchanged. A local recovery copy exists on the owner’s computer and is intentionally not included in this public repository.

- Active inventory: **188 invoices / 206 pages**; all 188 active PDFs match the included rows in `source_manifest.csv`.
- Active crop manifest: **14,469** rows; every referenced crop image exists.
- `manual_review_progress.json`: **13,401** records — 13,323 `verified`, 36 `needs_review`, and 42 `rejected`.
- Colab recognition export: **12,551** rows — 7,670 train, 2,359 validation, 2,522 test. The invoice split manifest contains 111/40/37 invoices respectively.
- Export provenance: 392 rows have human-review evidence; 12,159 are automatic or untraced. The export manifest also records 12,549 `ocr_pseudo_label` sources and 2 original labeler-confirmed crops. Do not treat all exported transcripts as visually verified ground truth.
- Test invoices were used in earlier OCR evaluations; results are diagnostic, not an independent benchmark.
- **WEB_242** is absent from active crop/PDF manifests, review progress, and Colab export.

Previous status notes below are historical snapshots.

---

# Historical dataset update — 2026-11-02T18:55:48.792793+00:00

At the user's request, WEB_076–WEB_081 and their **408 crop records** were removed from active review/training data. The six working PDFs, crops, rendered pages, checkpoints, manifests, progress and SQLite state from before the removal are preserved in `excluded_invoice_backups/WEB_076_077_078_079_080_081_20261102T185332976762Z/`. The original source PDFs in `HoaDonBanHang_300` remain intact.

- Active PDFs: **189**; active crop records: **16,049**.
- OCR candidates: **16,047**; verified recognition crops: **2**.
- Invoice splits: **111 train / 40 validation / 38 test**.
- Removed manual-progress entries: **3**.

---

 Historical dataset update — WEB_012/013/014/015/016/022/024 (2026-11-03)

Excluded 7 invoices and **731 crops** from active data. The 144 associated progress annotations were removed and the Colab recognition export regenerated. Recovery copies are in `excluded_invoice_backups/WEB_012_013_014_015_016_022_024_20261103T003645839788/`; original source PDFs were left unchanged.

- Active PDFs: **195**; active crop records: **16,457**.
- OCR candidates: **16,455**; confirmed recognition crops: **2**.
- Invoice splits: **114 train / 40 validation / 41 test**.
- This active-state note supersedes the older snapshots below.

---

# Historical dataset update — 2026-11-03

`WEB_011.pdf` and its 144 associated crops are excluded from the active review/training data. The local working PDF, crop images, rendered page, and per-invoice checkpoint are preserved for recovery under `excluded_invoice_backups/WEB_011_20261103T002311608941/`. The original source PDF was not changed.

- Active PDFs: **202**; active crop records: **17188**.
- OCR candidates: **17186**; confirmed crops in recognition manifest: **2**.
- Invoice split counts: `{"val": 41, "train": 120, "test": 41}`.
- The Colab export was regenerated after exclusion. The dated sections below are historical snapshots.

---

# Fine-tune readiness snapshot — WEB_003_20261102T145710Z

## Current Colab export

`colab_finetune/` was regenerated after excluding WEB_003 and all 69 crops.

- Exported: **12266** crops — train **7399**, val **2399**, test **2468**.
- Remaining active PDFs: **205**; active crops: **17558**.
- Remaining progress annotations: verified **12266**, rejected **273**, needs review **37**.
- Export provenance: **396** manual-review evidence; other verified-status crops have weaker/untraced provenance.
- Test invoices/crops were used in earlier OCR work; results are diagnostic, not an independent benchmark.
- Re-export after review changes with `py recognition_dataset/export_colab_dataset.py` from the repository root.

## Model readiness

The repository does not contain a verified trained checkpoint. Before training, confirm the exact PaddleOCR Recognition config, base checkpoint, character dictionary, and compatible PaddleOCR/PaddlePaddle versions. `model_assets/ppocrv6_dict.txt` is a candidate only; do not infer compatibility from its filename.

Recognition fine-tuning teaches the model to read text inside supplied crops. It does not train page text detection, invoice layout understanding, or field assignment. Do not report a fine-tune as successful until Colab training completes and the baseline and tuned models are evaluated on the same held-out crops with the same inference procedure.

## Active crop data quality

- Active PDFs: **206**
- Processed PDFs: **206**
- OCR crop candidates: **17625**
- Total active crop records: **17627**
- Excluded: HD_016 (Korean product text), WEB_001 (blurry scan; 203 crops).

## Active crop data quality

- Active PDFs: **205**
- Processed PDFs: **205**
- OCR crop candidates: **17556**
- Total active crop records: **17558**
- Excluded: HD_016 (Korean product text), WEB_001 (blurry scan; 203 crops), WEB_003 (user-requested; 69 crops).


## Cập nhật bộ dữ liệu active — 20261102T153653175676Z

- Đã loại `WEB_004.pdf` khỏi tập active theo yêu cầu; 119 crop của hóa đơn không còn trong hàng đợi, manifest hoặc checkpoint.
- PDF nguồn được giữ nguyên; bản làm việc và ảnh crop được lưu trong `excluded_invoice_backups/WEB_004_20261102T153653175676Z/` để có thể khôi phục.
