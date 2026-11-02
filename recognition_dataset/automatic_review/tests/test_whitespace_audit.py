import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from whitespace_audit import analyze_transcript, confirmed_gallery_rows, load_excluded_invoices, save_review_status
except ImportError:
    analyze_transcript = confirmed_gallery_rows = load_excluded_invoices = save_review_status = None


class WhitespaceAuditTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(analyze_transcript, 'whitespace audit analyzer is implemented')
        self.assertIsNotNone(confirmed_gallery_rows, 'gallery source matching is implemented')
        self.assertIsNotNone(load_excluded_invoices, 'gallery exclusions are read safely')
        self.assertIsNotNone(save_review_status, 'review decisions are persisted safely')

    def test_flags_split_word_and_suggests_join_only_when_word_is_known(self):
        result = analyze_transcript('Exchange r ate', vocabulary={'rate'})
        self.assertIn('split_inside_word', {issue['category'] for issue in result['issues']})
        self.assertEqual(result['suggested_transcript'], 'Exchange rate')

        unknown = analyze_transcript('A long invoice', vocabulary=set())
        self.assertIsNone(unknown['suggested_transcript'])

    def test_flags_screenshot_spacing_patterns_without_auto_correcting(self):
        result = analyze_transcript('Tổng c ộng ( Total:)')
        categories = {issue['category'] for issue in result['issues']}
        self.assertIn('split_inside_word', categories)
        self.assertIn('space_after_opening', categories)
        self.assertIsNone(result['suggested_transcript'])

        self.assertIn('split_inside_word', {
            issue['category'] for issue in analyze_transcript('Người mua h àng ( Buyer)')['issues']
        })
        self.assertIn('split_inside_word', {
            issue['category'] for issue in analyze_transcript('Signature V alid')['issues']
        })

    def test_flags_repeated_and_nonstandard_whitespace(self):
        result = analyze_transcript('Email ,  user\u00a0@example.com')
        categories = {issue['category'] for issue in result['issues']}
        self.assertIn('space_before_punctuation', categories)
        self.assertIn('repeated_whitespace', categories)
        self.assertIn('nonstandard_whitespace', categories)

    def test_does_not_flag_regular_invoice_text(self):
        self.assertEqual(analyze_transcript('Số hóa đơn: 001234; Tổng tiền 409.091')['issues'], [])
        self.assertEqual(analyze_transcript('Số tài khoản (A/C No.)')['issues'], [])
        self.assertEqual(analyze_transcript('Mã số thuế (VAT code) : 0101234567')['issues'], [])

    def test_gallery_scope_merges_saved_status_and_excludes_same_invoice_as_page(self):
        data = [
            {'id': 'one', 'invoice': 'HD_001', 'pdf': 'one.pdf', 'text': 'nháp'},
            {'id': 'two', 'invoice': 'HD_028', 'pdf': 'two.pdf', 'text': 'excluded'},
            {'id': 'three', 'invoice': 'HD_003', 'pdf': 'three.pdf', 'text': 'source'},
        ]
        saved = [
            {'crop_id': 'one', 'status': 'verified', 'transcript': 'Exchange r ate'},
            {'crop_id': 'two', 'status': 'verified', 'transcript': 'include? no'},
            {'crop_id': 'three', 'status': 'rejected', 'transcript': 'rejected'},
        ]
        rows = confirmed_gallery_rows(data, saved, excluded_invoices={'HD_028'})
        self.assertEqual([row['id'] for row in rows], ['one'])
        self.assertEqual(rows[0]['transcript'], 'Exchange r ate')

    def test_reads_single_quoted_javascript_exclusion_list(self):
        with tempfile.TemporaryDirectory() as directory:
            gallery = Path(directory) / 'gallery.html'
            gallery.write_text("const EXCLUDED_INVOICES=new Set(['HD_028', 'WEB_003']);", encoding='utf-8')
            self.assertEqual(load_excluded_invoices(gallery), {'HD_028', 'WEB_003'})

    def test_correction_preserves_confirmation_method_and_records_history(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / 'review_data.json').write_text(json.dumps([
                {'id': 'crop-1', 'crop_id': 'crop-1', 'invoice': 'HD_001', 'pdf': 'HD_001.pdf',
                 'page': 1, 'coords': [1, 2, 3, 4], 'image': '/crop.png', 'text': 'draft'}
            ]), encoding='utf-8')
            (out / 'confirmed_gallery.html').write_text("const EXCLUDED_INVOICES=new Set([]);", encoding='utf-8')
            annotations_path = out / 'manual_review_progress.json'
            annotations_path.write_text(json.dumps({'version': 1, 'annotations': [
                {'crop_id': 'crop-1', 'status': 'verified', 'transcript': 'Exchange r ate',
                 'confirmation_method': 'codex_visual_review'}
            ]}), encoding='utf-8')

            result = save_review_status(crop_id='crop-1', status='corrected', transcript='Exchange rate', out=out)
            saved = json.loads(annotations_path.read_text(encoding='utf-8'))['annotations'][0]
            progress = json.loads((out / 'whitespace_audit_progress.json').read_text(encoding='utf-8'))
            self.assertTrue(result['saved'])
            self.assertEqual(saved['transcript'], 'Exchange rate')
            self.assertEqual(saved['confirmation_method'], 'manual_visual_review')
            self.assertEqual(progress['history'][0]['old_transcript'], 'Exchange r ate')
            self.assertEqual(progress['history'][0]['new_transcript'], 'Exchange rate')
            self.assertEqual(progress['history'][0]['previous_confirmation_method'], 'codex_visual_review')
            self.assertTrue((out / 'manual_review_progress.before_whitespace_audit.json').is_file())


if __name__ == '__main__':
    unittest.main()
