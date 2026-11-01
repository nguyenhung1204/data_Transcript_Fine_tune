# PaddleOCR invoice transcript review dataset

Repository chia sẻ bộ crop nhận dạng chữ PaddleOCR, công cụ rà transcript và dữ liệu chuẩn bị cho thử nghiệm fine-tune trên Google Colab.

> **Quyền riêng tư:** repository này công khai. Repository có 208 PDF hóa đơn, ảnh trang render, crop và transcript; nội dung có thể được bất kỳ ai tải xuống. Chỉ dùng các tài liệu này khi bạn có quyền chia sẻ.

## Trạng thái dữ liệu mới nhất

- 208 PDF nguồn đã được sao chép vào `recognition_dataset/source_300_invoices/pdfs/`; checksum khớp manifest.
- Có 17.961 crop trong manifest. Tiến độ rà hiện ghi 7.358 nhãn `verified`, 111 `rejected`, 20 `needs_review`; các crop còn lại chưa có quyết định rà.
- Bộ Colab được làm mới từ tiến độ hiện tại: 4.370 train, 1.297 validation, 1.691 test. Các split kế thừa manifest cấp hóa đơn; 104/36/31 hóa đơn có crop được xuất trong từng split.
- Trong 7.358 nhãn export, 396 có bằng chứng audit rà trực quan hoặc xác nhận ban đầu từ công cụ gán nhãn; 6.962 là xác nhận tự động theo PDF/OCR hoặc chưa truy nguyên được thành rà tay. Đây là bộ thử nghiệm có nhãn yếu, không được gọi toàn bộ là ground truth đã được người kiểm tra.
- Tập test đã từng được dùng trong các lần đánh giá trước; xem đây là kết quả chẩn đoán, không phải benchmark độc lập.
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
