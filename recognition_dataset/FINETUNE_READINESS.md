# Fine-tune readiness (snapshot 2026-11-02)

## Dataset

`colab_finetune/` contains PaddleOCR Recognition `train.txt`, `val.txt`, and `test.txt`, plus `dataset_manifest.csv` and `dataset_summary.json`. It was generated from the latest `automatic_review/manual_review_progress.json` and `automatic_review/automatic_review_manifest.csv`.

- 7,292 crops have progress status `verified`: 4,370 train, 1,258 validation, 1,664 test.
- These labeled crops come from 104/36/31 invoices by split; invoice grouping is preserved. Other invoices may have no verified crop yet.
- 396 labels have a manual review audit record or original labeler confirmation. The remaining 6,896 are automatic PDF-text/OCR confirmations or otherwise not traceable to a manual review in the current audit files. The auto-confirm history indicates no independent second OCR was available. Treat these as weak labels, not human ground truth.
- The test set is not a fully independent human-verified benchmark. Report manual-audit and automatic-confirmation subsets separately where possible. Some invoices overlap prior OCR evaluation work.
- The exported labels meet the current 90-character cap and reference existing tracked crop images; images are not duplicated in the export folder.

## Model artifacts

The repository does not contain a verified fine-tune checkpoint. Before training, identify and verify the Recognition model configuration, matching character dictionary, PaddleOCR/PaddlePaddle version, and base pretrained checkpoint. Do not infer compatibility from a filename or use an unrelated checkpoint. The dictionary candidate is `model_assets/ppocrv6_dict.txt`; verify it matches the selected base model.

No fine-tuning has been run by creating this dataset export. It only prepares the current labels for a Colab experiment. Recognition training improves reading text inside a crop; it does not train invoice layout detection or field assignment.

Regenerate the export after changes with `python recognition_dataset/export_colab_dataset.py`. See `colab_finetune/README.md` for Colab loading instructions.
