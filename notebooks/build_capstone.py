#!/usr/bin/env python3
"""Build and execute the capstone notebook from the three sibling repos' committed artifacts."""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf


def md(source: str):
    return nbf.v4.new_markdown_cell(source)


def code(source: str):
    return nbf.v4.new_code_cell(source)


CELLS = [
    md("""# From Pixels To World Memory

One Xperience-10M pour-over coffee episode, three repositories, one connected story:

1. **[egocentric-action-baselines](https://github.com/ChaoYue0307/egocentric-action-baselines)** — what is the wearer *doing*?
2. **[egocentric-3d-reconstruction-demo](https://github.com/ChaoYue0307/egocentric-3d-reconstruction-demo)** — what does the *space* look like, and is the footage even reconstructable?
3. **[scene-graph-from-egocentric-video](https://github.com/ChaoYue0307/scene-graph-from-egocentric-video)** — what does the system *remember* about objects, interactions, and places?

This notebook runs entirely from the **committed artifacts** of the three sibling repositories — no raw dataset download is needed. Clone all four repos into one parent directory and run top to bottom."""),
    code("""import json
from pathlib import Path

ROOT = Path.cwd().resolve()
while not (ROOT / "egocentric-action-baselines").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

ACTION = ROOT / "egocentric-action-baselines"
RECON = ROOT / "egocentric-3d-reconstruction-demo"
GRAPH = ROOT / "scene-graph-from-egocentric-video"

def load(path):
    if not path.exists():
        print(f"missing: {path} — clone the sibling repo next to this hub")
        return None
    return json.loads(path.read_text(encoding="utf-8"))

action_summary = load(ACTION / "outputs/sample_ablation/summary.json")
dino = load(ACTION / "outputs/dino_ablation/summary.json")
chrono = load(ACTION / "outputs/split_comparison/chronological/summary.json")
strat = load(ACTION / "outputs/split_comparison/stratified/summary.json")
quality = load(RECON / "outputs/sample_demo/frame_quality.json")
hand_masks = load(RECON / "outputs/cam1_hand_mask_demo/hand_mask_report.json")
scene_graph = load(GRAPH / "outputs/sample_graph/scene_graph.json")
qa = load(GRAPH / "outputs/qa_eval/qa_results.json")
qa_detector = load(GRAPH / "outputs/qa_eval_detector/qa_results.json")
triangulation = load(GRAPH / "outputs/triangulated_graph/triangulation_summary.json")
print("artifacts loaded:", all(x is not None for x in [action_summary, dino, chrono, strat, quality, scene_graph, qa, qa_detector, triangulation]))"""),
    md("""## Stage 1 — Action: hands beat pixels, and the split decides everything

The action repo trains three tiny baselines (RGB, hand joints, early/late fusion) on 1093
temporal windows across 18 action classes. The headline is not any single number — it is
how violently the numbers move when the evaluation split changes."""),
    code("""def row(name, experiments):
    m = experiments.get(name)
    return f"{name:28s} acc={m['accuracy']:.3f}  macroF1={m['macro_f1']:.3f}" if m else f"{name:28s} (not run)"

print("blocked-instance split (honest within-episode):")
for name in ["rgb_only_majority", "rgb_only", "hand_joints_only", "rgb_hand_fusion", "rgb_hand_late_fusion"]:
    print(" ", row(name, action_summary["experiments"]))

print()
hand = "hand_joints_only"
print(f"the same hand-joint model under three splits:")
print(f"  stratified (leaky):        {strat['experiments'][hand]['accuracy']:.3f}")
print(f"  chronological (label shift): {chrono['experiments'][hand]['accuracy']:.3f}")
print(f"  blocked-instance (honest):   {action_summary['experiments'][hand]['accuracy']:.3f}")"""),
    md("""Three orders of magnitude of difference from evaluation design alone. Hand motion is the
strongest honest cue (0.47 vs the 0.14 majority floor); appearance features mostly memorize
the kitchen. Keep that in mind for Stage 3 — the scene graph will show *why* hands carry
the signal."""),
    code("""print("does a stronger visual backbone change the verdict? (frozen DINOv2, same head + split)")
for name in ["rgb_only", "rgb_hand_fusion"]:
    print(f"  {name:18s} handcrafted={action_summary['experiments'][name]['accuracy']:.3f} -> dino={dino['experiments'][name]['accuracy']:.3f}")
print(f"  hand_joints_only stays {action_summary['experiments']['hand_joints_only']['accuracy']:.3f} and still wins")"""),
    md("""## Stage 2 — Reconstruction readiness: measure, don't guess

Before any COLMAP run, the recon repo quantifies what reconstruction actually consumes:
sharp frames and feature overlap — and masks the one thing guaranteed to violate the
static-scene assumption: the wearer's hands."""),
    code("""print(f"frames sampled: {quality['num_frames']}  blurry: {quality['num_blurry']}  low-overlap pairs: {quality['num_low_overlap']}")
print(f"mean RANSAC-verified inliers between frames: {quality['mean_geometric_inliers']} (inlier ratio {quality['mean_inlier_ratio']})")
print()
sel = hand_masks["convention_selection"] if hand_masks else None
if sel:
    print("hand-mask extrinsic chain, selected empirically from 4 candidates:")
    for label, score in sel["candidates"].items():
        marker = " <-- selected" if label == sel["selected_chain"] else ""
        print(f"  {label:32s} in_bounds={score['in_bounds_fraction']:.3f} depth={score['median_depth_m']}{marker}")
    print(f"mean masked fraction on cam1: {hand_masks['mean_masked_fraction']:.1%}")"""),
    md("""The lesson that generalizes: **extrinsic conventions are verified by geometry, not field
names** — two of the four plausible compositions put every joint behind the camera, and the
fisheye's huge field of view makes "it projects in bounds" insufficient on its own (an
arm's-length depth prior breaks the tie)."""),
    md("""## Stage 3 — World memory: what the system can answer afterwards

The scene graph turns the same episode into object-centric memory with provenance, scored
against 33 human-labeled QA pairs."""),
    code("""meta = scene_graph["metadata"]
print(f"graph: {meta['num_frames']} frames, {meta['num_objects']} objects, {meta['num_relations']} relations")
print("most-observed objects:", ", ".join(f"{o} ({n})" for o, n in meta["top_objects"][:5]))
print(f"QA benchmark (caption-grounded): {qa['num_correct']}/{qa['num_questions']} = {qa['accuracy']:.3f}")
print(f"QA benchmark (detector-only):    {qa_detector['num_correct']}/{qa_detector['num_questions']} = {qa_detector['accuracy']:.3f}  <- the perception gap")
print("the gap is coverage: undetected objects break existence/order queries, not action/subtask")"""),
    code("""print("triangulated object positions (detector boxes + camera poses, residual-gated):")
for oid, r in triangulation["objects"].items():
    print(f"  {oid:10s} xyz={r['xyz']} residual={r['residual_m']:.3f}m reliable={r['reliable']}")"""),
    code("""kettle = scene_graph["objects"]["kettle"]
trail = kettle.get("camera_trail", [])
print("WHERE DID I LAST SEE THE KETTLE?")
print(f"  last seen at device timestamp {kettle['last_seen']}")
print(f"  wearer position then: {kettle.get('last_seen_camera_xyz')}")
print(f"  sightings with pose: {len(trail)} of {kettle['observations']} observations")

last_ts = kettle["last_seen"]
state_frame = min(scene_graph["frames"], key=lambda f: abs(int(f["timestamp"]) - int(last_ts)))
print(f"  task state at that moment: subtask={state_frame['subtask']!r} action={state_frame.get('action')!r}")

hand_rel = [r for r in scene_graph["relations"] if r["type"].startswith("hand_") and r["object"] == "kettle"]
print(f"  hand-kettle interactions on record: {len(hand_rel)} (e.g. {hand_rel[0]['type']})")"""),
    md("""## Synthesis — one episode, one connected picture

- **Hands are the through-line.** Hand joints are the best action cue (Stage 1), hands are
  what reconstruction must mask out (Stage 2), and hand-object relations dominate the
  interaction memory (Stage 3). Egocentric vision is, to a first approximation, the study
  of hands and what they touch.
- **Honesty compounds.** The blocked-instance split, the empirically-selected extrinsic
  chain, and the QA gold pairs are all the same idea applied three times: build the check
  before trusting the number.
- **Spatial memory is the meeting point.** SLAM poses flow into the action features'
  evaluation context, into reconstruction readiness, and into "where did I last see X" —
  the first genuinely world-model-shaped question this stack can answer.

**Where to go next:** more episodes unlock the `grouped-segment` split (cross-instance
action generalization), detector-sourced graphs turn the QA set into a perception
benchmark, and COLMAP runs with/without hand masks measure the masks' value directly."""),
]


def main() -> int:
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python", "version": "3"}
    nb.cells = CELLS
    out = Path(__file__).parent / "capstone_pixels_to_world_memory.ipynb"

    from nbclient import NotebookClient

    client = NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(Path(__file__).parent)}})
    client.execute()
    nbf.write(nb, out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
