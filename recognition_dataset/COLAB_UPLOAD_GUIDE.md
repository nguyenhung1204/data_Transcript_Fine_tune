# Colab upload guide

1. Finish visual review in `review/review_queue.html`; download the review JSON and send it to the data owner or commit it as `review/annotations.json` on your branch.
2. The data owner merges distinct crop IDs into the original working project and regenerates `exports/verified_recognition_dataset.zip` from human-confirmed labels only.
3. Upload only that verified ZIP to Google Drive/Colab, unzip it, and inspect `verified/train.txt`, `verified/val.txt`, `verified/test.txt` and `verified_manifest.csv`.
4. Confirm the model dictionary/config and training checkpoint before training. This repository does not include the PaddleOCR training config or pretrained checkpoint.

A ZIP with very few verified crops is not a useful fine-tuning set; see `FINETUNE_READINESS.md`. This repository does not run training.
