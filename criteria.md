# TakeMeter Unit 5 — Acceptance criteria (AI DRAFT: student must review and choose targets before training)

These are proposed criteria; approve or revise them yourself BEFORE running the training notebook. Once finalized, commit this file before `results.json` exists.

1. **Overall accuracy:** At least **0.68** on the held-out 15% test split using seed 42.
   **Why:** Three classes give a chance-level reference around 0.33 for balanced guessing, so 0.68 would indicate practically useful discrimination on unfamiliar posts.

2. **Macro F1:** At least **0.62** on the held-out set.
   **Why:** Macro F1 weights all three classes equally, so the model cannot meet the target simply by being good at the biggest class.

3. **Per-label F1:** Each of `debugging`, `implementation`, and `conceptual` should have test-set **F1 of at least 0.50**.
   **Why:** Even a good overall score would not be useful if one type of programming question is systematically misclassified.

4. **Dataset label balance:** No individual class should exceed **55%** of the 220 labeled examples once human review is complete.
   **Why:** The course allows as much as 70%, but a 55% cap sets a stronger, transparent safeguard against majority-class guessing. Verify this against `labels.csv` before training.

5. **Confidence calibration:** The model's accuracy among its top-confidence third of held-out predictions should exceed its bottom-confidence third by at least **0.10** (10 percentage points).
   **Why:** High-confidence guesses should be more reliable than low-confidence ones. The notebook records this comparison in `results.json`.
