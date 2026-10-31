# PaddleOCR invoice transcript review dataset

Repository chia sẻ bộ crop nhận dạng chữ PaddleOCR và công cụ để nhóm rà transcript theo từng hóa đơn.

> **Lưu ý về quyền riêng tư:** repository này hiện ở chế độ công khai. Gói có kèm 208 PDF hóa đơn, ảnh trang render, crop và dữ liệu nhận dạng; mọi người đều có thể tải và xem nội dung trong các hóa đơn.

## Trạng thái dữ liệu hiện tại

- 208 PDF hóa đơn đã được sao chép vào `recognition_dataset/source_300_invoices/pdfs/`; checksum SHA-256 khớp manifest nguồn.
- Có 17.959 crop OCR đang chờ người kiểm tra và 2 crop đã xác nhận.
- Transcript OCR chỉ là gợi ý. Không dùng crop `needs_review` làm nhãn chuẩn hoặc đưa vào train.
- Chia theo hóa đơn: 126 train, 41 validation, 41 test; các crop của cùng hóa đơn giữ cùng split.
- Bộ hiện **chưa đủ điều kiện fine-tune có giám sát**. Xem `recognition_dataset/FINETUNE_READINESS.md`.

## Cách mở web rà nhãn trên Windows

Cài Python 3 là đủ để mở công cụ rà nhãn; bước xem/copy PDF không cần PaddleOCR, Node.js hay Docker.

```powershell
cd .\recognition_dataset
py -m http.server 8767 --bind 127.0.0.1
```

Giữ cửa sổ PowerShell mở rồi truy cập:

`http://127.0.0.1:8767/review/review_queue.html`

Chọn **PDF gốc · copy chữ**, bôi đen chữ trên PDF, nhấn `Ctrl+C`, rồi dán vào ô transcript bằng `Ctrl+V`. Nếu PDF là scan ảnh và không chọn được chữ, dùng OCR gợi ý, phóng ảnh trang để so lại; không tự đoán chữ mờ.

## Lưu và gửi tiến độ rà nhãn

Trang web tự lưu tiến độ trong trình duyệt trên máy đang rà. Dữ liệu đó chưa tự đồng bộ lên GitHub. Hãy bấm **Tải tiến độ JSON** để tải file sao lưu định kỳ. Khi hoàn thành phần việc, gửi file JSON cho người tổng hợp hoặc đặt file ở `recognition_dataset/review/annotations.json`, commit và push lên nhánh của bạn.

Đừng ghi đè tiến độ của người khác. Nếu nhiều người cùng rà, mỗi người giữ JSON riêng; người tổng hợp sẽ gộp theo `crop_id` trước khi cập nhật manifest và export.

## Thành phần chính

- `recognition_dataset/review/review_queue.html`: công cụ rà crop cạnh PDF gốc.
- `recognition_dataset/crop_manifest.csv`: transcript gợi ý, trạng thái, tọa độ và nguồn của từng crop.
- `recognition_dataset/invoice_split_manifest.csv`: split ở cấp hóa đơn.
- `recognition_dataset/source_300_invoices/pdfs/`: các PDF gốc đã đóng gói.
- `recognition_dataset/rendered_pages/`, `crops/`: ảnh trang và crop tương ứng.
- `recognition_dataset/exports/verified_recognition_dataset.zip`: ZIP chỉ gồm các crop đã xác nhận hiện có; chưa đủ để fine-tune.

Các bước huấn luyện chưa được chạy. Cấu hình PaddleOCR và checkpoint huấn luyện nền cần được xác minh riêng trước khi fine-tune; xem `FINETUNE_READINESS.md`.
