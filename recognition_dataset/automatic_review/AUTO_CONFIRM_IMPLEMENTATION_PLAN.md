# Xác nhận transcript đủ bằng chứng — kế hoạch triển khai

**Mục tiêu:** Tự xác nhận crop chỉ khi lớp chữ PDF theo tọa độ khớp OCR1 tin cậy; giữ mọi mục nghi ngờ ở trạng thái chờ rà.

**Cách làm:** Đặt policy thuần Python dùng chung cho dry-run và API áp dụng. Server đọc manifest và tiến độ mới nhất, xác minh PDF/crop, tạo bản sao lưu trước khi ghi; giao diện chỉ áp dụng sau thao tác bấm riêng của người dùng.

**Phạm vi:** `automatic_review/auto_confirm.py`, `serve_review.py`, `review_queue.html`, test trong `automatic_review/tests/`, cùng `AUTO_CONFIRM_REPORT.md` và `auto_confirm_preview.json`. Không sửa PDF, crop nguồn, manifest nguồn, tiến độ khi dry-run, hoặc dữ liệu ngoài thư mục này.

## Các bước

1. Viết test policy cho đồng thuận PDF/OCR1, chuẩn hóa khoảng trắng dấu câu, confidence, độ dài, dòng, ký tự lỗi, file/checksum/tọa độ, nhãn thủ công và bản nháp người dùng; xác nhận test đỏ.
2. Cài policy server-side và chạy lại test xanh.
3. Thêm preview/apply API: preview không ghi tiến độ; apply yêu cầu token của dry-run hiện hành, đọc lại trạng thái mới nhất, bỏ qua nhãn đã rà, sao lưu và ghi atomic kèm bằng chứng từng mục.
4. Thêm panel dry-run và nút áp dụng riêng trong web; hiển thị lý do tổng hợp cho mục còn chờ, không hiện cảnh báo cho mục đã tự xác nhận.
5. Chạy test/API checks và dry-run trên bộ dữ liệu hiện tại; ghi số liệu, giới hạn OCR2 và trạng thái áp dụng vào `AUTO_CONFIRM_REPORT.md`.

## Tiêu chí kiểm tra

- Chỉ PDF text/OCR1 khớp an toàn, checksum/file/crop/hộp hợp lệ, một dòng, tối đa 90 ký tự, confidence PaddleOCR hợp lệ từ 0.90, và không có ký tự điều khiển/lỗi mới được đề xuất.
- Nhãn verified/rejected thủ công và bản nháp chờ rà khác PDF không bị ghi đè.
- Dry-run không thay đổi `manual_review_progress.json`.
- Apply dùng token stale sẽ bị từ chối; apply thành công tạo backup trước và giữ lại mọi annotation hiện tại.
- Nút chép chữ vẫn chỉ điền nháp; nút để rà sau vẫn lưu pending và chuyển mục.
