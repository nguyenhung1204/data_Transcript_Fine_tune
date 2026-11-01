import sys
import unittest
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(r'E:\KhoaLuanTotNghiep\data_Transcript_Fine_tune\recognition_dataset')
sys.path.insert(0, str(ROOT / 'automatic_review'))
from run_automatic_review import text_for_crop, normalized, visual_order_text


class PdfVisualOrderRegression(unittest.TestCase):
    def test_visual_order_keeps_raised_punctuation_and_multiple_lines(self):
        def glyph(text, left, center_y, height=5):
            return {
                'text': text, 'left': left, 'right': left + 2,
                'top_y': center_y + height / 2, 'bottom_y': center_y - height / 2,
                'center_y': center_y, 'height': height,
            }

        # Deliberately shuffled like PDF content streams; the apostrophe is raised.
        chars = [
            glyph('B', 18, 100), glyph('lower', 10, 91),
            glyph("'", 15, 103), glyph('A', 10, 100),
        ]
        text, lines = visual_order_text(chars)
        self.assertEqual(text, "A'B\nlower")
        self.assertEqual(lines, 2)

    def test_pdf_text_follows_left_to_right_visual_order(self):
        crop_id = '30027770f95dd4d81c37'
        import csv
        with (ROOT / 'automatic_review' / 'automatic_review_manifest.csv').open(encoding='utf-8-sig', newline='') as f:
            row = next(r for r in csv.DictReader(f) if r['crop_id'] == crop_id)
        document = pdfium.PdfDocument(str(ROOT / 'source_300_invoices' / 'pdfs' / row['filename']))
        page = document[int(row['page']) - 1]
        textpage = page.get_textpage()
        actual, valid, reason, _ = text_for_crop(page, textpage, row, 300)
        page.close()
        document.close()
        self.assertTrue(valid, reason)
        self.assertEqual(normalized(actual), "Tên đơn vị (Company's name) : CÔNG TY CỔ PHẦN NGÂN ĐỨC")


if __name__ == '__main__':
    unittest.main()
