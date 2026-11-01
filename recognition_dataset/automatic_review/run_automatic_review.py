from __future__ import annotations
import csv, hashlib, importlib.util, json, os, shutil, sqlite3, sys, time, unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pypdfium2 as pdfium

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
PDF_ROOT = ROOT / 'source_300_invoices' / 'pdfs'
MANIFEST = ROOT / 'crop_manifest.csv'
DB = OUT / 'checkpoint_visual_order.sqlite3'
FIELDS = [
    'review_status', 'review_reasons', 'ocr1_text', 'ocr2_text', 'pdf_text',
    'pdf_text_found', 'pdf_text_matches_ocr1', 'pdf_text_line_count',
    'geometry_valid', 'pdf_sha256_verified', 'is_machine_consensus',
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def normalized(value):
    return ' '.join(unicodedata.normalize('NFC', value or '').split())


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)


def visual_characters(textpage):
    """Read PDF glyphs once and retain their page geometry for visual ordering."""
    characters = []
    for index in range(textpage.count_chars()):
        value = textpage.get_text_range(index, 1)
        if not value or value in {'\r', '\n', '\x00'}:
            continue
        try:
            left, bottom, right, top = textpage.get_charbox(index)
        except Exception:
            continue
        if right < left or top < bottom:
            continue
        characters.append({
            'text': value,
            'left': float(left),
            'right': float(right),
            'top_y': float(top),
            'bottom_y': float(bottom),
            'center_y': (float(top) + float(bottom)) / 2,
            'height': max(0.0, float(top) - float(bottom)),
        })
    return characters


