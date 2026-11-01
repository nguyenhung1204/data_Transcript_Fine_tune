from __future__ import annotations
import argparse, csv, json, os, shutil, threading
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from auto_confirm import build_preview, write_preview_artifacts

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
MANIFEST = ROOT / 'crop_manifest.csv'
PROGRESS = OUT / 'manual_review_progress.json'
LOCK = threading.RLock()

with MANIFEST.open('r', encoding='utf-8-sig', newline='') as f:
    CROP_IDS = {row['crop_id'] for row in csv.DictReader(f)}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        # Keep the review UI current after local edits; stale HTML can hide fixes.
        self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def _json(self, code, body):
        payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/api/annotations':
            with LOCK:
                if PROGRESS.is_file():
                    try:
                        return self._json(200, json.loads(PROGRESS.read_text(encoding='utf-8')))
                    except (OSError, json.JSONDecodeError):
                        return self._json(500, {'error': 'Không đọc được tiến độ đã lưu.'})
                return self._json(200, {'version': 1, 'annotations': []})
        if path == '/api/auto-confirm/preview':
            try:
                with LOCK:
                    preview = build_preview(ROOT, OUT)
                    write_preview_artifacts(OUT, preview)
                return self._json(200, {k: v for k, v in preview.items() if k != 'candidates'})
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                return self._json(500, {'error': f'Không tạo được dry-run: {exc}'})
        return super().do_GET()

    def do_POST(self):
        path = self.path.split('?', 1)[0]
        if path == '/api/auto-confirm/apply':
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length < 1 or length > 1_000_000:
                    return self._json(413, {'error': 'Kích thước dữ liệu không hợp lệ.'})
                request = json.loads(self.rfile.read(length))
                token = request.get('token', '')
                with LOCK:
                    preview = build_preview(ROOT, OUT)
                    if not token or token != preview.get('token'):
                        return self._json(409, {'error': 'Tiến độ hoặc manifest đã đổi sau dry-run. Hãy chạy xem trước lại.', 'stale': True})
                    progress = json.loads(PROGRESS.read_text(encoding='utf-8')) if PROGRESS.is_file() else {'version': 1, 'annotations': []}
                    existing = {str(a['crop_id']): a for a in progress.get('annotations', []) if a.get('crop_id')}
                    now = datetime.now(timezone.utc).isoformat()
                    applied = []
                    for candidate in preview['candidates']:
                        crop_id = candidate['crop_id']
                        old = existing.get(crop_id)
                        if old and old.get('status') in {'verified', 'rejected'}:
                            continue
                        applied.append({
                            'crop_id': crop_id, 'status': 'verified',
                            'transcript': candidate['transcript'], 'reviewed_at': now,
                            'confirmation_method': candidate['method'],
                            'evidence': candidate['evidence'],
                        })
                    if not applied:
                        write_preview_artifacts(OUT, preview, applied_count=0)
                        return self._json(200, {'applied': 0, 'eligible': preview['eligible_count'], 'message': 'Không có mục mới cần áp dụng.'})
                    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    backup = PROGRESS.with_name(f'manual_review_progress.backup_{stamp}.json')
                    if PROGRESS.exists():
                        shutil.copy2(PROGRESS, backup)
                    for item in applied:
                        existing[item['crop_id']] = item
                    payload = json.dumps({'version': 1, 'annotations': list(existing.values())}, ensure_ascii=False, indent=2)
                    temp = PROGRESS.with_suffix('.json.tmp')
                    temp.write_text(payload, encoding='utf-8')
                    os.replace(temp, PROGRESS)
                    history_path = OUT / 'auto_confirm_history.json'
                    history = json.loads(history_path.read_text(encoding='utf-8')) if history_path.is_file() else []
                    history.append({
                        'applied_at_utc': now,
                        'applied': len(applied),
                        'policy_version': preview['policy_version'],
                        'preview_token': token,
                        'backup': str(backup) if backup.exists() else '',
                    })
                    history_tmp = history_path.with_suffix('.json.tmp')
                    history_tmp.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')
                    os.replace(history_tmp, history_path)
                    updated = build_preview(ROOT, OUT)
                    write_preview_artifacts(OUT, updated, applied_count=len(applied), backup_path=str(backup) if backup.exists() else 'không có file cũ')
                return self._json(200, {'applied': len(applied), 'eligible': preview['eligible_count'], 'backup': str(backup) if backup.exists() else '', 'path': str(PROGRESS)})
            except (ValueError, TypeError, json.JSONDecodeError, OSError, KeyError) as exc:
                return self._json(500, {'error': f'Không áp dụng được xác nhận: {exc}'})
        if path != '/api/annotations':
            return self._json(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 50_000_000:
                return self._json(413, {'error': 'Kích thước dữ liệu không hợp lệ.'})
            data = json.loads(self.rfile.read(length))
            if data.get('version') != 1 or not isinstance(data.get('annotations'), list):
                return self._json(400, {'error': 'Sai định dạng tiến độ.'})
            result, seen = [], set()
            for item in data['annotations']:
                crop_id, status = item.get('crop_id'), item.get('status')
                transcript = item.get('transcript') or ''
                if crop_id not in CROP_IDS or crop_id in seen:
                    return self._json(400, {'error': 'Crop ID không hợp lệ hoặc bị lặp.'})
                if status not in {'verified', 'rejected', 'needs_review'}:
                    return self._json(400, {'error': 'Trạng thái không hợp lệ.'})
                if status == 'verified' and (not transcript.strip() or len(transcript) > 90 or any(c in transcript for c in '\r\n\t')):
                    return self._json(400, {'error': 'Nhãn xác nhận phải có nội dung một dòng và tối đa 90 ký tự.'})
                seen.add(crop_id)
                confirmation_method = item.get('confirmation_method')
                if confirmation_method not in {None, 'pdf_ocr_agreement_v1', 'manual_visual_review', 'manual_rejected'}:
                    return self._json(400, {'error': 'Nguồn xác nhận không hợp lệ.'})
                result_item = {'crop_id': crop_id, 'status': status, 'transcript': transcript, 'reviewed_at': item.get('reviewed_at', '')}
                if confirmation_method:
                    result_item['confirmation_method'] = confirmation_method
                result.append(result_item)
            with LOCK:
                previous = json.loads(PROGRESS.read_text(encoding='utf-8')) if PROGRESS.is_file() else {'annotations': []}
                merged = {str(a['crop_id']): a for a in previous.get('annotations', []) if a.get('crop_id')}
                for item in result:
                    old = merged.get(item['crop_id'])
                    old_time = str((old or {}).get('reviewed_at') or '')
                    new_time = str(item.get('reviewed_at') or '')
                    if old and old_time and new_time and new_time < old_time:
                        continue
                    if old and old.get('status') == item.get('status') and old.get('transcript', '') == item.get('transcript', ''):
                        if 'confirmation_method' not in item and 'confirmation_method' in old:
                            item['confirmation_method'] = old['confirmation_method']
                        if item.get('confirmation_method') == old.get('confirmation_method') and 'evidence' in old:
                            item['evidence'] = old['evidence']
                    merged[item['crop_id']] = item
                payload = json.dumps({'version': 1, 'annotations': list(merged.values())}, ensure_ascii=False, indent=2)
                temp = PROGRESS.with_suffix('.json.tmp')
                temp.write_text(payload, encoding='utf-8')
                os.replace(temp, PROGRESS)
            return self._json(200, {'saved': len(result), 'total': len(merged), 'path': str(PROGRESS)})
        except (ValueError, TypeError, json.JSONDecodeError):
            return self._json(400, {'error': 'JSON không hợp lệ.'})
        except OSError:
            return self._json(500, {'error': 'Không ghi được tiến độ.'})

    def log_message(self, fmt, *args):
        # Keep the local server log concise.
        print(fmt % args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8768)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Invoice crop review: http://127.0.0.1:{args.port}/automatic_review/review_queue.html', flush=True)
    server.serve_forever()
