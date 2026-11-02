# Current active dataset status — 2026-11-02T20:38:12.312432+00:00

At the user’s request, **WEB_242** and all **56** associated crop records were excluded from the active dataset. The working PDF, rendered page, crop images, checkpoint and invoice-specific audit are preserved in `E:\KhoaLuanTotNghiep\data_Transcript_Fine_tune\recognition_dataset\excluded_invoice_backups\WEB_242_20261102T203812312432Z`; the original source PDF remains unchanged.

- Active inventory: **188 invoices / 206 pages**.
- Active crop records: **14469**; verified Colab labels: **12551**; pending: **1104**; rejected: **42**.
- Invoice splits: **111 train/40 val/37 test**.
- Removed WEB_242 progress entries: **36**; WEB_242 is absent from active manifests, review queues and Colab export.

Previous status notes below are historical snapshots.

---

# Historical dataset update — 2026-11-02T18:55:48.792793+00:00

At the user's request, WEB_076–WEB_081 and their **408 crop records** were removed from active review/training data. The six working PDFs, crops, rendered pages, checkpoints, manifests, progress and SQLite state from before the removal are preserved in `excluded_invoice_backups/WEB_076_077_078_079_080_081_20261102T185332976762Z/`. The original source PDFs in `HoaDonBanHang_300` remain intact.

- Active PDFs: **189**; active crop records: **16,049**.
- OCR candidates: **16,047**; verified recognition crops: **2**.
- Invoice splits: **111 train / 40 validation / 38 test**.
- Removed manual-progress entries: **3**.

---

 Historical dataset update — 2026-11-03

Excluded at the user's request: WEB_012, WEB_013, WEB_014, WEB_015, WEB_016, WEB_022, WEB_024. Removed **731 crop records** from the active manifests and review queue, removed **144 progress annotations**, regenerated the Colab export, and preserved working PDFs/crops/rendered pages/checkpoints in `excluded_invoice_backups/WEB_012_013_014_015_016_022_024_20261103T003645839788/`. The original source PDFs were not changed.

- Active PDFs: **195**; active crop records: **16457**.
- OCR candidates: **16455**; confirmed recognition crops: **2**.
- Invoice split counts: `{"val": 40, "train": 114, "test": 41}`.
- Older sections below are historical snapshots.

---

> **Cập nhật active 20261103:** `WEB_011.pdf` và 144 crop đã được loại khỏi dữ liệu rà soát hiện hành; số còn lại **202 hóa đơn / 17.188 crop**. Bản làm việc, 144 crop, trang render và checkpoint được lưu trong `../excluded_invoice_backups/WEB_011_20261103T002311608941/`. PDF nguồn không bị sửa. Các số liệu bên dưới là lịch sử trước lần loại này.

> **Cập nhật active 20261102T153653175676Z:** `WEB_004.pdf` và 119 crop đã bị loại khỏi hàng đợi hiện hành. Số liệu lịch sử bên dưới ghi nhận lần chạy trước khi loại hóa đơn này.

> Active dataset update 20261102T145710Z: WEB_003 and its 69 crops were excluded; 205 invoices and 17558 crops remain. The older counts below describe the original automatic-review run.

> Active dataset update 20261102T142619Z: WEB_001 and its 203 crops were excluded; 206 invoices and 17627 crops remain. The older counts below describe the original automatic-review run.

> Cập nhật HD_016_20261102T140159Z: HD_016 bị loại khỏi bộ active vì có chữ tiếng Hàn trong tên hàng. Hiện còn 207 hóa đơn và 17830 crop. Các số liệu lần chạy bên dưới là trước khi loại hóa đơn này.

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
