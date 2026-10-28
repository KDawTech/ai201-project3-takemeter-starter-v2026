"""Create a source-grounded Unit 6 report from REAL generated evidence.

Usage:
  python unit6_finalize.py
  python unit6_finalize.py --apply

--apply replaces only the existing Unit 6 section of README.md. It refuses to
apply an incomplete report unless --allow-incomplete is explicitly passed.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABELS = ["debugging", "implementation", "conceptual"]
SEEDS = [42, 7, 2024]
REPO_SECTION = "# Unit 6 — To Be Completed in the Next Unit"


def load(name):
    p = ROOT / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def fmt(v):
    return "—" if v is None else f"{v:.3f}"


def r_metric(r, k):
    if k == "accuracy": return r["accuracy"]
    if k == "macro_f1": return r["f1_macro"]
    if k == "min_f1": return min(r["per_label"][l]["f1"] for l in LABELS)
    if k == "confidence_gap":
        c=r["confidence"]
        return c["accuracy_most_confident_third"]-c["accuracy_least_confident_third"]
    raise ValueError(k)


def clean_three(blob):
    if not isinstance(blob, list) or sorted(x.get("seed") for x in blob) != sorted(SEEDS):
        return None
    return sorted(blob, key=lambda r: SEEDS.index(r["seed"]))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true", help="Replace README Unit 6 section after evidence is complete")
    p.add_argument("--allow-incomplete", action="store_true", help="Explicitly permit unfinished report, labeled incomplete")
    args=p.parse_args()
    before=clean_three(load("results_three_seeds_before.json"))
    after=clean_three(load("results_three_seeds_after.json"))
    baseline=load("baseline_results.json")
    trained=load("results.json")
    agreement=load("agreement_results.json")
    adjudications=load("unit6_adjudications.json") or {}
    prediction=ROOT / "UNIT6_BASELINE_PREDICTION.md"
    dataset=ROOT / "labels.csv"
    if not dataset.exists() or trained is None:
        p.error("Missing Unit 5 labels.csv or results.json. Use your original repository.")
    with dataset.open(encoding="utf-8-sig", newline="") as f:
        rows=list(csv.DictReader(f))
    counts=collections.Counter(r["label"] for r in rows)
    max_share=max(counts.values())/len(rows)
    unreviewed=sum("review required" in r.get("note", "").lower() for r in rows)
    trained_scores=trained
    base_scores=baseline.get("scores") if baseline else None
    missing=[]
    if not baseline: missing.append("baseline_results.json")
    if not before: missing.append("results_three_seeds_before.json (all three seeds)")
    if not after: missing.append("results_three_seeds_after.json (all three seeds)")
    if not agreement: missing.append("agreement_results.json (requires TF's staff labels)")
    if agreement and len(adjudications)<len(agreement.get("disagreements",[])):
        missing.append("written adjudications for every staff disagreement")
    if not prediction.exists(): missing.append("UNIT6_BASELINE_PREDICTION.md")
    bad_source=False
    if before and after:
        signatures={r.get("dataset_sha256") for r in before+after}
        if len(signatures)>1:
            bad_source=True
            missing.append("consistent dataset across before and after runs")
    status="COMPLETE" if not missing else "INCOMPLETE"
    report=[]
    add=report.append
    add("# Unit 6 — The Test")
    add("")
    add(f"**Evidence status:** {status}. " + ("All required inputs present." if not missing else "Missing: "+"; ".join(missing)+"."))
    add("")
    add("## Baseline vs. Trained")
    add("")
    add("The baseline is a zero-shot model scored on the same held-out questions saved in `test_split.csv` by Unit 5. Its exact test-set comparison can be claimed only when `baseline_results.json` records `held_out: true` and the same sample count.")
    add("")
    add("| Measure | Baseline | Unit 5 trained | Difference (trained - baseline) |")
    add("|---|---:|---:|---:|")
    measures=[("Overall accuracy", "accuracy"), ("Macro F1","f1_macro")]
    for l in LABELS:
        measures.append((f"F1 — `{l}`", l))
    for label,key in measures:
        def get(s):
            if not s: return None
            return s[key] if key in ["accuracy","f1_macro"] else s.get("per_label",{}).get(key,{}).get("f1")
        b,t=get(base_scores),get(trained_scores)
        diff=None if b is None or t is None else t-b
        add(f"| {label} | {fmt(b)} | {fmt(t)} | {fmt(diff)} |")
    add("")
    if baseline:
        add(f"Baseline model: `{baseline.get('model','unknown')}`; evaluated posts: {baseline.get('n','unknown')}; held-out comparison: `{baseline.get('held_out','unknown')}`; used label definitions: `{baseline.get('used_definitions','unknown')}`.")
    else:
        add("Baseline model not run yet; do not fill in numbers from guesswork.")
    add("")
    if prediction.exists():
        add("**Prediction written before baseline:** See [UNIT6_BASELINE_PREDICTION.md](UNIT6_BASELINE_PREDICTION.md). Verify it was committed before the baseline was run.")
    else:
        add("**Prediction:** Must be recorded before looking at the baseline output.")
    add("")
    if base_scores:
        delta=trained_scores["f1_macro"]-base_scores["f1_macro"]
        add(f"**Measured interpretation:** The trained model's macro-F1 was {fmt(abs(delta))} {'higher' if delta>0 else 'lower' if delta<0 else 'the same'} than zero-shot. A higher baseline suggests that training on this dataset did not yet improve generalization; a higher trained score supports a benefit of fine-tuning. This is an observation, not an explanation of cause by itself.")
    else:
        add("**Measured interpretation:** Waiting for actual baseline output.")
    add("")
    add("## Run Log — Before")
    add("")
    def runlog(arr):
        names=[
            ("Overall accuracy", "≥ 0.680", "accuracy",lambda v:v>=0.68),
            ("Macro F1", "≥ 0.620", "macro_f1", lambda v:v>=0.62),
            ("Minimum per-label F1", "≥ 0.500 for every label", "min_f1",lambda v:v>=0.50),
            ("Largest dataset label share", "≤ 0.550", "largest_share",lambda v:v<=0.55),
            ("Confidence accuracy gap", "≥ 0.100", "confidence_gap",lambda v:v>=0.10),
        ]
        out=["| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |",
             "|---|---|---:|---:|---:|---|"]
        for i,(name,target,key,ok) in enumerate(names, 1):
            vals=([max_share]*3 if key=="largest_share" else [r_metric(r,key) for r in arr] if arr else [None]*3)
            verdict="MET" if all(v is not None and ok(v) for v in vals) else "MISSED" if all(v is not None for v in vals) else "NOT MEASURED"
            out.append(f"| {i}. {name} | {target} | "+" | ".join(fmt(v) for v in vals)+f" | {verdict} |")
        return out
    report.extend(runlog(before))
    add("")
    add("Targets are carried forward from `criteria.md`; any missed target is reported as MISSED rather than rewritten after seeing results. The dataset-balance criterion is the same fixed value in all three seed columns.")
    add("")
    add("### Confusion matrix (seed 42, before)")
    add("")
    if before:
        mat=before[0]["confusion"]
        add("| true \\ predicted | "+" | ".join(LABELS)+" |")
        add("|---|---:|---:|---:|")
        for t in LABELS:
            add("| "+t+" | "+" | ".join(str(mat[t][p]) for p in LABELS)+" |")
        off=[(mat[t][p],t,p) for t in LABELS for p in LABELS if t!=p]
        worst,t,pred=max(off)
        add("")
        add(f"**Largest off-diagonal:** {worst} real `{t}` posts predicted as `{pred}`; the reverse direction is {mat[pred][t]}. This points to a specific label boundary or majority-class prediction problem, not just a generic model error.")
        accs=[r["accuracy"] for r in before]
        add(f"**Seed stability:** accuracy ranged from {fmt(min(accs))} to {fmt(max(accs))}; spread {fmt(max(accs)-min(accs))}.")
    else:
        add("Three-seed before evaluation is still required; no matrix has been invented.")
    add("")
    add("## Verdicts and Diagnoses")
    add("")
    if before:
        failed=[]
        accs=[r["accuracy"] for r in before]
        f1s=[r["f1_macro"] for r in before]
        if min(accs)<0.68: failed.append("Overall accuracy missed on one or more seeds.")
        if min(f1s)<0.62: failed.append("Macro F1 missed on one or more seeds.")
        if any(min(r["per_label"][l]["f1"] for l in LABELS)<0.5 for r in before):
            failed.append("One or more classes fell below F1 0.50, reflecting uneven separation of the three labels.")
        if max_share>0.55: failed.append("Dataset imbalance exceeded the predeclared 55% cap.")
        if any(r_metric(r,"confidence_gap")<0.10 for r in before): failed.append("Higher-confidence predictions were not consistently at least 10 points more accurate.")
        add(" " .join(failed) if failed else "All five targets were met across the three seeds.")
    else:
        add("The Unit 5 seed-42 result (accuracy 0.515, macro F1 0.227) predicted `implementation` for every held-out post. That is direct evidence of majority-class prediction collapse, but the required three-seed diagnosis must wait for `results_three_seeds_before.json`.")
    add("")
    add(f"**Annotation-quality limitation:** {unreviewed} of {len(rows)} dataset rows are marked 'student review required'. This is evidence of provisional annotation quality, not proof that any particular disagreement is wrong. Staff agreement may strengthen or challenge that hypothesis when completed.")
    add("")
    add("## Agreement Report")
    add("")
    if agreement:
        add(f"**Agreement:** {agreement.get('agreed','?')}/{agreement.get('compared','?')} = {fmt(agreement.get('agreement_rate'))}; calculated by `agreement.py` against the provided staff answer key using the staff's own taxonomy.")
        add("")
        for i,entry in enumerate(agreement.get("disagreements",[]),1):
            a=adjudications.get(str(i),{})
            add(f"**Disagreement {i}:** {entry['text']}")
            add(f"- Staff: `{entry['staff']}`; mine: `{entry['mine']}`")
            add(f"- My adjudication: {a.get('why') or 'NOT PROVIDED — human rationale required'}")
            add(f"- Category (a/b/c): `{a.get('pile') or 'NOT PROVIDED'}`")
            add("")
        if not agreement.get("disagreements"):
            add("No disagreements were found; a short personal reflection is still useful.")
    else:
        add("Not measured: `data/staff_labels.csv` is supplied by the teaching fellow AFTER independent labeling. The public starter does not include it. Run `unit6_staff_labeler.py` to make your own labels, obtain the answer key, then run `agreement.py`. Do not invent staff answers or an agreement percentage.")
    add("")
    add("## The Improvement")
    add("")
    add("**One change:** keep the same original data, model, three seeds, optimizer settings, 70/15/15 splits, and labels, but use inverse-frequency-weighted cross entropy in the `after` training runs. The implementation is in `unit6_three_seeds.py` (the `WeightedTrainer` class). This directly targets the Unit 5 failure mode where the classifier selected `implementation` for every held-out example; smaller classes receive larger loss weights.")
    add("")
    add("### Run Log — After")
    add("")
    report.extend(runlog(after))
    add("")
    if before and after:
        bacc=statistics.mean(r["accuracy"] for r in before)
        aacc=statistics.mean(r["accuracy"] for r in after)
        bf1=statistics.mean(r["f1_macro"] for r in before)
        af1=statistics.mean(r["f1_macro"] for r in after)
        add(f"**Measured change:** mean accuracy {fmt(bacc)} → {fmt(aacc)} ({fmt(aacc-bacc)}); mean macro F1 {fmt(bf1)} → {fmt(af1)} ({fmt(af1-bf1)}).")
        add("**Interpretation:** The improvement " + ("raised" if af1>bf1 else "lowered" if af1<bf1 else "did not change") + " mean macro F1 across the three seeds. A change in the intended direction is evidence it helped this dataset, but does not prove it generalizes beyond these 220 posts.")
    else:
        add("No after-run outcome has been claimed; run the three actual `after` seeds first.")
    add("")
    add("## What's Still Broken")
    add("")
    if after:
        for i,r in enumerate(after):
            failures=[l for l in LABELS if r["per_label"][l]["f1"]<0.5]
            if failures:
                add(f"- Seed {r['seed']} still has F1 under 0.50 for: {', '.join(failures)}.")
        if any(r["f1_macro"]<0.62 for r in after):
            add("- The three-category boundary is not consistently strong enough on the held-out examples. A larger genuinely reviewed dataset and clearer boundary decisions would be next steps.")
    else:
        add("An actual after evaluation is required to name which criteria remain missed.")
    if unreviewed:
        add(f"- {unreviewed} AI-suggested labels remain unreviewed. They should be independently checked; until then, a mislabeled training set remains a plausible source of error.")
    if not agreement:
        add("- Staff-agreement evidence is unavailable without the teaching fellow's answer key; it cannot yet separate annotator inconsistency from a model-capacity problem.")
    add("")
    content="\n".join(report).rstrip()+"\n"
    out=ROOT / "UNIT6_REPORT.md"
    out.write_text(content, encoding="utf-8")
    print(f"Wrote {out.name}. Status: {status}")
    if missing:
        print("Missing:")
        for name in missing:
            print("  -", name)
    if args.apply:
        if missing and not args.allow_incomplete:
            raise SystemExit("Refusing to update README with incomplete work. Complete the missing evidence, or pass --allow-incomplete to label it explicitly.")
        readme=ROOT / "README.md"
        if not readme.exists(): raise SystemExit("README.md not found")
        previous=readme.read_text(encoding="utf-8")
        marker=previous.find(REPO_SECTION)
        if marker < 0:
            raise SystemExit(f"README unit-6 heading not recognized. File {out.name} exists; append it manually after reviewing.")
        updated=previous[:marker].rstrip()+"\n\n---\n\n"+content+"\n"
        readme.write_text(updated, encoding="utf-8")
        print("Updated README.md, preserving all original Unit 5 content")

if __name__=="__main__":
    main()
