# Tập train — nhật ký rà soát thủ công

## Khởi động

- Bắt đầu (UTC): 2026-11-01T13:04:20.809483+00:00
- Crop train theo manifest: 11124
- Hóa đơn train: 127
- Trạng thái ban đầu: {'verified': 4246, 'needs_review': 6872, 'rejected': 6}
- Nhãn verified theo nguồn: {'<none>': 42, 'pdf_ocr_agreement_v1': 4204}
- Sao lưu tiến độ trước rà: `manual_review_progress.backup_train_visual_review_20261101_130420.json`
- Phạm vi: chỉ `split=train`; tuyệt đối không ghi vào val/test.
- Chưa có crop nào được xác nhận thủ công trong lượt này.

## Đợt rà trực quan tiếp theo — 2026-11-01

- Phạm vi đợt: 3 crop thuộc `train`, xem ảnh crop trực tiếp.
- Xác nhận đúng: 1 (`62d01ac44e0ca52a483a`) — transcript `Cốc sạc Apple 20W USB-C Power Adapter, Wty 1`.
- Loại: 1 (`39ba02ce41b2fd6be53f`) — crop địa chỉ nhiều dòng, bị cắt ở dòng dưới.
- Còn chờ: 1 (`8722d3872eea050200b2`) — nội dung đọc rõ nhưng dài 95 ký tự, vượt giới hạn 90; không rút gọn.
- Đã sao lưu trước lưu: `manual_review_progress.backup_visual_batch_20261101_200731.json`; API lưu 2 quyết định và đọc lại xác nhận thành công.
- Trạng thái train sau đợt: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (tổng 11124/11124).

## Đợt rà trực quan — HD_002, phần đầu

- Đã xem 6 crop auto-confirmed (`pdf_ocr_agreement_v1`) và đối chiếu ảnh trang HD_002.pdf. Cả 6 transcript đều khớp ảnh; đã đổi provenance thành `manual_visual_review`, giữ nguyên transcript.
- Gồm: `(Unit price)`, `(Description)`, `6=4x5`, `2`, `1`, `3`.
- Tiến độ train hiện tại: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (tổng 11124/11124).
- Backup trước đợt: `manual_review_progress.backup_visual_batch_20261101_200838.json`; API lưu 6 mục và đọc lại xác minh thành công.

## Đợt rà trực quan — HD_002, dòng hàng

- Đã xem 10 crop được PDF/OCR tự xác nhận và đối chiếu trang 1 HD_002.pdf. Cả 10 transcript khớp nội dung nhìn thấy; đã đổi provenance sang `manual_visual_review`, không thay nội dung.
- Bao gồm số thứ tự, tên sản phẩm, mã trong ngoặc, đơn vị, số lượng, đơn giá và thành tiền.
- Trạng thái train hiện tại: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (tổng 11124/11124).
- Backup: `manual_review_progress.backup_visual_batch_20261101_200903.json`; API lưu 10 mục và đọc lại thành công.

## Đợt rà trực quan — HD_002 cuối và HD_006 đầu

