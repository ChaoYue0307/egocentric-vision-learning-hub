# From First-Person Video To World Memory

Egocentric vision is powerful because it observes the world from the same
viewpoint as a person or embodied agent. The same video episode can answer three
connected questions:

1. What is the wearer doing?
2. Where is the camera moving in 3D space?
3. What objects and relations should be remembered?

## Part 1: Action Understanding

The action baseline repo starts with short temporal windows. Each window turns
RGB frames and hand joints into feature vectors, then compares a majority
baseline, a softmax classifier, and an optional MLP head. The key lesson is that
evaluation design matters: chronological splits are stricter than random
overlapping-window splits, and multi-episode evaluation is the next step toward
research-quality evidence.

## Part 2: 3D Reconstruction

The reconstruction repo prepares the geometry layer. It extracts frames, exports
camera calibration, aligns frames to SLAM poses, and writes COLMAP/NeRF/3DGS
command templates. When COLMAP is installed, the parser summarizes sparse
models and compares registered image poses against nearest SLAM poses. The key
lesson is that reconstruction quality starts with diagnostics before training
any neural renderer.

## Part 3: Scene Graph Memory

The scene graph repo turns observations into structured memory: objects,
relations, timestamps, provenance, and queries. Caption-derived objects provide
a transparent starting point, while detector/tracker JSON can be merged later.
The key lesson is that a graph is useful only when every fact records where it
came from and how confident the system should be.

## Why The Three Pieces Belong Together

Action recognition explains intention. Reconstruction explains geometry. Scene
graphs explain persistent state. Together they form a practical learning path
for egocentric video systems that need to understand tasks, space, and objects.

## Current Evidence

- Live tutorial pages for each project.
- Unit tests, CI, versioned docs, and `v0.1.0` releases.
- Real sample artifacts generated from one Xperience-10M pour-over coffee
  episode.
- A clear path to extend the work with more episodes, real detector outputs,
  and full COLMAP/NeRF/3DGS runs.