def visual_order_text(characters):
    """Order PDF glyphs top-to-bottom, then left-to-right, independent of stream order."""
    if not characters:
        return '', 0

    heights = sorted(c['height'] for c in characters if c['height'] > 0)
    typical_height = heights[len(heights) // 2] if heights else 6.0
    # Superscript punctuation (especially apostrophes) can sit above the body
    # line; allow it to join that line without merging adjacent baselines.
    line_tolerance = max(1.5, min(5.0, typical_height * 0.68))
    lines = []
    for character in sorted(characters, key=lambda c: (c['center_y'], c['left'])):
        line = min(lines, key=lambda item: abs(item['center_y'] - character['center_y']), default=None)
        if line is None or abs(line['center_y'] - character['center_y']) > line_tolerance:
            lines.append({'center_y': character['center_y'], 'characters': [character]})
            continue
        line['characters'].append(character)
        line['center_y'] = sum(c['center_y'] for c in line['characters']) / len(line['characters'])

    # PDF coordinates start at the bottom-left, so larger y values are higher
    # on the rendered page.
    lines.sort(key=lambda item: item['center_y'], reverse=True)
    rendered_lines = []
    for line in lines:
        ordered = sorted(line['characters'], key=lambda c: (c['left'], c['right']))
        parts = []
        previous = None
        for character in ordered:
            if previous is not None:
                gap = character['left'] - previous['right']
                # Some PDFs store label, punctuation, and value in separate text runs
                # without a space glyph. Restore a visible gap while preserving spaces
                # already present in the PDF text layer.
                apostrophe = character['text'] in {"'", '’'} or previous['text'] in {"'", '’'}
                if gap > max(1.2, typical_height * 0.34) and not apostrophe and not parts[-1].endswith((' ', '\t')):
                    parts.append(' ')
            parts.append(character['text'])
            previous = character
        rendered_lines.append(''.join(parts).strip())
    text = '\n'.join(line for line in rendered_lines if line)
    return text, sum(bool(line) for line in rendered_lines)


def text_for_crop(page, textpage, row, dpi, characters=None):
    width, height = page.get_size()
    try:
        x0, y0, x1, y1 = [float(row[k]) for k in ('x0', 'y0', 'x1', 'y1')]
        number = int(row['page'])
    except (ValueError, TypeError, KeyError):
        return '', False, 'invalid_page_or_coordinates', 0
    if number < 1 or x1 <= x0 or y1 <= y0:
        return '', False, 'invalid_page_or_coordinates', 0
    scale = 72.0 / dpi
    left, right = x0 * scale, x1 * scale
    bottom, top = height - y1 * scale, height - y0 * scale
    tol = scale * 1.5
    valid = left >= -tol and bottom >= -tol and right <= width + tol and top <= height + tol
    if not valid:
        return '', False, 'crop_outside_page', 0
    box = (max(0.0, left), max(0.0, bottom), min(width, right), min(height, top))
    try:
        characters = visual_characters(textpage) if characters is None else characters
        selected = [
            character for character in characters
            if box[0] <= (character['left'] + character['right']) / 2 <= box[2]
            and box[1] <= character['center_y'] <= box[3]
        ]
        value, line_count = visual_order_text(selected)
    except Exception as exc:
        return '', False, f'pdf_text_extraction_error:{type(exc).__name__}', 0
    value = unicodedata.normalize('NFC', value or '').replace('\x00', '').strip()
    return value, True, '', line_count


def engine_inventory():
    names = ['easyocr', 'rapidocr_onnxruntime', 'doctr', 'keras_ocr', 'pytesseract']
    available = [name for name in names if importlib.util.find_spec(name)]
    return {'independent_ocr_packages_found': available, 'tesseract_executable_found': bool(shutil.which('tesseract'))}


def main():
    started = time.time()
    log_path = OUT / 'run.log'
    def log(message):
        with log_path.open('a', encoding='utf-8') as f:
            f.write(f'[{utc_now()}] {message}\n')
        print(message.encode('ascii', 'backslashreplace').decode('ascii'), flush=True)

    if not MANIFEST.is_file() or not PDF_ROOT.is_dir():
        raise SystemExit('Required source manifest or read-only PDF folder is missing.')
    base_meta = json.loads((ROOT / 'metadata.json').read_text(encoding='utf-8'))
    dpi = int(base_meta.get('dpi') or 300)
    with MANIFEST.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        source_fields = reader.fieldnames or []
        rows = list(reader)
    if not rows or not {'crop_id','document_id','filename','source_pdf_sha256','page','x0','y0','x1','y1','split','label_status'} <= set(source_fields):
        raise SystemExit('Crop manifest is empty or lacks required fields.')
    if len({row['crop_id'] for row in rows}) != len(rows):
        raise SystemExit('Duplicate crop_id found; refusing to produce ambiguous output.')

    grouped = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[row['document_id']].append((index, row))

    inventory = engine_inventory()
    log(f'Started: {len(grouped)} documents, {len(rows)} manifest rows, DPI={dpi}; OCR2 available={inventory["independent_ocr_packages_found"] or inventory["tesseract_executable_found"]}')
    db = sqlite3.connect(DB)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('CREATE TABLE IF NOT EXISTS results (row_index INTEGER PRIMARY KEY, crop_id TEXT UNIQUE, document_id TEXT, payload TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS completed (document_id TEXT PRIMARY KEY, filename TEXT, source_sha256 TEXT, row_count INTEGER, completed_utc TEXT)')
    db.commit()
    completed = {r[0] for r in db.execute('SELECT document_id FROM completed')}

    for doc_number, (document_id, indexed_rows) in enumerate(grouped.items(), start=1):
        filename_set = {row['filename'] for _, row in indexed_rows}
        checksum_set = {row['source_pdf_sha256'].lower() for _, row in indexed_rows}
        if len(filename_set) != 1 or len(checksum_set) != 1:
            raise SystemExit(f'Manifest conflict for document_id={document_id}')
        filename, expected_sha = next(iter(filename_set)), next(iter(checksum_set))
        if document_id in completed:
            continue
        if Path(filename).name != filename or not filename.lower().endswith('.pdf'):
            raise SystemExit(f'Unsafe or invalid PDF filename in manifest: {filename!r}')
        pdf_path = PDF_ROOT / filename
        got_sha = sha256(pdf_path) if pdf_path.is_file() else ''
        sha_ok = bool(got_sha and got_sha.lower() == expected_sha)
        output = []
        page_cache = {}
        doc = None
        if sha_ok:
            try:
                doc = pdfium.PdfDocument(str(pdf_path))
            except Exception as exc:
                log(f'PDF open failed {filename}: {type(exc).__name__}')
        for row_index, source in indexed_rows:
            row = dict(source)
            ocr1 = source.get('raw_ocr_text') or source.get('transcript') or ''
            pdf_text, geometry_valid, geom_reason, line_count = '', False, '', 0
            reason = []
            if not sha_ok:
                reason.append('source_pdf_missing_or_sha256_mismatch')
            elif doc is None:
                reason.append('pdf_open_failed')
            else:
                try:
                    page_number = int(source['page'])
                    if page_number < 1 or page_number > len(doc):
                        geom_reason = 'page_out_of_range'
                    else:
                        if page_number not in page_cache:
                            page = doc[page_number - 1]
                            textpage = page.get_textpage()
                            page_cache[page_number] = (page, textpage, visual_characters(textpage))
                        page, textpage, characters = page_cache[page_number]
                        pdf_text, geometry_valid, geom_reason, line_count = text_for_crop(page, textpage, source, dpi, characters)
                except Exception as exc:
                    geom_reason = f'pdf_page_error:{type(exc).__name__}'
                if geom_reason:
                    reason.append(geom_reason)
            pdf_found = bool(normalized(pdf_text))
            exact_match = bool(pdf_found and normalized(ocr1) and normalized(pdf_text) == normalized(ocr1))
            existing = (source.get('label_status') or '').strip().lower()
            if existing == 'verified':
                status = 'human_verified_preserved'
                reasons = ['source_label_already_human_verified_preserved']
            elif existing in {'rejected', 'excluded'}:
                status = 'source_rejected_preserved'
                reasons = ['source_label_status_preserved']
            else:
                status = 'needs_review'
                if not inventory['independent_ocr_packages_found'] and not inventory['tesseract_executable_found']:
                    reason.append('independent_ocr2_unavailable')
                else:
                    # Engines are inventoried but no independent OCR inference is run without a configured Vietnamese model.
                    reason.append('independent_ocr2_not_configured')
                if not pdf_found:
                    reason.append('pdf_text_layer_empty_or_crop_has_no_text')
                elif not exact_match:
                    reason.append('pdf_text_and_ocr1_disagree')
                if line_count > 1:
                    reason.append('pdf_crop_contains_multiple_text_lines')
                reasons = list(dict.fromkeys(reason))
            # Three-way consensus is deliberately impossible until a separately configured OCR2 is available.
            consensus = False
            row.update({
                'review_status': status,
                'review_reasons': ';'.join(reasons),
                'ocr1_text': ocr1,
                'ocr2_text': '',
                'pdf_text': pdf_text,
                'pdf_text_found': str(pdf_found).lower(),
                'pdf_text_matches_ocr1': str(exact_match).lower(),
                'pdf_text_line_count': str(line_count),
                'geometry_valid': str(geometry_valid).lower(),
                'pdf_sha256_verified': str(sha_ok).lower(),
                'is_machine_consensus': str(consensus).lower(),
            })
            output.append((row_index, source['crop_id'], document_id, json.dumps(row, ensure_ascii=False)))
        if doc is not None:
            for page, _, _ in page_cache.values():
                page.close()
            doc.close()
        with db:
            db.executemany('INSERT OR REPLACE INTO results VALUES (?,?,?,?)', output)
            db.execute('INSERT OR REPLACE INTO completed VALUES (?,?,?,?,?)', (document_id, filename, expected_sha, len(output), utc_now()))
        log(f'Processed {doc_number}/{len(grouped)}: {document_id} ({len(output)} crops)')
        atomic_json(OUT / 'checkpoint.json', {
            'updated_utc': utc_now(), 'total_documents': len(grouped),
            'completed_documents': db.execute('SELECT COUNT(*) FROM completed').fetchone()[0],
            'total_crop_rows': len(rows), 'committed_crop_rows': db.execute('SELECT COUNT(*) FROM results').fetchone()[0],
            'last_document_id': document_id,
        })

    result_rows = {}
    for row_index, payload in db.execute('SELECT row_index,payload FROM results ORDER BY row_index'):
        result_rows[row_index] = json.loads(payload)
    if len(result_rows) != len(rows):
        raise SystemExit(f'Checkpoint incomplete: {len(result_rows)} of {len(rows)} rows.')

    all_fields = source_fields + [field for field in FIELDS if field not in source_fields]
    def write_csv(path, selected):
        with path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction='ignore')
            writer.writeheader()
            for row in selected:
                writer.writerow(row)
    enriched = [result_rows[i] for i in range(len(rows))]
    pending = [r for r in enriched if r['review_status'] == 'needs_review']
    test_pending = [r for r in pending if (r.get('split') or '').lower() == 'test']
    train_val_pending = [r for r in pending if (r.get('split') or '').lower() in {'train','val','validation'}]
    machine_consensus = [r for r in enriched if r['is_machine_consensus'] == 'true']
    write_csv(OUT / 'automatic_review_manifest.csv', enriched)
    write_csv(OUT / 'needs_review.csv', pending)
    write_csv(OUT / 'train_val_needs_review.csv', train_val_pending)
    write_csv(OUT / 'test_candidates.csv', test_pending)
    # Never create a ZIP if there are no eligible, machine-consensus labels.
    zip_path = OUT / 'auto_consensus_train_val.zip'
    if not machine_consensus and zip_path.exists():
        zip_path.unlink()
    elif machine_consensus:
        raise SystemExit('Unexpected consensus rows without OCR2; inspect before packaging.')

    statuses = Counter(r['review_status'] for r in enriched)
    splits = Counter((r.get('split') or 'unknown').lower() for r in enriched)
    pdf_found_count = sum(r['pdf_text_found'] == 'true' for r in enriched)
    matches = sum(r['pdf_text_matches_ocr1'] == 'true' for r in enriched)
    geometry_bad = sum(r['geometry_valid'] != 'true' for r in enriched)
    line_multi = sum(int(r['pdf_text_line_count'] or 0) > 1 for r in enriched)
    reason_counts = Counter(reason for r in pending for reason in r['review_reasons'].split(';') if reason)
    summary = {
        'generated_utc': utc_now(), 'source_manifest': str(MANIFEST), 'source_pdf_directory': str(PDF_ROOT),
        'crop_manifest_rows': len(rows), 'source_documents': len(grouped), 'dpi': dpi,
        'ocr1_source': 'raw_ocr_text (fallback: transcript) from the existing crop manifest',
        'ocr2_status': 'unavailable_or_not_configured; no independent engine inference run',
        'pdf_text_extraction': 'pypdfium2 embedded glyphs selected by crop coordinates and ordered by visual geometry',
        'status_counts': dict(statuses), 'split_crop_counts': dict(splits),
        'pdf_text_found_count': pdf_found_count, 'pdf_text_matches_ocr1_count': matches,
        'geometry_invalid_count': geometry_bad, 'multi_line_pdf_crop_count': line_multi,
        'machine_consensus_count': len(machine_consensus), 'reason_counts': dict(reason_counts),
        'verified_zip_created': False, 'test_candidates_exported_separately': True,
        'packages_not_installed': True,
    }
    atomic_json(OUT / 'summary.json', summary)
    metadata = {
        'generated_utc': utc_now(), 'python': sys.version, 'pypdfium2': getattr(pdfium, '__version__', 'version_unavailable'),
        'dpi': dpi, 'source_dataset_metadata': base_meta, 'ocr_inventory': inventory,
        'ocr2_policy': 'Do not install or download engines; consensus requires PDF embedded text + OCR1 + independent OCR2.',
        'source_scope': 'read-only; all generated outputs are under automatic_review/',
        'source_pdf_checksum_policy': 'SHA-256 checked against every crop manifest record before extraction',
    }
    atomic_json(OUT / 'metadata.json', metadata)
    lines = [
        '# Tóm tắt rà soát tự động crop', '',
        f'- Thời điểm hoàn tất (UTC): `{summary["generated_utc"]}`',
        f'- PDF/hoá đơn đã rà: **{len(grouped)}**', f'- Crop trong manifest: **{len(rows)}**',
        f'- Lớp chữ PDF có nội dung trong crop: **{pdf_found_count}/{len(rows)}**',
        '- Thứ tự chữ PDF được dựng từ tọa độ ký tự theo thứ tự nhìn thấy; nút trên web chỉ chép bản nháp, không tự xác nhận nhãn.',
        f'- Lớp chữ PDF khớp OCR cũ sau chuẩn hoá Unicode NFC và khoảng trắng: **{matches}/{len(rows)}**',
        f'- Nhãn xác nhận thủ công được giữ nguyên: **{statuses.get("human_verified_preserved", 0)}**',
        f'- Crop cần rà tay: **{statuses.get("needs_review", 0)}**',
        f'- Crop đồng thuận máy: **{len(machine_consensus)}**',
        f'- Hộp crop sai/ngoài trang: **{geometry_bad}**; crop có nhiều dòng chữ PDF: **{line_multi}**',
        '', '## Lý do chưa tự xác nhận', '',
        'Môi trường không có OCR độc lập thứ hai đã cấu hình. Theo tiêu chí an toàn, nhãn chỉ được tự xác nhận khi lớp chữ PDF, OCR hiện có và OCR thứ hai đồng thuận; do thiếu OCR thứ hai, kết quả PDF khớp OCR cũ chỉ là bằng chứng hỗ trợ, không phải nhãn chuẩn.',
        'Không cài thêm package, không tải model, không tạo ZIP fine-tune rỗng. Hai nhãn đã xác nhận thủ công trong nguồn được giữ trạng thái riêng, không bị ghi đè.',
        '', '## File đầu ra', '',
        '- `automatic_review_manifest.csv`: toàn bộ crop và kết quả đối chiếu.',
        '- `needs_review.csv`: tất cả crop còn chờ người xem.',
        '- `train_val_needs_review.csv`: các crop train/validation đang chờ; chưa dùng làm nhãn huấn luyện.',
        '- `test_candidates.csv`: test được tách riêng, không đưa vào train/validation.',
        '- `summary.json`, `metadata.json`, `run.log`, `checkpoint.json`.',
        '- Không có `auto_consensus_train_val.zip`: chưa có crop nào đủ điều kiện đồng thuận ba nguồn.',
        '', '## Giới hạn', '',
        'PDF không có lớp text hoặc lớp text không khớp vùng crop sẽ vẫn cần rà tay. OCR cũ được tái dùng từ manifest; chưa chạy OCR độc lập thứ hai. Việc so khớp chính xác không tự sửa khác biệt ký tự hay dấu tiếng Việt.',
    ]
    (OUT / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    log(f'Finished: rows={len(rows)}, pdf_text={pdf_found_count}, OCR1_matches={matches}, needs_review={len(pending)}, consensus={len(machine_consensus)}')
    atomic_json(OUT / 'checkpoint.json', {
        'updated_utc': utc_now(), 'total_documents': len(grouped), 'completed_documents': len(grouped),
        'total_crop_rows': len(rows), 'committed_crop_rows': len(rows), 'finished': True,
        'summary': str(OUT / 'summary.json'),
    })
    db.close()
    print(f'OUTPUT_DIR={OUT}')
    print(f'SUMMARY={OUT / "SUMMARY.md"}')
    print(f'ELAPSED_SECONDS={time.time()-started:.1f}')

if __name__ == '__main__':
    main()
