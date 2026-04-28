# YPE v6.6 Full Layout — Deterministic Visual Intelligence Pipeline

Purpose: a phase-by-phase, tier-by-tier operating layout for the current improved YPE concept after the AgentPie failure audit.

## North Star
YPE should convert a YouTube playlist into a verified visual knowledge library:

1. raw video/transcript inputs,
2. transcript-analyzed timestamp maps,
3. key-moment visual frame captures,
4. actual vision analysis of frames,
5. enhanced transcripts that merge what was said + what was shown,
6. intelligence reports,
7. infographics,
8. compilations,
9. NotebookLM audio/slides,
10. optional publication package.

If the output does not prove that visual frames were analyzed and incorporated, it is not a visual-enhanced YPE run.

---

## Default Human Burden

- Golden sample: **OFF by default**.
- Jon review: checkpoint summaries only unless quality fails.
- Jon assistance only required when:
  - explicit approval is needed for external posting,
  - account auth/2FA cannot be solved from existing logged-in browser,
  - the batch fails EVS after automatic repair attempts.

Golden sample should be an optional rescue/quality-lock mode, not a normal gate.

---

## Required Batch Structure

Every batch folder must contain:

```text
processing-plan.json
execution-ledger.md
evs-ledger.json
HANDOFF.md
transcripts/raw/
transcripts/clean/
timestamp-maps/
frames/
vision-analysis/
enhanced-transcripts/
reports/
infographics/
compilations/categories/
notebooklm/
logs/
metadata/
downloads/
tmp/
```

The batch is incomplete unless the plan, ledger, and EVS ledger agree.

---

## Phase 0 — Preflight + Quick Batch

### Step -1: Environment check
Verify:
- disk space,
- browser availability,
- YouTube download capability,
- ffmpeg available,
- vision model available,
- NotebookLM/browser policy known,
- sleep prevention if long-running.

### QB-1: Confirm video list
Create inventory of URLs, IDs, titles, durations, channels.

### QB-2: Quick transcript pull
Pull available subtitles/transcripts first. This is fast and gives the pipeline the material needed to choose visual moments.

### QB-3: Fast triage
Assign provisional relevance + tier using title, description, channel, transcript sample, and expected visual density.

### QB-4: Handoff/checkpoint
Record what will be processed. No need to wait for Jon unless requested.

---

## Phase A — Registry + Categorization

### Step 0: Registry check
Mark each video as:
- `new`,
- `already_processed`,
- `needs_refresh`,
- `skip_catalog_only`.

### Step 1: Enhanced metadata
Store `.info.json` metadata for every video.

### Step 2: Transcript download + cleaning
Create:
- `transcripts/raw/{id}.vtt`,
- `transcripts/clean/{id}-clean.txt`.

Clean duplicates from VTT line overlap. Repeated text fragments are an EVS failure.

### Step 3: Categorization + final tier
Assign category, tier, relevance, rationale.

---

## Tier Model

### Tier 1 — Full Visual Intelligence
Use for code demos, screen shares, tutorials, UI walkthroughs, diagram/slides, technical workflows, high strategic relevance.

Requirements:
- transcript-derived keypoint map,
- dense or burst frame capture around key moments,
- actual vision analysis,
- enhanced transcript sections: What Was Said, What Was Shown, Synthesized Knowledge,
- frame/timestamp citations.

Expected frame strategy:
- minimum: key moments × 3-frame burst unless content is static,
- normal: 50-150 frames,
- long tutorial/demo: up to 300 frames,
- do not accept a uniform 8-frame sample unless explicitly downgraded.

### Tier 2 — Smart Enhancement
Use for talking-head strategy/commentary where visuals may matter occasionally.

Requirements:
- transcript-derived map,
- conditional visual probe on high-importance moments,
- 5-20 frames if useful,
- if frames reveal demos/slides/data, upgrade relevant sections to Tier 1 treatment.

### Tier 3 — Catalog Only
Use for irrelevant, duplicate, no transcript, low value, or too long/noisy videos.

Requirements:
- metadata + reason for skip.
- no enhanced transcript/report unless promoted.

---

## Phase B — Machine Material Preparation

### Step 4: Transcript-derived timestamp map
This is where AgentPie failed.