- Đã xem 10 crop auto-confirmed và đối chiếu ảnh trang tương ứng; cả 10 khớp nội dung in trên hóa đơn.
- Với `3fac1a3699b9b5c2517b`, giữ nguyên chữ in `Signatutre Vaild` dù có vẻ sai chính tả; nhãn recognition chép đúng ảnh nguồn, không hiệu đính văn bản hóa đơn.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_200935.json`; API lưu 10 mục và đọc lại xác minh thành công.

## Đợt rà trực quan — HD_006, phần bảng hàng

- Đã xem 12 crop auto-confirmed và đối chiếu trực tiếp trang 1 HD_006.pdf; cả 12 khớp nhãn cột/dòng hàng nhìn thấy.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201030.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_006, phần tổng hợp

- Đã xem 12 crop auto-confirmed, gồm nhãn bảng, các số 0, tỷ lệ và tổng tiền; đối chiếu trang 1 HD_006.pdf, cả 12 khớp.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201113.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_006, phần cuối hóa đơn

- Đã xem 12 crop auto-confirmed và đối chiếu trang 1 HD_006.pdf; các số 0, tiền thuế, tổng thanh toán và nhãn “Bên bán” khớp hình.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201155.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_006 cuối và HD_010 đầu

- Đã xem 12 crop auto-confirmed; đối chiếu trang HD_006/HD_010, các nhãn khớp ảnh. Với dòng ngày HD_010, đã sửa khoảng trắng kép thành một dấu cách theo chữ nhìn thấy.
- Các crop `(Name of goods and`, `(VAT`, `(No)` là những dòng riêng trong tiêu đề cột nhiều dòng; nội dung crop khớp đúng phần dòng được cắt.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201242.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_010, tiêu đề cột

- Đã xem 12 crop auto-confirmed và đối chiếu trang 1 HD_010.pdf; các đoạn như `(Unit)`, `(Discount`, `(Total amount`, `services)`, `(VAT`, `rate)` là những dòng/đoạn hiển thị riêng trong tiêu đề cột nhiều dòng, khớp đúng crop.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201337.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_010, dòng hàng 1–2

- Đã xem 12 crop auto-confirmed và so với trang 1 HD_010.pdf; các phần tên hàng, đơn vị, số thứ tự, thuế, thành tiền và tổng tiền đều khớp hình.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201417.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_010, dòng hàng 2–4 và tổng hợp

- Đã xem 12 crop auto-confirmed và đối chiếu trang 1 HD_010.pdf; các đơn vị, số thứ tự, thuế, thành tiền và đoạn nhãn tổng hợp khớp ảnh.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201458.json`; API lưu 12 mục và đọc lại thành công.

## Đợt rà trực quan — HD_010, tổng kết và trang 2

- Đã xem 12 crop, đối chiếu các số tổng hợp trên trang 1 và hai nhãn chữ ký điện tử trên trang 2. Tất cả khớp ảnh nguồn.
- Trạng thái train: {'verified': 4247, 'needs_review': 1, 'rejected': 7, 'pending': 6869} (11124/11124); backup `manual_review_progress.backup_visual_batch_20261101_201542.json`; API lưu 12 mục và đọc lại thành công.


## Đợt rà trực quan 2026-11-01T13:19:49+00:00

- Đã đối chiếu 16 crop: HD_010 (3 crop trang 2) và HD_012 (13 crop trang 1). Transcript khớp nội dung nhìn thấy trên crop và trang PDF.
- Đã lưu trạng thái `verified` với phương thức `manual_visual_review`; API trả thành công và đọc lại xác nhận đủ 16 mục.
- Ảnh địa chỉ HD_002 `8722d3872eea050200b2` được đọc rõ nhưng dài hơn giới hạn 90 ký tự nên giữ `needs_review`, không rút gọn.
- Trạng thái train hiện tại: {"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}. Phương thức rà: {"": 6918, "manual_rejected": 1, "manual_visual_review": 139, "pdf_ocr_agreement_v1": 4066}.


## Đợt rà trực quan 2026-11-01T13:21:03+00:00

- Đối chiếu 16 crop của HD_012 trang 1 và HD_013 trang 1; transcript khớp crop và trang PDF.
- API lưu thành công, đọc lại xác nhận đủ 16 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202103.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 155, "pdf_ocr_agreement_v1": 4050}`.


## Đợt rà trực quan 2026-11-01T13:22:17+00:00

- Đối chiếu 16 crop của HD_013 trang 1 với đúng trang PDF; transcript khớp ảnh.
- API lưu thành công và đọc lại xác nhận đủ 16 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202217.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 171, "pdf_ocr_agreement_v1": 4034}`.


## Đợt rà trực quan 2026-11-01T13:23:18+00:00

- Đối chiếu 8 crop của HD_013 trang 1; transcript khớp crop và trang PDF.
- API lưu thành công, đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202318.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 179, "pdf_ocr_agreement_v1": 4026}`.


## Đợt rà trực quan 2026-11-01T13:24:21+00:00

- Đối chiếu 8 crop của HD_013 trang 1; transcript khớp hình. `(In sumary)` là lỗi in có trên PDF, giữ đúng nguyên văn.
- API lưu thành công, đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202421.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 187, "pdf_ocr_agreement_v1": 4018}`.


## Đợt rà trực quan 2026-11-01T13:25:00+00:00

- Đối chiếu 8 crop của HD_013 trang 1 với ảnh trang PDF; transcript khớp.
- API lưu thành công và đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202500.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 195, "pdf_ocr_agreement_v1": 4010}`.


## Đợt rà trực quan 2026-11-01T13:26:09+00:00

- Đối chiếu 8 crop HD_013 trang 1 và HD_014 trang 1; transcript khớp ảnh PDF.
- API lưu thành công và đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202609.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 203, "pdf_ocr_agreement_v1": 4002}`.


## Đợt rà trực quan 2026-11-01T13:26:56+00:00

- Đối chiếu 8 crop HD_014 trang 1 với trang PDF. Nội dung khớp; hai transcript có khoảng trắng lặp được chuẩn hóa về một dấu cách theo quy tắc nhãn.
- API lưu thành công, đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202656.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 211, "pdf_ocr_agreement_v1": 3994}`.


## Đợt rà trực quan 2026-11-01T13:27:55+00:00

- Đối chiếu 8 crop HD_014 trang 1 với ảnh trang PDF; transcript khớp.
- API lưu thành công và đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202755.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 219, "pdf_ocr_agreement_v1": 3986}`.


