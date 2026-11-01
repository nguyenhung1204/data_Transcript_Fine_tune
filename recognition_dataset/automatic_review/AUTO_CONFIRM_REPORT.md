# Báo cáo tự xác nhận transcript

- Chính sách: `pdf_ocr_agreement_v1`
- Tạo lúc UTC: 2026-11-01T16:42:26.744809+00:00
- Tổng crop: 17961
- Đủ điều kiện theo dry-run hiện tại: 0
- Đợt áp dụng gần nhất: 6767 transcript lúc 2026-11-01T09:50:47.922507+00:00
- Ngưỡng OCR1: confidence ≥ 0.90; transcript tối đa 90 ký tự, đúng một dòng.
- Nhãn thủ công được giữ nguyên: 866
- OCR thứ hai: không có; đây chỉ là đồng thuận lớp chữ PDF + OCR1 PaddleOCR.
- Token xem trước hiện tại: `534d4599c7c5a5fd62b1b512f0743adc90734310d0bd6f429c26535e352d082b`
- Sao lưu trước đợt áp dụng gần nhất: E:\KhoaLuanTotNghiep\data_Transcript_Fine_tune\recognition_dataset\automatic_review\manual_review_progress.backup_20261101_165047_922507.json

## Lý do giữ lại để rà tay

- `confidence_below_threshold`: 618
- `control_character`: 82
- `multiple_lines`: 63
- `overlength`: 356
- `pdf_ocr_disagree`: 10521
- `pdf_text_missing`: 3206
- `pending_draft_differs`: 7

Chỉ giá trị PDF text được giữ nguyên khi so khớp an toàn với OCR1. Bất đồng ký tự, dấu tiếng Việt, thiếu nguồn, confidence thấp hoặc hình học không hợp lệ sẽ không được tự sửa hay xác nhận.
