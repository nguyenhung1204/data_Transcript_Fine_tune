# Báo cáo tự xác nhận transcript

- Chính sách: `pdf_ocr_agreement_v1`
- Tạo lúc UTC: 2026-11-02T20:41:26.050367+00:00
- Tổng crop: 14469
- Đủ điều kiện theo dry-run hiện tại: 0
- Đợt áp dụng gần nhất: 6767 transcript lúc 2026-11-01T09:50:47.922507+00:00
- Ngưỡng OCR1: confidence ≥ 0.90; transcript tối đa 90 ký tự, đúng một dòng.
- Nhãn thủ công được giữ nguyên: 6989
- OCR thứ hai: không có; đây chỉ là đồng thuận lớp chữ PDF + OCR1 PaddleOCR.
- Token xem trước hiện tại: `2bfc433ee89fbee9da8145d2ca45bb5487816bb96e0b366ea72cd341a29e9903`
- Sao lưu trước đợt áp dụng gần nhất: E:\KhoaLuanTotNghiep\data_Transcript_Fine_tune\recognition_dataset\automatic_review\manual_review_progress.backup_20261101_165047_922507.json

## Lý do giữ lại để rà tay

- `confidence_below_threshold`: 64
- `control_character`: 22
- `multiple_lines`: 15
- `overlength`: 336
- `pdf_ocr_disagree`: 1102
- `pending_draft_differs`: 10

Chỉ giá trị PDF text được giữ nguyên khi so khớp an toàn với OCR1. Bất đồng ký tự, dấu tiếng Việt, thiếu nguồn, confidence thấp hoặc hình học không hợp lệ sẽ không được tự sửa hay xác nhận.