## Đợt rà trực quan 2026-11-01T13:28:32+00:00

- Đối chiếu 8 crop HD_014 trang 1 với trang PDF; transcript khớp.
- API lưu thành công, đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202832.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 227, "pdf_ocr_agreement_v1": 3978}`.


## Đợt rà trực quan 2026-11-01T13:29:07+00:00

- Đối chiếu 8 crop HD_014 trang 1 với trang PDF; transcript khớp.
- API lưu thành công, đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202907.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 235, "pdf_ocr_agreement_v1": 3970}`.


## Đợt rà trực quan 2026-11-01T13:29:46+00:00

- Đối chiếu 8 crop HD_014 trang 1 với PDF; transcript khớp. Một nhãn có khoảng trắng thừa được gộp về một dấu cách.
- API lưu thành công, đọc lại xác nhận đủ 8 mục. Bản sao lưu: `manual_review_progress.backup_visual_batch_20261101_202946.json`.
- Trạng thái train: `{"verified": 4247, "needs_review": 1, "rejected": 7, "pending": 6869}`; phương thức xác nhận: `{"": 6918, "manual_rejected": 1, "manual_visual_review": 243, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:40:02.569625+00:00

- Đối chiếu 8 crop HD_002 trang 1 với ảnh crop và trang PDF. Đã xác nhận transcript chính xác theo nội dung in.
- API lưu thành công và đọc lại khớp đủ 8 nhãn; các annotation validation/test giữ nguyên (2967 mục được đối chiếu). Bản sao lưu trước đợt này: `manual_review_progress.backup_resume_20261101_203719.json`.
- Trạng thái train hiện tại: `{"verified": 4247, "needs_review": 6870, "rejected": 7}`; phương thức: `{"": 6910, "manual_visual_review": 251, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:40:53.635370+00:00

- Đối chiếu 7 crop HD_002 trang 1 với ảnh crop và trang PDF; transcript khớp, các khoảng trắng được gộp về một dấu cách.
- API lưu thành công và đọc lại khớp đủ 7 mục; 2967 annotation validation/test giữ nguyên.
- Crop địa chỉ `8722d3872eea050200b2` đã được nhìn đối chiếu; transcript đọc được nhưng dài 95 ký tự, vượt giới hạn nhập 90. Giữ `needs_review`, không cắt ngắn/ghi nhãn rút gọn.
- Trạng thái train: `{"verified": 4247, "needs_review": 6870, "rejected": 7}`; phương thức: `{"": 6903, "manual_visual_review": 258, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:41:40.598998+00:00

- Đối chiếu 8 crop HD_002 trang 1 với ảnh crop và trang PDF; transcript khớp chính xác nội dung nhìn thấy.
- API lưu thành công và đọc lại khớp đủ 8 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train hiện tại: `{"verified": 4247, "needs_review": 6870, "rejected": 7}`; phương thức: `{"": 6895, "manual_visual_review": 266, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:42:16.804463+00:00

- Đối chiếu 8 crop HD_002 trang 1 với ảnh crop và trang PDF; transcript khớp chính xác.
- API lưu thành công, đọc lại khớp đủ 8 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4247, "needs_review": 6870, "rejected": 7}`; phương thức: `{"": 6887, "manual_visual_review": 274, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:42:53.313524+00:00

- Đối chiếu 8 crop HD_002 trang 1 với ảnh crop và trang PDF; transcript khớp chính xác.
- API lưu thành công, đọc lại khớp đủ 8 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4247, "needs_review": 6870, "rejected": 7}`; phương thức: `{"": 6879, "manual_visual_review": 282, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:43:31.953270+00:00

- Đối chiếu 8 crop HD_002 trang 1 với ảnh crop và trang PDF; transcript khớp.
- API lưu thành công, đọc lại khớp đủ 8 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4253, "needs_review": 6864, "rejected": 7}`; phương thức: `{"": 6871, "manual_visual_review": 290, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:44:26.779514+00:00

- Đối chiếu 4 crop cuối HD_002 trang 1 với ảnh và PDF. Hai mục ngắn đã xác nhận; hai transcript footer được lưu đầy đủ ở trạng thái chờ vì dài 91 và 133 ký tự, vượt giới hạn 90. Không rút gọn.
- API lưu và đọc lại khớp đủ 4 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4255, "needs_review": 6862, "rejected": 7}`; phương thức: `{"": 6867, "manual_visual_review": 294, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.


## Đợt rà trực quan 2026-11-01T13:51:51.315416+00:00

- Đối chiếu 4 crop HD_006 trang 1 trực tiếp với ảnh crop và đúng trang hóa đơn; cả 4 transcript khớp hình ảnh.
- API đã lưu và GET đọc lại khớp đủ 4 mục. 6837 annotation validation/test giữ nguyên so với bản sao lưu trước đợt.
- Trạng thái train sau đợt: `{"verified": 4259, "needs_review": 6858, "rejected": 7}`; phương thức: `{"": 6863, "manual_visual_review": 298, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu trước đợt: `manual_review_progress.backup_resume_20261101_205028.json`.


## Đợt rà trực quan 2026-11-01T13:52:31.815603+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript của cả 4 mục khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên so với trước đợt.
- Trạng thái train: `{"verified": 4263, "needs_review": 6854, "rejected": 7}`; phương thức: `{"": 6859, "manual_visual_review": 302, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205231.json`.


## Đợt rà trực quan 2026-11-01T13:53:08.481163+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp từng chữ.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4267, "needs_review": 6850, "rejected": 7}`; phương thức: `{"": 6855, "manual_visual_review": 306, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205308.json`.


## Đợt rà trực quan 2026-11-01T13:53:49.477225+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4271, "needs_review": 6846, "rejected": 7}`; phương thức: `{"": 6851, "manual_visual_review": 310, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205349.json`.


## Đợt rà trực quan 2026-11-01T13:54:21.588363+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4275, "needs_review": 6842, "rejected": 7}`; phương thức: `{"": 6847, "manual_visual_review": 314, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205421.json`.


## Đợt rà trực quan 2026-11-01T13:54:53.613288+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; cả 4 transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4279, "needs_review": 6838, "rejected": 7}`; phương thức: `{"": 6843, "manual_visual_review": 318, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205453.json`.


## Đợt rà trực quan 2026-11-01T13:55:32.406427+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4283, "needs_review": 6834, "rejected": 7}`; phương thức: `{"": 6839, "manual_visual_review": 322, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205532.json`.


## Đợt rà trực quan 2026-11-01T13:56:04.125265+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4287, "needs_review": 6830, "rejected": 7}`; phương thức: `{"": 6835, "manual_visual_review": 326, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205604.json`.


## Đợt rà trực quan 2026-11-01T13:56:37.854385+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4291, "needs_review": 6826, "rejected": 7}`; phương thức: `{"": 6831, "manual_visual_review": 330, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205637.json`.


## Đợt rà trực quan 2026-11-01T13:57:10.570863+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4295, "needs_review": 6822, "rejected": 7}`; phương thức: `{"": 6827, "manual_visual_review": 334, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205710.json`.


## Đợt rà trực quan 2026-11-01T13:57:53.852067+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4299, "needs_review": 6818, "rejected": 7}`; phương thức: `{"": 6823, "manual_visual_review": 338, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205753.json`.


## Đợt rà trực quan 2026-11-01T13:58:36.750140+00:00

- Đối chiếu 4 crop HD_006 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4303, "needs_review": 6814, "rejected": 7}`; phương thức: `{"": 6819, "manual_visual_review": 342, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205836.json`.


## Đợt rà trực quan 2026-11-01T13:59:11.532360+00:00

- Đối chiếu 2 crop footer HD_006 và 2 crop đầu HD_010 trực tiếp với ảnh; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4307, "needs_review": 6810, "rejected": 7}`; phương thức: `{"": 6815, "manual_visual_review": 346, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205911.json`.


## Đợt rà trực quan 2026-11-01T13:59:43.272008+00:00

- Đối chiếu 4 crop HD_010 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4311, "needs_review": 6806, "rejected": 7}`; phương thức: `{"": 6811, "manual_visual_review": 350, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_205943.json`.


## Đợt rà trực quan 2026-11-01T14:00:32.708672+00:00

- Đối chiếu 4 crop HD_010 trang 1; 3 mục được xác nhận. Crop số tài khoản đã chép nguyên văn 95 ký tự nhưng để `needs_review` vì web giới hạn xác nhận 90 ký tự; không rút gọn.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4314, "needs_review": 6803, "rejected": 7}`; phương thức: `{"": 6807, "manual_visual_review": 354, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_210032.json`.


## Đợt rà trực quan 2026-11-01T14:01:05.756178+00:00

- Đối chiếu 4 crop HD_010 trang 1 với ảnh crop và đúng trang PDF; transcript khớp.
- API lưu và GET đọc lại khớp đủ 4 mục; 6837 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4318, "needs_review": 6799, "rejected": 7}`; phương thức: `{"": 6803, "manual_visual_review": 358, "manual_rejected": 1, "pdf_ocr_agreement_v1": 3962}`.
- Sao lưu: `manual_review_progress.backup_visual_batch_20261101_210105.json`.


## Đợt rà trực quan 2026-11-01T14:08:40.509519+00:00

- Đối chiếu 4 crop HD_010 trang 1 với ảnh crop; transcript khớp nguyên văn.
- API lưu và GET đọc lại khớp đủ 4 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6795, "verified": 4322, "rejected": 7}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 362, "": 8, "manual_rejected": 1}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_140840.json`.


## Đợt rà trực quan 2026-11-01T14:10:48.473470+00:00

- Đối chiếu 4 crop HD_010 trang 1 với ảnh crop; transcript khớp nguyên văn.
- API lưu và GET đọc lại khớp đủ 4 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6791, "verified": 4326, "rejected": 7}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 366, "": 8, "manual_rejected": 1}`.
- Sao lưu tiến độ trước ghi: `manual_review_progress.backup_visual_batch_20261101_141003.json`.


## Đợt rà trực quan 2026-11-01T14:11:32.932224+00:00

- Đối chiếu 4 crop HD_010 trang 1: 3 crop được xác nhận; 1 crop bị loại vì ghép nội dung hai cột.
- API lưu và GET đọc lại khớp cả 4 mục; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4329, "needs_review": 6787, "rejected": 8}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 369, "": 8, "manual_rejected": 2}`.
- Sao lưu tiến độ: `manual_review_progress.backup_visual_batch_20261101_141132.json`.


