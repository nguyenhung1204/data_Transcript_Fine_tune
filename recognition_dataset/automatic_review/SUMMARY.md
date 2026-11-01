# Tóm tắt rà soát tự động crop

- Thời điểm hoàn tất (UTC): `2026-11-01T09:07:40.204853+00:00`
- PDF/hoá đơn đã rà: **208**
- Crop trong manifest: **17961**
- Lớp chữ PDF có nội dung trong crop: **14656/17961**
- Thứ tự chữ PDF được dựng từ tọa độ ký tự theo thứ tự nhìn thấy; nút trên web chỉ chép bản nháp, không tự xác nhận nhãn.
- Lớp chữ PDF khớp OCR cũ sau chuẩn hoá Unicode NFC và khoảng trắng: **6803/17961**
- Nhãn xác nhận thủ công được giữ nguyên: **2**
- Crop cần rà tay: **17959**
- Crop đồng thuận máy: **0**
- Hộp crop sai/ngoài trang: **0**; crop có nhiều dòng chữ PDF: **90**

## Lý do chưa tự xác nhận

Môi trường không có OCR độc lập thứ hai đã cấu hình. Theo tiêu chí an toàn, nhãn chỉ được tự xác nhận khi lớp chữ PDF, OCR hiện có và OCR thứ hai đồng thuận; do thiếu OCR thứ hai, kết quả PDF khớp OCR cũ chỉ là bằng chứng hỗ trợ, không phải nhãn chuẩn.
Không cài thêm package, không tải model, không tạo ZIP fine-tune rỗng. Hai nhãn đã xác nhận thủ công trong nguồn được giữ trạng thái riêng, không bị ghi đè.

## File đầu ra

- `automatic_review_manifest.csv`: toàn bộ crop và kết quả đối chiếu.
- `needs_review.csv`: tất cả crop còn chờ người xem.
- `train_val_needs_review.csv`: các crop train/validation đang chờ; chưa dùng làm nhãn huấn luyện.
- `test_candidates.csv`: test được tách riêng, không đưa vào train/validation.
- `summary.json`, `metadata.json`, `run.log`, `checkpoint.json`.
- Không có `auto_consensus_train_val.zip`: chưa có crop nào đủ điều kiện đồng thuận ba nguồn.

## Giới hạn

PDF không có lớp text hoặc lớp text không khớp vùng crop sẽ vẫn cần rà tay. OCR cũ được tái dùng từ manifest; chưa chạy OCR độc lập thứ hai. Việc so khớp chính xác không tự sửa khác biệt ký tự hay dấu tiếng Việt.
