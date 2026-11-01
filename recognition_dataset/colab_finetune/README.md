# Colab dataset input

This folder contains PaddleOCR Recognition label lists generated from the latest review progress. Clone the public repository in a Colab runtime, then set the dataset root to the cloned repository's `recognition_dataset` directory.

```bash
git clone --depth 1 https://github.com/nguyenhung1204/data_Transcript_Fine_tune.git
cd data_Transcript_Fine_tune
```

Use `recognition_dataset/colab_finetune/train.txt`, `val.txt`, and `test.txt`. Each row is `relative_image_path<TAB>transcript`; paths are relative to `recognition_dataset/`, for example `crops/HD_001/<crop-id>.png`. Resolve images as `DATA_ROOT / relative_image_path`. The two original labeler crops use the tracked paths under `verified/images/`. The image bytes remain in the repo's existing crop directories and are not duplicated here.

Before training, verify the model config, base checkpoint, and character dictionary match. The repository currently has no confirmed trained checkpoint. `ppocrv6_dict.txt` is only a candidate dictionary until compatibility is established.

## Label quality caveat

The progress status `verified` includes automatic PDF-text/OCR agreement confirmations. It does not mean that every transcript was manually inspected. `dataset_manifest.csv` records the available evidence per crop; the current export has 396 entries with manual audit evidence and 6,962 that are automatic confirmations or not traceable to manual review. Treat this export as a pilot/weakly supervised dataset. Do not present test results on these labels as independent human-ground-truth accuracy.

To rebuild after label changes, run `python recognition_dataset/export_colab_dataset.py` from the repository root.
