# Fine-tune readiness

Current state: **not ready for supervised fine-tuning**. 2 crop(s) have confirmed transcripts; by split: train=1, val=1, test=0. 17959 candidate(s) still need review and 0 were rejected. 323 OCR suggestions exceed the 90-character recognition label limit and need visual inspection for oversized or multi-line regions.

Verified training target: `PP-OCRv6_medium_rec` (`SVTR_LCNet`), using PaddleOCR 3.7.0 / PaddlePaddle 3.2.0, UTF-8 dictionary at `ocr_labeler/assets/ppocrv6_dict.txt`, input shape `[3, 48, 1152]`, and max label length 90 from `ocr_labeler/train_local.py`. The runner expects PaddleOCR source tag `v3.7.0` and config `configs/rec/PP-OCRv6/PP-OCRv6_medium_rec.yml`; those training source files are not currently present. The expected pretrained checkpoint is `PP-OCRv6_medium_rec_pretrained.pdparams`; it is also absent. Obtain/verify these before training.

Edit and confirm crops in `review/review_queue.html`, download `review_annotations.json`, place it at `review/annotations.json`, then rerun `python prepare_recognition.py`. Existing OCR checkpoints are reused; inference is not repeated. The ZIP contains only confirmed labels. No training was run.