## Đợt rà trực quan 2026-11-01T14:12:25.569815+00:00

- Đối chiếu 4 crop HD_010 trang 1; cả 4 transcript được xác nhận theo ảnh crop.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6783, "verified": 4333, "rejected": 8}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 373, "": 8, "manual_rejected": 2}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141225.json`.


## Đợt rà trực quan 2026-11-01T14:13:13.280255+00:00

- Đối chiếu 4 crop HD_010 trang 1; 2 xác nhận, 2 loại vì ghép cột số lượng/đơn giá.
- API lưu và GET đọc lại khớp cả 4; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6779, "verified": 4335, "rejected": 10}`; phương thức: `{"manual_visual_review": 375, "pdf_ocr_agreement_v1": 3962, "": 8, "manual_rejected": 4}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141313.json`.


## Đợt rà trực quan 2026-11-01T14:13:48.654961+00:00

- Đối chiếu 4 crop HD_010 trang 1; cả 4 transcript xác nhận khớp ảnh.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6775, "verified": 4339, "rejected": 10}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 379, "manual_rejected": 4, "": 8}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141348.json`.


## Đợt rà trực quan 2026-11-01T14:14:26.527103+00:00

- Đối chiếu 4 crop HD_010 trang 1; 3 xác nhận, 1 loại do ghép hai cột số liệu.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6771, "verified": 4342, "rejected": 11}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 382, "manual_rejected": 5, "": 8}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141426.json`.


