# Nạp bộ dữ liệu vào Google Colab

## Dùng export cập nhật trên GitHub

Mở notebook Colab, bật GPU nếu có, rồi chạy một cell để lấy bản dữ liệu mới nhất:

```bash
!git clone --depth 1 https://github.com/nguyenhung1204/data_Transcript_Fine_tune.git /content/data_Transcript_Fine_tune
```

Trong Python:

```python
from pathlib import Path
DATA_ROOT = Path('/content/data_Transcript_Fine_tune/recognition_dataset')
TRAIN_LIST = DATA_ROOT / 'colab_finetune/train.txt'
VAL_LIST = DATA_ROOT / 'colab_finetune/val.txt'
TEST_LIST = DATA_ROOT / 'colab_finetune/test.txt'
```

Mỗi dòng danh sách có dạng `đường_dẫn_ảnh<TAB>transcript`. Ảnh crop có sẵn trong repository; ghép đường dẫn ảnh với `DATA_ROOT`. Dùng `train.txt` để cập nhật trọng số, `val.txt` để chọn checkpoint, và chỉ dùng `test.txt` sau khi chọn xong cấu hình.

Export hiện có 7.358 crop (4.370 train, 1.297 validation, 1.691 test). Trong đó 396 có bằng chứng rà trực quan/nhãn gốc và 6.962 là xác nhận PDF/OCR tự động hoặc chưa truy nguyên được rà tay. Vì vậy đây là pilot có nhãn yếu; test đã từng xuất hiện trong đánh giá OCR trước đó.

## Trước khi chạy huấn luyện

Đọc `FINETUNE_READINESS.md` và xác minh cấu hình Recognition, checkpoint nền, từ điển ký tự và phiên bản PaddleOCR/PaddlePaddle tương thích với notebook. Không dùng tên tệp làm bằng chứng tương thích. Recognition chỉ học đọc crop; nó không học phát hiện bố cục hoặc gán nội dung vào trường hóa đơn.

`exports/verified_recognition_dataset.zip` là archive riêng của luồng gán nhãn thủ công cũ; không dùng archive đó thay cho export 7.358 crop ở `colab_finetune/`.
