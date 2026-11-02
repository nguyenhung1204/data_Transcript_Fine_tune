# Current active dataset status — 2026-11-02T20:38:12.312432+00:00

At the user’s request, **WEB_242** and all **56** associated crop records were excluded from the active dataset. The working PDF, rendered page, crop images, checkpoint and invoice-specific audit are preserved in `E:\KhoaLuanTotNghiep\data_Transcript_Fine_tune\recognition_dataset\excluded_invoice_backups\WEB_242_20261102T203812312432Z`; the original source PDF remains unchanged.

- Active inventory: **188 invoices / 206 pages**.
- Active crop records: **14469**; verified Colab labels: **12551**; pending: **1104**; rejected: **42**.
- Invoice splits: **111 train/40 val/37 test**.
- Removed WEB_242 progress entries: **36**; WEB_242 is absent from active manifests, review queues and Colab export.

Previous status notes below are historical snapshots.

---

# Current active dataset update — 2026-11-02T18:55:48.792793+00:00

At the user's request, WEB_076–WEB_081 and their **408 crop records** were removed from active review/training data. The six working PDFs, crops, rendered pages, checkpoints, manifests, progress and SQLite state from before the removal are preserved in `excluded_invoice_backups/WEB_076_077_078_079_080_081_20261102T185332976762Z/`. The original source PDFs in `HoaDonBanHang_300` remain intact.

- Active PDFs: **189**; active crop records: **16,049**.
- OCR candidates: **16,047**; verified recognition crops: **2**.
- Invoice splits: **111 train / 40 validation / 38 test**.
- Removed manual-progress entries: **3**.

---

 Crop data quality status

- Active PDFs: 195
- Processed PDFs: 195
- OCR crop candidates: 16455
- Confirmed crops in recognition manifest: 2
- Pending review: 16455
- Rejected OCR candidates: 0
- OCR suggestions longer than 90 characters: 312
- Candidate crops with confidence below 0.80: 157
- Candidate crops with empty OCR transcript: 0
- Active crop records: 16457
- Invoice split counts: {"val": 40, "train": 114, "test": 41}
- Recorded exclusions: WEB_176: Hóa đơn scan quá mờ, chữ khó đọc để tạo transcript đáng tin cậy. (66 crop); WEB_004: Excluded at user's request because it still appeared in the unreviewed crop queue. (119 crop); WEB_005: User requested removal because the invoice contains handwritten/overwritten content unsuitable for the active recognition dataset. (107 crop); WEB_011: Excluded at user request; remove invoice and all crops from active dataset (144 crop); WEB_012: User requested exclusion from active dataset (84 crop); WEB_013: User requested exclusion from active dataset (144 crop); WEB_014: User requested exclusion from active dataset (95 crop); WEB_015: User requested exclusion from active dataset (109 crop); WEB_016: User requested exclusion from active dataset (101 crop); WEB_022: User requested exclusion from active dataset (90 crop); WEB_024: User requested exclusion from active dataset (108 crop)

OCR outputs are suggestions until checked against the source page. Excluded invoice assets are preserved only in recovery backups; original source PDFs were not modified.