The timestamp map must be derived from transcript analysis, not evenly spaced checkpoints.

Each map entry must include:
- timestamp,
- transcript excerpt,
- why it matters,
- visual capture reason,
- importance,
- expected visual type: talking head / code / UI / slide / chart / demo / unknown,
- burst count needed.

EVS fail if all checkpoints are evenly spaced or contain generic notes.

### Step 5: Frame capture
Capture frames after timestamp map selection.

Preferred order:
1. Use direct video download only when efficient.
2. Use segmented downloads around selected timestamps when full video is slow.
3. Use lower-res fallback when high-res stalls.
4. Use browser playback screenshots if yt-dlp fails and browser is logged in/available.
5. Mark visual blocked only after all practical local/browser attempts are logged.

Frame manifest must include:
- frame filename,
- timestamp,
- source method,
- linked timestamp-map entry,
- burst index,
- reason captured.

### Step 5.5: Vision analysis
Run actual image/vision analysis against selected frames.

Write:
- `vision-analysis/{id}.json`,
- optionally `vision-analysis/{id}.md`.

Each observation must tie to frame + timestamp.

EVS fail if the enhanced transcript merely lists frame filenames without visual observations.

---

## Optional Golden Sample

Default: `golden_sample_expected=false`.

Use a golden sample only when:
- Jon explicitly asks to set quality style,
- a new output type is being invented,
- EVS repeatedly passes shallow work,
- a batch is especially important and needs custom taste alignment.

Golden sample must not block ordinary batch execution.

---

## Phase B2 — Assembly Line

### Step 6: Enhanced transcript synthesis
Inputs:
- clean transcript,
- transcript-derived timestamp map,
- frame manifest,
- vision-analysis file,
- tier/rationale.

Required structure for Tier 1:
1. Metadata
2. Core thesis
3. What Was Said
4. What Was Shown
5. Visual evidence timeline
6. Synthesized Knowledge
7. Tools/workflows/tactics
8. Strategic IDC/OpenClaw relevance
9. Risks/hype gaps
10. Follow-up actions
11. Source integrity

EVS fail if:
- no real visual observations,
- no frame/timestamp citations,
- VTT duplicate text remains,
- output is mostly generic summary,
- raw transcript word count is wrong/missing,
- visual sections are not tied to frames.

### Step 7: Intelligence report
Derive from the validated enhanced transcript, not raw transcript alone.

Required:
- executive verdict,
- strategic value,
- tactical extractions,
- timestamp evidence,
- risks/limitations,
- recommended IDC actions.

### Step 8: Infographic
Generate only after Step 7 passes. Infographic prompt should use the validated report and meaningful visual frames.

---

## Phase C — Synthesis + NotebookLM

### Step 9: Category compilations
Group validated enhanced transcripts/reports by category.

### Step 10: Master compilation
Create root master synthesis and/or `compilations/master-compilation.md` consistently. EVS path expectations must match the spec.

### Step 11: NotebookLM
NotebookLM is not automatically blocked just because API access is unavailable.

Required policy:
1. Attempt browser automation with the OpenClaw-managed browser.
2. If logged-in Google is needed, attempt the user/browser profile when authorized/available.
3. If NotebookLM is already logged in, create/open notebook and upload sources.
4. Generate/trigger audio and slides if UI allows.
5. Record notebook URL/ID and status in `notebooklm/notebooklm-status.json` and `processing-plan.json`.
6. Mark blocked only if browser login/session truly unavailable or UI requires human-only action.

---

## Phase D — Content Assembly
Create content deliverables only from EVS-passed Phase C artifacts.

No external posting without Jon approval.

---

## Phase E — Cleanup
Clean temp video media only after manifests and artifacts are verified.

Never delete diagnostic evidence from failed runs without approval.

---

## Phase F — Visual Intelligence Publication
Optional publication expansion:
- slide screenshots,
- animation prompts,
- Grok Imagine/video generation,
- X article,
- video essay package,
- approval package.

---

## Final Completion Definition
A batch is complete only when:
- `processing-plan.json` says `batch_complete`,
- EVS ledger passes all required gates,
- final verdict exists,
- NotebookLM complete or explicitly accepted as skipped/blocked,
- handoff says no remaining work,
- no report claims completion earlier than evidence supports.
