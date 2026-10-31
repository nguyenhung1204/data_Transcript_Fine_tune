import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_workflow import apply_review_annotations


class ReviewAnnotationTests(unittest.TestCase):
    def test_verified_annotation_promotes_corrected_transcript(self):
        rows = [{"crop_id": "a", "label_source": "ocr_pseudo_label", "label_status": "needs_review", "transcript": "OCR text"}]
        result = apply_review_annotations(rows, {"version": 1, "annotations": [{"crop_id": "a", "status": "verified", "transcript": "Chữ đúng", "reviewed_at": "now"}]})
        self.assertEqual(result[0]["transcript"], "Chữ đúng")
        self.assertEqual(result[0]["label_status"], "verified")
        self.assertEqual(result[0]["label_source"], "human_visual_review")

    def test_rejects_empty_or_multiline_verified_transcript(self):
        row = {"crop_id": "a", "label_source": "ocr_pseudo_label", "label_status": "needs_review", "transcript": "OCR text"}
        for text in ("", "   ", "hai\ndòng", "có\ttab"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                apply_review_annotations([row.copy()], {"version": 1, "annotations": [{"crop_id": "a", "status": "verified", "transcript": text}]})

    def test_verified_transcript_must_fit_90_character_training_limit(self):
        row = {"crop_id": "a", "label_source": "ocr_pseudo_label", "label_status": "needs_review", "transcript": ""}
        result = apply_review_annotations([row.copy()], {"version": 1, "annotations": [{"crop_id": "a", "status": "verified", "transcript": "x" * 90}]})
        self.assertEqual(result[0]["label_status"], "verified")
        with self.assertRaises(ValueError):
            apply_review_annotations([row.copy()], {"version": 1, "annotations": [{"crop_id": "a", "status": "verified", "transcript": "x" * 91}]})

    def test_review_page_shows_coordinates_and_confidence_filter(self):
        from review_workflow import build_review_html
        row = {"crop_id": "a", "document_id": "INV-1", "filename": "a.pdf", "page": 1,
               "split": "train", "confidence": 0.5, "crop_path": "crops/INV-1/a.png",
               "x0": 1, "y0": 2, "x1": 30, "y1": 20, "transcript": "x" * 91,
               "raw_ocr_text": "x" * 91, "label_status": "needs_review"}
        page = build_review_html([row])
        self.assertIn("confidence", page)
        self.assertIn("tọa độ", page)
        self.assertIn("90", page)

    def test_does_not_overwrite_manually_verified_crop(self):
        row = {"crop_id": "a", "label_source": "user_confirmed_labeler_crop", "label_status": "verified", "transcript": "Giữ nguyên"}
        result = apply_review_annotations([row], {"version": 1, "annotations": [{"crop_id": "a", "status": "verified", "transcript": "Thay thế"}]})
        self.assertEqual(result[0]["transcript"], "Giữ nguyên")

    def test_rejects_unknown_or_duplicate_crop_ids(self):
        row = {"crop_id": "a", "label_source": "ocr_pseudo_label", "label_status": "needs_review", "transcript": "OCR text"}
        with self.assertRaises(ValueError):
            apply_review_annotations([row], {"version": 1, "annotations": [{"crop_id": "missing", "status": "verified", "transcript": "ok"}]})
        with self.assertRaises(ValueError):
            apply_review_annotations([row], {"version": 1, "annotations": [{"crop_id": "a", "status": "rejected"}, {"crop_id": "a", "status": "verified", "transcript": "ok"}]})


if __name__ == "__main__":
    unittest.main()
