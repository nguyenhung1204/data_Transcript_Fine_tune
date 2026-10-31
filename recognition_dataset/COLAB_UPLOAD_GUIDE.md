# Colab upload guide

1. Finish visual review in `review/review_queue.html`; save its download as `review/annotations.json` and rerun `prepare_recognition.py` with the project `.venv`.
2. Upload only `exports/verified_recognition_dataset.zip` to Google Drive. It contains only human-confirmed transcripts.
3. In Colab, unzip the archive and inspect `verified/train.txt`, `verified/val.txt`, `verified/test.txt` and `verified_manifest.csv`.
4. Confirm dataset paths and PaddleOCR dictionary/config before training.

A ZIP with very few verified crops is not a useful fine-tuning set; see `FINETUNE_READINESS.md`.