## Đợt rà trực quan 2026-11-01T14:15:10.175405+00:00

- Đối chiếu 4 crop HD_010 trang 1; 3 xác nhận nguyên văn, 1 loại do ghép cột.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4345, "needs_review": 6767, "rejected": 12}`; phương thức: `{"manual_visual_review": 385, "pdf_ocr_agreement_v1": 3962, "": 8, "manual_rejected": 6}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141510.json`.


## Đợt rà trực quan 2026-11-01T14:15:55.182055+00:00

- Đối chiếu 4 crop HD_010 trang 1; cả 4 xác nhận đúng theo ảnh.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"needs_review": 6763, "verified": 4349, "rejected": 12}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 389, "": 8, "manual_rejected": 6}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141555.json`.


## Đợt rà trực quan 2026-11-01T14:16:31.512342+00:00

- Đối chiếu 4 crop HD_010 trang 1; cả 4 xác nhận nguyên văn.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4353, "needs_review": 6759, "rejected": 12}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 393, "manual_rejected": 6, "": 8}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141631.json`.


## Đợt rà trực quan 2026-11-01T14:17:08.393442+00:00

- Đối chiếu 4 crop HD_010 trang 1; cả 4 xác nhận chính xác theo ảnh.
- API lưu và GET đọc lại khớp; 2967 annotation validation/test giữ nguyên.
- Trạng thái train: `{"verified": 4357, "needs_review": 6755, "rejected": 12}`; phương thức: `{"pdf_ocr_agreement_v1": 3962, "manual_visual_review": 397, "": 8, "manual_rejected": 6}`.
- Sao lưu trước ghi: `manual_review_progress.backup_visual_batch_20261101_141708.json`.
