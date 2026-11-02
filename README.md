# PaddleOCR invoice transcript review dataset

Repository chia sẻ bộ crop nhận dạng chữ PaddleOCR, công cụ rà transcript và dữ liệu chuẩn bị cho thử nghiệm fine-tune trên Google Colab.

> **Quyền riêng tư:** repository này công khai. Repository có 208 PDF hóa đơn, ảnh trang render, crop và transcript; nội dung có thể được bất kỳ ai tải xuống. Chỉ dùng các tài liệu này khi bạn có quyền chia sẻ.

## Trạng thái dữ liệu mới nhất

- 188 hóa đơn active (206 trang) nằm trong `recognition_dataset/source_300_invoices/pdfs/`; danh sách và checksum ở `source_manifest.csv`.
- `crop_manifest.csv` có 14.469 vùng crop; ảnh crop đều tồn tại tại đường dẫn trong manifest.
- Bộ export Colab có 12.551 dòng nhãn: 7.670 train, 2.359 validation và 2.522 test. Chia tập theo hóa đơn: 111 train, 40 validation, 37 test; các hóa đơn không có crop export vẫn được giữ trong manifest split.
- Theo `colab_finetune/dataset_manifest.csv`, nguồn nhãn ghi 12.549 dòng `ocr_pseudo_label` và 2 dòng từ crop được xác nhận trong công cụ gán nhãn. Phân loại nguồn gốc riêng ghi 392 dòng có bằng chứng rà soát của con người và 12.159 dòng tự động/chưa truy nguyên được; các nhóm này không đồng nghĩa với việc toàn bộ đã được kiểm tra bằng mắt.
- Tập hóa đơn đã được dùng trong các lần đánh giá OCR trước; kết quả trên tập này có tính chẩn đoán, không phải benchmark độc lập.
- WEB_242 và các hóa đơn bị loại khỏi dữ liệu active không nằm trong export; bản sao khôi phục cục bộ bị loại khỏi GitHub.
- Danh sách và manifest Colab: `recognition_dataset/colab_finetune/`. Ảnh crop được tham chiếu từ các thư mục đã có trong repository.

## Dùng dữ liệu trong Google Colab

Clone repository mới nhất trong Colab rồi đặt data root là thư mục `recognition_dataset`:

```bash
git clone --depth 1 https://github.com/nguyenhung1204/data_Transcript_Fine_tune.git
```

Đọc `recognition_dataset/colab_finetune/README.md` để nạp `train.txt`, `val.txt`, `test.txt` và ảnh crop. Chỉ dùng `train.txt` để cập nhật trọng số; dùng validation để chọn checkpoint; chỉ dùng test để đánh giá cuối và ghi rõ giới hạn của nhãn yếu/tái sử dụng.

Trước khi train, cần xác minh phiên bản PaddleOCR/PaddlePaddle, cấu hình Recognition, checkpoint nền và từ điển ký tự tương thích. Repository này chuẩn bị dữ liệu, không chứa checkpoint fine-tune đã xác minh. Xem `recognition_dataset/FINETUNE_READINESS.md`.

## Chạy công cụ rà nhãn trên Windows

Cần Python 3; không cần Node.js, Docker hoặc PaddleOCR để xem/copy chữ PDF:

```powershell
cd .\recognition_dataset
py -m http.server 8767 --bind 127.0.0.1
```

Mở `http://127.0.0.1:8767/review/review_queue.html`. Tiến độ trên trình duyệt được lưu cục bộ; sau khi nhập tiến độ mới, chạy `python recognition_dataset/export_colab_dataset.py` từ thư mục gốc để cập nhật danh sách train/val/test và manifest trước khi push.

Không ghi đè tiến độ của người khác. Khi nhiều người cùng rà, mỗi người cần gửi bản JSON riêng để gộp theo `crop_id`.
