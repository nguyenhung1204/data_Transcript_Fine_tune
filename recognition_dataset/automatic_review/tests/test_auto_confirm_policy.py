import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from auto_confirm import evaluate_candidate
except ImportError:
    evaluate_candidate = None


def candidate(**overrides):
    row = {
        'crop_id': 'crop-1', 'label_status': 'needs_review',
        'pdf_text': 'Mã số : 0123456789',
        'ocr1_text': 'Mã số: 0123456789', 'confidence': '0.95',
        'ocr_model': 'cached_paddleocr_baseline',
        'pdf_text_found': 'true', 'pdf_text_line_count': '1',
        'pdf_sha256_verified': 'true', 'geometry_valid': 'true',
        'page': '1', 'x0': '10', 'y0': '20', 'x1': '300', 'y1': '60',
    }
    row.update(overrides)
    return row


class AutoConfirmPolicyTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(evaluate_candidate, 'auto-confirm policy is implemented')

    def test_only_matching_high_confidence_single_line_is_eligible(self):
        result = evaluate_candidate(candidate(), source_pdf_status='verified', crop_exists=True)
        self.assertTrue(result['eligible'], result['reasons'])
        self.assertEqual(result['transcript'], 'Mã số : 0123456789')

    def test_visible_character_or_diacritic_disagreement_stays_pending(self):
        result = evaluate_candidate(candidate(ocr1_text='Mã sô: 0123456789'), source_pdf_status='verified', crop_exists=True)
        self.assertFalse(result['eligible'])
        self.assertIn('pdf_ocr_disagree', result['reasons'])

    def test_missing_source_crop_and_invalid_geometry_stay_pending(self):
        for row, source_status, crop_exists, expected in [
            (candidate(), 'missing', True, 'source_pdf_missing'),
            (candidate(), 'sha256_mismatch', True, 'source_pdf_sha_mismatch'),
            (candidate(), 'verified', False, 'crop_image_missing'),
            (candidate(geometry_valid='false'), 'verified', True, 'geometry_invalid'),
            (candidate(x1='10'), 'verified', True, 'coordinates_invalid'),
        ]:
            with self.subTest(expected=expected):
                result = evaluate_candidate(row, source_pdf_status=source_status, crop_exists=crop_exists)
                self.assertFalse(result['eligible'])
                self.assertIn(expected, result['reasons'])

    def test_multiline_overlength_and_suspicious_characters_stay_pending(self):
        for row, expected in [
            (candidate(pdf_text_line_count='2'), 'multiple_lines'),
            (candidate(pdf_text='A' * 91, ocr1_text='A' * 91), 'overlength'),
            (candidate(pdf_text='Mã\ufffd số'), 'replacement_character'),
            (candidate(pdf_text='Mã\x01 số'), 'control_character'),
        ]:
            with self.subTest(expected=expected):
                result = evaluate_candidate(row, source_pdf_status='verified', crop_exists=True)
                self.assertFalse(result['eligible'])
                self.assertIn(expected, result['reasons'])

    def test_low_unknown_or_out_of_range_confidence_stays_pending(self):
        for row, expected in [
            (candidate(confidence='0.89'), 'confidence_below_threshold'),
            (candidate(confidence=''), 'confidence_missing'),
            (candidate(confidence='1.4'), 'confidence_invalid'),
            (candidate(ocr_model='unknown_engine'), 'confidence_source_unknown'),
        ]:
            with self.subTest(expected=expected):
                result = evaluate_candidate(row, source_pdf_status='verified', crop_exists=True)
                self.assertFalse(result['eligible'])
                self.assertIn(expected, result['reasons'])

    def test_prior_manual_decision_or_changed_draft_is_never_overwritten(self):
        for status in ('verified', 'rejected'):
            result = evaluate_candidate(candidate(), prior={'status': status, 'transcript': 'manual'}, source_pdf_status='verified', crop_exists=True)
            self.assertFalse(result['eligible'])
            self.assertIn('manual_decision_preserved', result['reasons'])
        result = evaluate_candidate(candidate(), prior={'status': 'needs_review', 'transcript': 'Nội dung đã sửa'}, source_pdf_status='verified', crop_exists=True)
        self.assertFalse(result['eligible'])
        self.assertIn('pending_draft_differs', result['reasons'])


if __name__ == '__main__':
    unittest.main()
