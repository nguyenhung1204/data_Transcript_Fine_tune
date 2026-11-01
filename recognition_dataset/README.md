# PaddleOCR recognition data preparation

This folder contains copied active invoice PDFs, OCR line-crop candidates, confirmed manual labels, split manifests, review files, and exports. OCR transcripts are pseudo-labels until visually verified. Only rows explicitly marked verified may be used as supervised ground truth.

Open `review/review_queue.html` locally to review each crop beside its rendered PDF page. Filter by invoice, split, confidence, review status, or OCR text length; coordinates are shown for source lookup. Correct the transcript and choose **Xác nhận đúng** only after visual comparison. The recognition label limit is 90 characters; do not truncate text to pass the limit. Progress is saved in the browser; periodically click **Tải tiến độ JSON** for a backup.

To rebuild the verified dataset, save the downloaded file as `review/annotations.json`, then run:

```powershell
& E:\KhoaLuanTotNghiep\PaddleOCR_Field_Improvement\.venv\Scripts\python.exe E:\KhoaLuanTotNghiep\PaddleOCR_Field_Improvement\recognition_dataset\prepare_recognition.py
```

Existing OCR checkpoints are reused, so OCR inference is not repeated. The ZIP contains only human-confirmed crops. This folder prepares data; it does not train a model.


## Bộ dữ liệu Colab fine-tune

- Danh sách PaddleOCR Recognition và manifest: `recognition_dataset/colab_finetune/`.
- Chạy lại bộ xuất sau khi cập nhật nhãn: `python recognition_dataset/export_colab_dataset.py`.
- Ảnh crop được tham chiếu từ `recognition_dataset/crops/` và `recognition_dataset/verified/images/`; không nhân đôi ảnh trong thư mục export. Hướng dẫn nạp vào Colab ở `recognition_dataset/colab_finetune/README.md`.
