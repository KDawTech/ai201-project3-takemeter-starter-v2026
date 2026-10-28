# Unit 6 — The Test

**Evidence status:** INCOMPLETE. Missing: agreement_results.json (requires TF's staff labels).

## Baseline vs. Trained

The baseline is a zero-shot model scored on the same held-out questions saved in `test_split.csv` by Unit 5. Its exact test-set comparison can be claimed only when `baseline_results.json` records `held_out: true` and the same sample count.

| Measure | Baseline | Unit 5 trained | Difference (trained - baseline) |
|---|---:|---:|---:|
| Overall accuracy | 0.333 | 0.515 | 0.182 |
| Macro F1 | 0.335 | 0.227 | -0.108 |
| F1 — `debugging` | 0.375 | 0.000 | -0.375 |
| F1 — `implementation` | 0.200 | 0.680 | 0.480 |
| F1 — `conceptual` | 0.429 | 0.000 | -0.429 |

Baseline model: `facebook/bart-large-mnli`; evaluated posts: 33; held-out comparison: `True`; used label definitions: `True`.

**Prediction written before baseline:** See [UNIT6_BASELINE_PREDICTION.md](UNIT6_BASELINE_PREDICTION.md). Verify it was committed before the baseline was run.

**Measured interpretation:** The trained model's macro-F1 was 0.108 lower than zero-shot. A higher baseline suggests that training on this dataset did not yet improve generalization; a higher trained score supports a benefit of fine-tuning. This is an observation, not an explanation of cause by itself.

## Run Log — Before

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---:|---:|---:|---|
| 1. Overall accuracy | ≥ 0.680 | 0.515 | 0.515 | 0.515 | MISSED |
| 2. Macro F1 | ≥ 0.620 | 0.227 | 0.227 | 0.227 | MISSED |
| 3. Minimum per-label F1 | ≥ 0.500 for every label | 0.000 | 0.000 | 0.000 | MISSED |
| 4. Largest dataset label share | ≤ 0.550 | 0.509 | 0.509 | 0.509 | MET |
| 5. Confidence accuracy gap | ≥ 0.100 | 0.545 | 0.000 | 0.091 | MISSED |

Targets are carried forward from `criteria.md`; any missed target is reported as MISSED rather than rewritten after seeing results. The dataset-balance criterion is the same fixed value in all three seed columns.

### Confusion matrix (seed 42, before)

| true \ predicted | debugging | implementation | conceptual |
|---|---:|---:|---:|
| debugging | 0 | 7 | 0 |
| implementation | 0 | 17 | 0 |
| conceptual | 0 | 9 | 0 |

**Largest off-diagonal:** 9 real `conceptual` posts predicted as `implementation`; the reverse direction is 0. This points to a specific label boundary or majority-class prediction problem, not just a generic model error.
**Seed stability:** accuracy ranged from 0.515 to 0.515; spread 0.000.

## Verdicts and Diagnoses

Overall accuracy missed on one or more seeds. Macro F1 missed on one or more seeds. One or more classes fell below F1 0.50, reflecting uneven separation of the three labels. Higher-confidence predictions were not consistently at least 10 points more accurate.

**Annotation-quality limitation:** 108 of 220 dataset rows are marked 'student review required'. This is evidence of provisional annotation quality, not proof that any particular disagreement is wrong. Staff agreement may strengthen or challenge that hypothesis when completed.

## Agreement Report

Not measured: `data/staff_labels.csv` is supplied by the teaching fellow AFTER independent labeling. The public starter does not include it. Run `unit6_staff_labeler.py` to make your own labels, obtain the answer key, then run `agreement.py`. Do not invent staff answers or an agreement percentage.

## The Improvement

**One change:** keep the same original data, model, three seeds, optimizer settings, 70/15/15 splits, and labels, but use inverse-frequency-weighted cross entropy in the `after` training runs. The implementation is in `unit6_three_seeds.py` (the `WeightedTrainer` class). This directly targets the Unit 5 failure mode where the classifier selected `implementation` for every held-out example; smaller classes receive larger loss weights.

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---:|---:|---:|---|
| 1. Overall accuracy | ≥ 0.680 | 0.455 | 0.333 | 0.485 | MISSED |
| 2. Macro F1 | ≥ 0.620 | 0.417 | 0.328 | 0.336 | MISSED |
| 3. Minimum per-label F1 | ≥ 0.500 for every label | 0.308 | 0.286 | 0.000 | MISSED |
| 4. Largest dataset label share | ≤ 0.550 | 0.509 | 0.509 | 0.509 | MET |
| 5. Confidence accuracy gap | ≥ 0.100 | 0.000 | 0.182 | 0.364 | MISSED |

**Measured change:** mean accuracy 0.515 → 0.424 (-0.091); mean macro F1 0.227 → 0.360 (0.134).
**Interpretation:** The improvement raised mean macro F1 across the three seeds. A change in the intended direction is evidence it helped this dataset, but does not prove it generalizes beyond these 220 posts.

## What's Still Broken

- Seed 42 still has F1 under 0.50 for: debugging, conceptual.
- Seed 7 still has F1 under 0.50 for: debugging, implementation, conceptual.
- Seed 2024 still has F1 under 0.50 for: debugging, conceptual.
- The three-category boundary is not consistently strong enough on the held-out examples. A larger genuinely reviewed dataset and clearer boundary decisions would be next steps.
- 108 AI-suggested labels remain unreviewed. They should be independently checked; until then, a mislabeled training set remains a plausible source of error.
- Staff-agreement evidence is unavailable without the teaching fellow's answer key; it cannot yet separate annotator inconsistency from a model-capacity problem.
