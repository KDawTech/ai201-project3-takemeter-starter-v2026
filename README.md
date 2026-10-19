# TakeMeter

**AI201 — Project 3, Unit 5: Build**

See [RUNNING.md](RUNNING.md) for setup and execution instructions. This repository continues into **Unit 6**; Unit 6 evaluation sections are intentionally unfinished.

## What This Does

TakeMeter is a supervised text classifier for real questions from the public [Stack Overflow](https://stackoverflow.com/) community tagged `python`. It sorts questions into three categories: **`debugging`** (troubleshooting existing behavior), **`implementation`** (building or changing a feature), and **`conceptual`** (understanding a programming idea or tool).

The dataset contains **220 unique public questions** collected through the Stack Exchange API. The starter notebook, `takemeter.ipynb`, provides the data split, training, and evaluation logic for a locally fine-tuned `distilbert-base-uncased` model. The completed training run saved its metrics in `results.json` and its held-out examples in `test_split.csv`.

## Label Taxonomy

### `debugging`

**Definition:** A question about diagnosing or fixing code or a program that already fails, throws an error, or behaves unexpectedly.

**Examples from the collected posts:**

- "Screen blanks after executing .py file in Geany"
- "Playwright installation fails on Linux Mint Gigi"

### `implementation`

**Definition:** A question about writing, configuring, or changing code to accomplish a particular task or feature, when an existing malfunction is not the main problem.

**Examples from the collected posts:**

- "How can I color specific words in live time in a QTextEdit?"
- "How to get both losses and detection predictions from Torchvision Faster R-CNN in training mode and vice versa?"

### `conceptual`

**Definition:** A question primarily seeking an explanation of why or how a language, library, algorithm, or other programming concept works.

**Examples from the collected posts:**

- "Does importing modules which are only used for type-checking have any runtime overhead?"
- "Where is the Python documentation for handling ties with the built-in min function?"

### Hardest boundary: `debugging` versus `implementation`

**Decision rule:** When a post identifies an error or unexpected output from an existing program and asks for a solution, choose `debugging`, even if the question begins "How can I …?" When the post is primarily seeking new functionality or a method to accomplish a task and does not report existing broken behavior, choose `implementation`. Choose `conceptual` when an explanation, rather than a fix or implementation, is the main deliverable.

This is the working decision rule used to distinguish the labels; final consistency should be assessed through review of the AI-suggested examples.

## The Dataset

**Community and collection:** 220 unique public Stack Overflow questions tagged `python`, retrieved using the Stack Exchange API. The collection file `raw_posts.csv` contains source IDs and URLs. `labels.csv` contains the complete post text and the required `text`, `label`, `note` columns; the rows are not manually split into training and test files. The notebook performs a stratified 70/15/15 split.

**Annotation process:** The first **20 rows** have labels and the note `cold`, from the initial independent labeling step. The other **200 rows** received AI-suggested labels. At the point of this submission, **92** of those suggestions are marked `AI pre-labeled; reviewed and corrected`, while **108** remain marked `AI pre-labeled; student review required`. The unreviewed rows were nevertheless used in the completed training run, so the labels are **provisional rather than a fully verified human-labeled dataset**. This is a remaining limitation, not a claim that all 220 examples were manually checked.

### Label counts

| Label | Count | Share |
|---|---:|---:|
| `debugging` | 48 | 21.8% |
| `implementation` | 112 | 50.9% |
| `conceptual` | 60 | 27.3% |
| **Total** | **220** | **100.0%** |

No label exceeds the assignment's 70% cap. The counts are drawn from the labeled file, not from model predictions.

### Three challenging boundary examples

These are **candidate hard cases identified for further personal adjudication**, rather than claims that I reviewed and resolved them independently:

1. **"Why does Pyright reject protocol methods with a 'pass' body?"** Could be `conceptual` or `debugging`. The provisional choice is `conceptual`, because the question appears to ask about the type checker's rule rather than diagnosing broken application code.
2. **"How do I safely remove unused asyncio locks without causing duplicate requests?"** Could be `implementation` or `debugging`. The provisional choice is `implementation`, because the user is asking for a concurrency design pattern.
3. **"How to get both losses and detection predictions from Torchvision Faster R-CNN in training mode and vice versa?"** Could be `implementation` or `conceptual`. The provisional choice is `implementation`, because the desired outcome is to obtain specific outputs in code.

Before claiming these as **personal** hard-case judgments, I still need to read and adjudicate the complete questions.

## The Training Run

**Base model:** `distilbert-base-uncased`  
**Epochs:** 3  
**Learning rate:** `2e-5`  
**Batch size:** 16  
**Maximum sequence length:** 128 tokens  
**Random seed:** 42  
**Split:** 70% train / 15% validation / 15% test (**154 / 33 / 33 posts**)  
**Device:** CPU (PyTorch `2.14.1+cpu`)

Training was run locally from the TakeMeter project environment using the notebook's Unit 5 training logic. The completed held-out evaluation produced:

| Metric | Result |
|---|---:|
| Test examples | 33 |
| Accuracy | 0.5152 (51.5%) |
| Macro F1 | 0.2267 (22.7%) |

These are the actual recorded results in `results.json`; they are **not target numbers** and should not be confused with the draft acceptance criteria. The classifier predicted `implementation` for all 33 held-out posts, which limits its ability to distinguish the three categories. Further error analysis belongs in Unit 6.

## How I Used AI

**Moment 1 — data collection:** An initial script attempted to collect posts from r/VALORANT, but Reddit returned HTTP 403. I used AI to help create a replacement collector using the public Stack Exchange API. The replacement collected **220 real questions**, rather than generating synthetic examples, and wrote `raw_posts.csv` and `labels.csv`.

**Moment 2 — taxonomy and assisted annotation:** I used AI to draft the three-category taxonomy, a preliminary decision rule, acceptance criteria, and 200 proposed post labels. I completed the cold-label step for the first 20 questions. The other 200 were AI-pre-labeled; 92 are marked reviewed and corrected, while 108 remain unverified. I should review the remaining suggestions before treating the dataset as consistently human annotated.

**Acceptance-criteria disclosure:** `criteria.md` still contains a note that its numeric targets were AI-drafted and required my review. The training run has already happened; the README should not imply that I independently approved those criteria before training if I did not.

---

# Unit 6 — To Be Completed in the Next Unit

Unit 6 continues **in the same repository**. The tables below are placeholders. No baseline, three-seed comparison, agreement score, or after-improvement outcome is claimed until it has actually been run.

## Baseline vs. Trained

| Measure | Baseline | Trained | Difference |
|---|---:|---:|---:|
| Overall accuracy | — | — | — |
| Macro F1 | — | — | — |
| F1 — `debugging` | — | — | — |
| F1 — `implementation` | — | — | — |
| F1 — `conceptual` | — | — | — |

**Prediction written before seeing baseline numbers:** To be completed before the baseline run.

**What the comparison means:** To be completed.

## Run Log — Before

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | 0.68 | — | — | — | — |
| 2. Macro F1 | 0.62 | — | — | — | — |
| 3. All per-label F1 scores | 0.50 each | — | — | — | — |
| 4. Largest label share | ≤ 55% | — | — | — | — |
| 5. Top-vs-bottom confidence accuracy gap | ≥ 0.10 | — | — | — | — |

### Confusion matrix

*Paste the actual markdown table printed by the notebook's Unit 6 evaluation. Do not invent counts.*

## Verdicts and Diagnoses

*For each criterion, compare the three real seed runs with the predeclared targets. Use the agreement report to distinguish labeling inconsistency from model limitations.*

## Agreement Report

*Label the 30 staff posts using the staff taxonomy, run `agreement.py`, and adjudicate each disagreement. No agreement results are available yet.*

## The Improvement

*Describe one specific change informed by the diagnosed weaknesses. Rerun with the `after` label and compare with the three-seed `before` results.*

## What's Still Broken

*Document any criteria that still fail after the improvement and why.*

---

**How to run:** [RUNNING.md](RUNNING.md)
