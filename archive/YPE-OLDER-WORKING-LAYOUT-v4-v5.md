# Older Working YPE Layout — v4/v5 Practical Completion Model

Purpose: a side-by-side reference for the simpler YPE approach that was known to move from beginning to completion more reliably.

This is reconstructed from archived YPE v5 files and historical run notes, especially:
- `skills/youtube-pipeline/archive/SKILL-v5.0-original.md`
- `skills/youtube-pipeline/archive/RUNBOOK-v5.0.md`
- `skills/youtube-pipeline/archive/YPE-TRIGGER-v5.8.md`
- memory notes from v4.5/v5.8 runs

Known working evidence:
- v4.5 Claw playlist: 90 transcripts downloaded, 70/90 frame extractions passed, individual long video with 652 frames.
- Mar 16 architecture batch: 12 videos, 8,863 frames captured, `MASTER-COMPILATION.md` delivered.
- Apr 1 v6.5.2 batch still retained the practical completion speed: 45 videos in ~1h 8m with NotebookLM audio/slides completed.

---

## Core Philosophy
Older YPE was less elegant but more direct:

1. Get transcripts.
2. Get frames.
3. Generate enhanced transcripts.
4. Generate reports.
5. Generate infographics.
6. Compile the knowledge.
7. Deliver.

The strength was forward motion. The weakness was that sub-agents could create stubs unless checked.

---

## Batch Structure

Typical folders:

```text
transcripts/
frames/
enhanced-transcripts/
reports/
infographics/
compilations/
MASTER-COMPILATION.md
```

There were fewer ledgers and fewer state transitions.

---

## Step 1 — Download Transcripts
For every video:
- download subtitles/transcript,
- clean into markdown/txt,
- continue even if some videos fail.

This was fast and gave immediate data.

---

## Step 2 — Extract Frames
Frames were extracted aggressively from videos, often producing hundreds per important video.

The old system did not overthink visual relevance before capture. It preferred having enough visual material and filtering later.

Historical examples:
- 70/90 frame extractions passed in one v4.5 run.
- One 2.5 hour video produced 652 frames.
- 12-video architecture batch produced 8,863 frames.

This explains Jon's concern: 72 frames across 9 videos is far below the older working norm.

---

## Step 3 — Enhanced Transcripts
Enhanced transcripts were built from:
- transcript content,
- frame context,
- video/topic understanding.

The system was expected to integrate the visual layer directly, not merely list frame filenames.

---

## Step 4 — Intelligence Reports
Reports distilled:
- key ideas,
- tools,
- frameworks,
- strategic insights,
- applicability to IDC.

---

## Step 5 — Infographics / Visual Outputs
Infographics were generated from the report + visual findings.

Older YPE cared about completed useful deliverables more than perfect gate accounting.

---

## Step 6 — Master Compilation
Create a master synthesis across all processed videos.

This was a clear endpoint and prevented the run from scattering into many half-finished files.

---

## Step 7 — Optional NotebookLM / Publication
NotebookLM was a downstream enhancement, not something that should invalidate the whole batch unless explicitly required.

When browser access was available, the practical move was to use the logged-in browser and do the notebook work directly.

---

## Why This Worked Better Operationally

- Fewer gates.
- Fewer human approval points.
- No default golden sample blockage.
- More aggressive frame extraction.
- Less re-planning between phases.
- Clear deliverable endpoint: master compilation + reports + visuals.

---

## Why It Needed Improvement

- Stub risk from sub-agents.
- Weak proof that visuals were truly analyzed.
- Less deterministic failure reporting.
- Easier to claim completion based on file counts.
- Less recoverable if a run crashed mid-process.

---

## What v6.6 Should Preserve From v4/v5

1. Bias toward completion.
2. Aggressive visual capture for important videos.
3. Simple linear path.
4. NotebookLM through browser when logged in.
5. Golden sample optional, not default.
6. One master final package.

---

## What v6.6 Should Add Without Slowing It Down

1. Lightweight ledgers.
2. Hard anti-stub checks.
3. Proof that frame vision analysis happened.
4. Browser fallback rules for NotebookLM.
5. Clear restart/resume state.
6. EVS as guardrails, not bureaucracy.

---

## Practical Hybrid Recommendation

Use v4/v5 as the execution spine and v6.6 as the validation harness.

The runner should feel like:

```text
transcripts → key moments → frames → vision → enhanced transcripts → reports → infographics → compile → NotebookLM/browser → final package
```

Not like:

```text
transcripts → gate → tier debate → gate → golden sample wait → gate → visual exception → gate → NotebookLM blocked → stale run
```

The latter is what created the AgentPie failure pattern.
