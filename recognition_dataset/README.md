# PaddleOCR recognition data preparation

This package contains copied active invoice PDFs, rendered pages, OCR crop candidates, split manifests, review workflow and exports. OCR transcripts are suggestions only until a person visually checks them against the source PDF.

## Open the review page on Windows

Install Python 3. From this folder, run:

```powershell
py -m http.server 8767 --bind 127.0.0.1
```

Keep that terminal open and visit `http://127.0.0.1:8767/review/review_queue.html`.

In the right pane choose **PDF gốc · copy chữ**. If the PDF has a text layer, select the text and press Ctrl+C, then paste into the transcript field with Ctrl+V. Scanned image PDFs do not have selectable text; compare the OCR suggestion against the rendered page and correct only what is readable.

## Save review progress

Progress is stored in that browser profile, not automatically shared through GitHub. Click **Tải tiến độ JSON** regularly. When your assigned review is complete, put the downloaded file at `review/annotations.json` in your branch and commit/push it, or send it to the data owner. Avoid overwriting another reviewer's progress; the owner must combine distinct crop IDs before rebuilding the export.

## Current data state

- 208 active invoice PDFs are included; the copied PDF checksums match the source manifest.
- There are 17,959 OCR candidates awaiting review and 2 manually confirmed crops.
- Invoice-level split: 126 train, 41 validation, 41 test. Crops from one invoice stay in the same split.
- This dataset is **not yet ready for supervised fine-tuning**. Do not use `needs_review` transcripts as ground truth.
- The recognition dictionary used for the preparation metadata is included at `model_assets/ppocrv6_dict.txt` (SHA-256: 769e7fa79bb297b5f18d8dbd149e364a45bc61f2b3f574e5ea836f0b261c23a6). The PaddleOCR training config and pretrained checkpoint are not included; see `FINETUNE_READINESS.md`.

`exports/verified_recognition_dataset.zip` contains only the currently confirmed crops and is not a useful training set yet.
