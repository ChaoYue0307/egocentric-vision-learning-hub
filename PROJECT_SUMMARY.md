# Egocentric Vision Portfolio Summary

This portfolio turns one Xperience-10M egocentric coffee-making sample into a
three-part learning path: action recognition, 3D reconstruction preparation, and
temporal scene graph memory. Each repository is intentionally small enough to
read, run, test, and extend.

## What Was Built

- Action understanding: https://github.com/ChaoYue0307/egocentric-action-baselines
  RGB, hand-joint, fusion, majority, and optional MLP baselines with metrics and ablations.
- Geometry readiness: https://github.com/ChaoYue0307/egocentric-3d-reconstruction-demo
  Frame extraction, calibration export, SLAM trajectory, COLMAP command templates, and COLMAP text-model parser.
- World memory: https://github.com/ChaoYue0307/scene-graph-from-egocentric-video
  Timestamped object/relation graph with query mode, detector provenance, and graph comparison.
- Learning hub: https://github.com/ChaoYue0307/egocentric-vision-learning-hub
  Live landing page, project narrative, and walkthrough links across all three demos.

## Evidence Included

- Live tutorials: https://chaoyue0307.github.io/egocentric-vision-learning-hub/
- Browser recordings: `docs/assets/walkthrough.webm` in each repository.
- Action artifacts: baseline summaries, confusion matrix SVG, and local episode discovery report.
- Reconstruction artifacts: frame manifest, contact sheet, dependency/COLMAP readiness report, and COLMAP parser path.
- Scene graph artifacts: sample graph JSON, visual-proposal detector JSON, detector-merged graph, graph comparison JSON, and timeline SVG.
- Engineering hygiene: tests, GitHub Actions CI, `ruff`, `pre-commit`, contribution guides, citation files, licenses, issue templates, and versioned `v0.1.0` docs snapshots.

## Current Results And Limits

The public Xperience-10M distribution currently provides one verified sample
episode for open reuse. The full multi-episode dataset is gated, so the action
repository includes discovery and batch-evaluation commands but does not claim
public multi-episode metrics beyond the available sample.

The scene graph detector path now uses real video-frame visual proposals from
OpenCV contours and records bounding boxes/tracks in detector-style JSON. This is
stronger than a purely annotation-grounded fixture, but it is still not a
trained object detector. The labels remain associated with graph-visible object
names.

COLMAP is supported through command templates, an availability checker, and a
text-model parser. On the current machine COLMAP is not installed, so no sparse
reconstruction is published as a real run result. Installing COLMAP with
Homebrew and rerunning `python scripts/run_colmap_if_available.py --run` is the
next step when system installation is available.

## Why It Matters

The projects show an end-to-end egocentric vision workflow without hiding the
interfaces: data contracts, model baselines, geometry artifacts, graph schemas,
runtime commands, and limitations are all inspectable. That makes the portfolio
useful both as a learning resource and as a foundation for stronger experiments
when more episodes, trained detectors, or local COLMAP are available.
