# Implementation ledger

- Ruling: Require OCR1 confidence >= 0.90 only for recognized PaddleOCR `rec_scores` in the observed 0–1 scale; the source normalizer reads `rec_scores` as floats and the active manifest records PaddleOCR engines. This is deliberately stricter than merely copying PDF text; cost if wrong: some valid transcripts remain for manual review.
- Ruling: Keep bulk apply behind an explicit user button and run only a dry-run during implementation; the brief requires an explicit apply action and there is live user progress. Cost if wrong: users must perform one final click to apply confirmed candidates.
- Ruling: No Git worktree/commit; the repository currently treats the dataset project as untracked, and the brief limits writes to `automatic_review/`. Cost if wrong: no isolated branch/history is provided.

## Progress

- [x] Inspect current app, 17,961-row manifest, PDF/OCR confidence provenance, and live annotation count.
- [x] Add policy regression tests and observe expected failure while the policy module is absent.
- [x] Implement and pass policy tests: PDF/OCR1 agreement, confidence, one-line/90-character limit, geometry/source/crop checks, Unicode errors, and manual/draft preservation.
- [x] Add preview/apply APIs with progress locking, stale-token rejection, backup before apply, and merge-safe annotation saves.
- [x] Add dry-run/apply controls and uncertainty-only warning counts to the web UI; page load does not save or apply labels.
- [x] Fix “Bỏ qua lúc này”: keep the draft pending, hide that item for the current browser session, and show an explanatory empty state; make “Loại crop” wait for confirmed server save.
- [x] Run 8 unit tests, Python compilation and browser-script syntax validation; dry-run over 17,961 crops found 6,767 eligible and preserved 124 manual decisions. SHA-256 of `manual_review_progress.json` was unchanged.
- [x] Restart the localhost server at port 8768 with the new API implementation; live HTTP checks returned the updated UI and a successful dry-run preview.
- [x] POST with a stale dry-run token returned HTTP 409; progress SHA-256 remained unchanged. No auto-confirm was applied.
