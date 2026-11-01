# Fine-tune readiness snapshot — 2026-11-02

## Current Colab export

`colab_finetune/` was regenerated from the latest `automatic_review/manual_review_progress.json` and `automatic_review/automatic_review_manifest.csv`.

- Exported: **7,358** crops — train **4,370**, validation **1,297**, test **1,691**.
- Exported crops come from 104/36/31 invoices respectively. Split is inherited from the invoice-level manifest; no invoice leakage was detected.
- Progress file currently records 7,358 `verified`, 111 `rejected`, and 20 `needs_review` annotations. The remaining manifest crops do not yet have a review decision.
- Provenance in the export: **396** crops have a manual-review audit record or original labeler confirmation; **6,962** are automatic PDF/OCR confirmations or cannot be traced to manual review. The automatic confirmations did not have independent OCR2 evidence. Treat these as weak labels, not human ground truth.
- The test invoices/crops have been used in earlier OCR work. Results are diagnostic, not an independent benchmark. Report human-audited and weak-label subsets separately when possible.
- All exported transcripts pass the current 90-character limit and reference existing crop images. The exporter validates blank/oversized labels, image paths, and split consistency.

To refresh after review changes, run from repository root:

```powershell
py recognition_dataset/export_colab_dataset.py
```

Then verify `colab_finetune/dataset_summary.json` and commit the progress JSON and refreshed export together. In Colab, clone the latest repository and resolve image paths relative to `recognition_dataset/` as described in `colab_finetune/README.md`.

## Model readiness

The repository does not contain a verified trained checkpoint. Before training, confirm the exact PaddleOCR Recognition config, base checkpoint, character dictionary, and compatible PaddleOCR/PaddlePaddle versions. `model_assets/ppocrv6_dict.txt` is a candidate only; do not infer compatibility from its filename.

Recognition fine-tuning teaches the model to read text inside supplied crops. It does not train page text detection, invoice layout understanding, or field assignment. Do not report a fine-tune as successful until Colab training completes and the baseline and tuned models are evaluated on the same held-out crops with the same inference procedure.
