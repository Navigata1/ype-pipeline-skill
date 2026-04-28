# YPE v7.2 — YouTube Pipeline Experience

> **Version:** 7.2 Concrete Visual Intelligence Pipeline
> **Purpose:** Convert YouTube playlists into verified visual knowledge assets: enhanced transcripts, intelligence reports, infographics, category/master compilations, NotebookLM audio/slides, and optional publication packages.
> **Design Principle:** v4/v5 execution speed + v6.6 evidence discipline. Direct flow, hard proof, no bureaucracy.
> **Default:** No golden sample. No false completion. Browser-first NotebookLM when required. Transcript-derived visual capture. Actual frame vision analysis. Curated drops default to Tier 1.

---

## 0. Non-Negotiable Truth Rules

1. **Counting files is not validation.** A file existing only proves a file exists.
2. **No visual-enhanced transcript without vision evidence.** Listing frame filenames is not enough.
3. **No uniform 8-frame Tier 1 shortcut.** Tier 1 videos need transcript-selected moments and burst/dense captures.
4. **Golden sample is optional and OFF by default.** Jon should not have to hand-build quality examples for ordinary batches.
5. **NotebookLM is browser-first.** If the browser/profile is logged in, use it before declaring Step 11 blocked.
6. **Never report complete unless EVS and the final verdict agree.**
7. **Failures are reported loudly and recorded.** No silent stalls, no vague blocked states.
8. **The runner follows the spine:** transcripts → key moments → frames → vision → enhanced transcripts → reports → infographics → compilations → NotebookLM when requested/required → final package.
9. **Batch intent controls tiering.** Hand-selected small batches are presumed important and default to Tier 1.
10. **Knowledge acquisition outranks neat categorization.** The goal is maximum useful data extraction, not artificial tier balance.

---

## 1. Batch Folder Contract

Every run gets its own folder:

```text
skills/youtube-pipeline/_active/{batch_id}/
```

Required structure:

```text
processing-plan.json
execution-ledger.md
evs-ledger.json
HANDOFF.md
final-verdict.md                         # created at the end only
metadata/
transcripts/raw/
transcripts/clean/
timestamp-maps/
downloads/
frames/
vision-analysis/
enhanced-transcripts/
reports/
infographics/
compilations/categories/
notebooklm/
content-drops/
logs/
tmp/
```

### `processing-plan.json` minimum schema

```json
{
  "batch_id": "ype-name-YYYY-MM-DD",
  "version": "7.2",
  "status": "preflight_pending",
  "batch_intent": "curated_drop|playlist_sweep|explicit_override",
  "golden_sample_expected": false,
  "golden_sample_provided": false,
  "notebooklm_browser_first": true,
  "notebooklm_required": false,
  "videos": [
    {
      "id": "VIDEO_ID",
      "url": "https://youtu.be/...",
      "title": "",
      "channel": "",
      "duration": 0,
      "status": "pending",
      "tier": null,
      "relevance": null,
      "knowledge_acquisition_priority": null,
      "category": null,
      "artifacts": {}
    }
  ]
}
```

### Allowed batch states

```text
preflight_pending
preflight_passed
inventory_complete
transcripts_complete
tiering_complete
timestamp_maps_complete
frames_complete
vision_analysis_complete
enhanced_transcripts_complete
intelligence_reports_complete
infographics_complete
category_compilations_complete
master_compilation_complete
notebooklm_complete
notebooklm_skipped_with_reason
notebooklm_blocked_after_browser_attempt
content_package_complete
cleanup_complete
batch_complete
failed_needs_attention
```

A batch may not skip states unless the skip is explicitly recorded with a reason and EVS accepts it.

---

## 2. Tier System

YPE v7 has three tiers. The tier controls how much visual work is required.

### Batch Intent Comes Before Tiering

The tier system must never punish a hand-selected batch.

There are two major intake modes:

#### Mode A — Curated Drop / Hand-Selected Batch

Use when Jon provides a small set of explicit URLs, usually **1-19 videos**.

Default assumption: **Jon selected these because they matter.**

Rules:
- All videos default to **Tier 1 / Full Visual Intelligence** unless there is a concrete disqualifier.
- Tier 2 is allowed only when the transcript and/or quick visual probe proves the video is mostly talking-head with minimal screen value.
- Tier 3 is allowed only for duplicate, unavailable, no transcript/no audio, broken, irrelevant-by-Jon-confirmed, or explicit skip.
- The runner must record `batch_intent: curated_drop` in `processing-plan.json`.
- The runner must not "balance" the batch into Tier 1/2/3 just because tiers exist.
- NotebookLM is optional for curated drops unless Jon requests it or the batch is intended to become a study/audio package.

#### Mode B — Playlist Sweep / Large Playlist Run

Use when Jon provides a playlist link, channel sweep, or **20+ videos**.

Default assumption: this is a broad collection that needs prioritization.

Rules:
- Apply Tier 1 / Tier 2 / Tier 3 normally.
- Tiering is based on relevance, transcript content, visual complexity, duplicates, duration, and strategic value.
- For huge playlists, tiering protects time and compute while still maximizing useful knowledge extraction.
- NotebookLM is normally required for playlist sweeps unless explicitly skipped, because the value is cross-video synthesis and study/audio reuse.

#### Mode C — Explicit Override

Jon can override either mode:
- `all tier 1`
- `quick sweep`
- `catalog only`
- `full treatment on these IDs`
- `skip these IDs`

The override must be written into `processing-plan.json` and `execution-ledger.md`.

### Knowledge Acquisition Priority

Every processable video gets a **Knowledge Acquisition Priority** score separate from visual complexity.

This prevents a video from being downgraded just because it is visually simple. Some talking-head videos contain extremely high-value frameworks, business models, architecture decisions, or strategic insight.

Score each video:

```json
{
  "knowledge_acquisition_priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "knowledge_priority_rationale": "Why this video matters to Jon/IDC even if visual complexity is low."
}
```

Rules:
- `CRITICAL` or `HIGH` knowledge priority can force Tier 1 full treatment even if visual complexity is medium/low.
- Visual complexity determines frame density, not whether the video deserves deep thinking.
- Tier decisions must consider both `visual_complexity` and `knowledge_acquisition_priority`.

### Minimum Visual Coverage Formula

Tier 1 visual coverage must use a duration-based minimum unless a downgrade/fallback is recorded.

Minimum Tier 1 frame targets:

| Video duration | Minimum frames | Normal target |
|---|---:|---:|
| 0-5 min | 15 | 25-40 |
| 5-15 min | 30 | 50-80 |
| 15-30 min | 50 | 80-150 |
| 30-60 min | 80 | 120-220 |
| 60-90 min | 120 | 180-300 |
| 90+ min | 150 | 250-400, or segment by chapters |

For static/talking-head Tier 1 videos, the runner may capture fewer frames only after a visual probe proves the screen is not adding information. The reason must be recorded as `visual_density_downgrade_reason`.

### Tier 1 — Full Visual Intelligence

Use for:
- coding demos,
- software tutorials,
- UI walkthroughs,
- screen shares,
- slides/diagrams/charts,
- high-relevance technical strategy videos,
- anything where the screen teaches what the words do not.

Required:
- transcript-derived timestamp map,
- key-moment frame capture with bursts,
- actual vision analysis,
- enhanced transcript with what was said + what was shown + synthesized knowledge,
- frame/timestamp citations.

Expected frame volume:
- short high-visual video: 25-60 frames,
- 10-30 min tutorial/demo: 50-150 frames,
- 30-90 min tutorial/demo: 100-300 frames,
- static talking-head with occasional screen inserts: capture around visual moments, downgrade specific sections if justified.

EVS fail examples:
- only 8 uniform frames from a long Tier 1 demo,
- no `vision-analysis/{id}.json`,
- enhanced transcript says “visual verification” but gives no visual observations.

### Tier 2 — Smart Enhancement

Use for:
- strategy/talking-head videos,
- podcasts with occasional screen material,
- medium relevance but not screen-heavy.

Required:
- transcript-derived timestamp map,
- visual probe around high-importance moments,
- 5-25 frames if useful,
- upgrade any section to Tier 1 treatment if frames reveal code/UI/slides/charts.

### Tier 3 — Catalog Only

Use for:
- duplicates,
- low relevance,
- no usable transcript and low priority,
- long noisy livestreams without clear value.

Required:
- metadata,
- skip reason,
- optional short summary if easy.

No enhanced transcript/report required unless promoted.

---

## 3. Phase 0 — Preflight + Quick Batch

### Step -1: Environment Check

Verify and log:
- disk space,
- `yt-dlp` available,
- `ffmpeg` available,
- browser automation available,
- vision/image model available,
- NotebookLM browser policy enabled,
- sleep prevention/caffeinate if long-running,
- output folders exist.

Write result to:

```text
logs/preflight.md
```

EVS fail if preflight is missing.

### QB-1: Video List Confirmation

Input can be playlist URL or explicit URLs.

Create inventory with:
- video ID,
- URL,
- title,
- channel,
- duration,
- upload date,
- view count if available.

Write:

```text
metadata/inventory.json
```

### QB-2: Fast Transcript Pull

Pull transcripts/subtitles before downloading full video.

Outputs:

```text
transcripts/raw/{id}.vtt
transcripts/clean/{id}-clean.txt
transcripts/index.json
```

Cleaning requirement:
- remove duplicated VTT overlap lines,
- remove timestamps from clean prose unless useful,
- preserve enough timestamp anchors for map generation.

EVS fail if repeated phrases dominate the clean transcript.

### QB-3: Fast Triage

Assign provisional:
- batch intent (`curated_drop`, `playlist_sweep`, or `explicit_override`),
- category,
- relevance,
- knowledge acquisition priority,
- tier,
- tier rationale,
- visual complexity estimate.

Batch-intent rule:
- If input is explicit URLs and count is under 20, default `batch_intent` to `curated_drop` and default processable videos to Tier 1.
- If input is a playlist/channel or count is 20+, default `batch_intent` to `playlist_sweep` and apply normal tiering.
- If Jon gives a direct override, obey it and record `batch_intent: explicit_override`.

Write into `processing-plan.json`.

No Jon approval required by default. Jon may override if present.

---

## 4. Phase A — Registry + Categorization

### Step 0: Registry Check

For every video mark:
- `process_new`,
- `already_processed`,
- `refresh_needed`,
- `catalog_only`.

Do not skip silently.

### Step 1: Metadata Finalization

Store full metadata:

```text
metadata/{id}.info.json
```

### Step 2: Transcript Finalization

Make sure every processable video has raw + clean transcript.

If no transcript exists:
- attempt auto-subtitle,
- attempt Whisper/transcription only if video is high value and available,
- otherwise Tier 3 catalog with reason.

### Step 3: Final Tier + Category Assignment

Write final tier decisions into `processing-plan.json`.

Required fields:

```json
{
  "batch_intent": "curated_drop",
  "tier": "Tier 1",
  "relevance": "HIGH",
  "knowledge_acquisition_priority": "HIGH",
  "knowledge_priority_rationale": "Hand-selected AgentPie/OpenClaw strategy video likely relevant to IDC agent architecture.",
  "category": "multi-agent-orchestration",
  "visual_complexity": "HIGH",
  "tier_rationale": "Screen-share tutorial with code/UI workflow."
}
```

For curated drops under 20 videos, any downgrade from Tier 1 must include:

```json
{
  "downgraded_from_default_tier1": true,
  "downgrade_reason": "Mostly static talking-head after transcript + visual probe; no meaningful screen information found."
}
```

EVS fail if a curated drop is silently distributed across Tier 1/2/3 without downgrade reasons.

---

## 5. Phase B — Machine Material Preparation

This is the most important correction in v7.

### Step 4: Transcript-Derived Timestamp Maps

Timestamp maps must come from transcript analysis, not uniform spacing.

For each video write:

```text
timestamp-maps/{id}-map.json
```

Required schema:

```json
{
  "video_id": "VIDEO_ID",
  "title": "",
  "duration": 0,
  "method": "transcript_derived_keypoints",
  "moments": [
    {
      "index": 1,
      "timestamp_seconds": 123,
      "timestamp": "00:02:03",
      "importance": "high",
      "transcript_excerpt": "The speaker introduces the agent harness architecture...",
      "why_it_matters": "Defines the core framework later used in demos.",
      "expected_visual_type": "diagram|code|ui|slide|talking_head|unknown",
      "capture_reason": "Need to see architecture diagram / code / UI state.",
      "burst_count": 5,
      "window_seconds": 8
    }
  ]
}
```

Rules:
- Tier 1 should usually have 10-40 key moments.
- Tier 2 should usually have 3-12 key moments/probes.
- Evenly spaced fallback must be marked `method: uniform_fallback` and justified.
- Generic notes like “auto-generated checkpoint” fail EVS.

### Step 5: Frame Capture

Capture frames from timestamp map moments.

Preferred strategies in order:

1. Direct video download if fast.
2. Segment download around selected timestamp windows.
3. Lower resolution download if high-res stalls.
4. Browser playback screenshot fallback if download fails.
5. Mark visual blocked only after practical local/browser attempts fail.

Frame output:

```text
frames/{id}/{id}_m{moment}_b{burst}_{timestamp}.jpg
frames/{id}/manifest.json
```

Manifest schema:

```json
{
  "video_id": "VIDEO_ID",
  "capture_method": "segment_download|full_download|browser_screenshot|fallback",
  "total_frames": 0,
  "frames": [
    {
      "frame": "VIDEO_ID_m01_b03_000203.jpg",
      "timestamp_seconds": 123,
      "timestamp": "00:02:03",
      "moment_index": 1,
      "burst_index": 3,
      "capture_reason": "Architecture diagram visible",
      "source_map": "timestamp-maps/VIDEO_ID-map.json",
      "size_bytes": 123456
    }
  ]
}
```

EVS checks:
- Tier 1 frame count matches tier expectations or has downgrade/fallback reason.
- Frames link to timestamp map moments.
- `.part` files are cleaned or logged as diagnostic failures.

### Step 5.1: Sampling Audit

Before vision analysis, audit whether the captured frames actually cover the video's key ideas.

Output:

```text
frames/{id}/sampling-audit.md
```

Required questions:
- Do captured frames cover every high-importance timestamp-map moment?
- Do captured frames include the expected visual types: code, UI, slides, diagrams, charts, demos, or talking head?
- Are there long gaps in the video where important transcript sections have no visual coverage?
- Are there too many redundant frames from the same static scene?
- Does the frame set satisfy the Tier 1 minimum visual coverage formula?
- If below target, is the video visually static enough to justify it?

Sampling audit verdicts:

```text
pass
needs_more_frames
visual_static_downgrade_accepted
failed_capture_retry_required
```

If verdict is `needs_more_frames` or `failed_capture_retry_required`, the runner must capture more frames or record a real blocker before Step 5.5.

### Step 5.5: Vision Analysis

Run image/vision analysis on captured frames.

Output:

```text
vision-analysis/{id}.json
vision-analysis/{id}.md
```

Required JSON schema:

```json
{
  "video_id": "VIDEO_ID",
  "analysis_method": "vision_model",
  "observations": [
    {
      "frame": "VIDEO_ID_m01_b03_000203.jpg",
      "timestamp": "00:02:03",
      "moment_index": 1,
      "visual_type": "code|ui|slide|diagram|chart|talking_head|other",
      "description": "A browser window shows the agent configuration screen...",
      "text_visible": "Any legible text/code/UI labels",
      "knowledge_added": "This reveals the actual implementation structure not clear from the transcript.",
      "confidence": "high|medium|low"
    }
  ]
}
```

EVS fail if:
- no vision file for Tier 1,
- observations are generic,
- no frame-specific descriptions,
- enhanced transcript later ignores these observations.

---

## 6. Optional Golden Sample Protocol

Default:

```json
{
  "golden_sample_expected": false,
  "golden_sample_mode": "off_by_default"
}
```

Golden sample only activates when:
- Jon explicitly requests it,
- a new deliverable type is being created,
- EVS repeatedly passes shallow work,
- a high-stakes batch needs taste alignment.

If activated, process one representative Tier 1 video fully, ask Jon for approval, then continue.

Golden sample must never be an unintentional blocker.

---

## 7. Phase B2 — Assembly Line Deep Processing

Process by step across all videos:

1. all Step 6 enhanced transcripts,
2. all Step 7 reports,
3. all Step 8 infographics.

This preserves quality and prevents context mixing.

### Step 6: Enhanced Transcript Synthesis

Inputs:
- clean transcript,
- timestamp map,
- frame manifest,
- vision-analysis file,
- metadata/tier/category.

Output:

```text
enhanced-transcripts/{id}-enhanced.md
```

Required Tier 1 structure:

```markdown
# Enhanced Transcript — {Title}

## Metadata
- Video ID:
- Channel:
- Duration:
- Tier:
- Visual method:
- Vision frames analyzed:

## Core Thesis

## What Was Said
Transcript-derived summary with timestamp anchors.

## What Was Shown
Concrete visual observations tied to frames/timestamps.

## Visual Evidence Timeline
- [00:02:03] Frame `...jpg`: what is visible and why it matters.

## Synthesized Knowledge
What the combined transcript + visuals reveal.

## Tools / Workflows / Tactics

## Strategic IDC / OpenClaw Relevance

## Risks / Hype Gaps / Unclear Claims

## Recommended Actions

## Source Integrity
- Raw transcript words:
- Enhanced transcript words:
- Frames captured:
- Frames analyzed:
- Vision confidence:
```

EVS fail if:
- Tier 1 has no `What Was Shown`,
- no frame/timestamp citations,
- visual section only lists filenames,
- VTT duplicates remain,
- `Source Integrity` has false/missing counts,
- output is stub/generic.

### Step 7: Intelligence Report

Input must be the validated enhanced transcript.

Output:

```text
reports/{id}-intelligence.md
```

Required structure:
- Executive Verdict
- What This Video Demonstrates
- Strategic Value for IDC/OpenClaw
- Tactical Extracts
- Evidence/Timestamp Anchors
- Visual Evidence That Changed Understanding
- Risks / Limitations / Hype Gaps
- Recommended IDC Actions
- Confidence

EVS fail if report ignores visual evidence for Tier 1.

### Step 8: Infographic

Generate after Step 7 passes.

Output:

```text
infographics/{id}-infographic.png
```

Prompt should include:
- core thesis,
- 3-5 most important findings,
- visual motifs from actual frame analysis,
- strategic category.

EVS checks:
- file exists,
- size > 50KB,
- not blank/corrupt.

---

## 8. Phase C — Synthesis + NotebookLM

### Step 9: Category Compilations

Group videos by category.

Output:

```text
compilations/categories/{category}.md
compilations/categories/index.json
```

Each category compilation includes:
- videos included,
- shared thesis,
- key agreements,
- contradictions,
- best visual evidence,
- IDC implications.

### Step 10: Master Compilation

Output both paths for compatibility:

```text
compilations/master-compilation.md
MASTER-COMPILATION.md
```

Required structure:
- Executive Summary
- Category Map
- Cross-Video Convergence
- Contradictions / Debates
- Visual Intelligence Findings
- IDC Strategic Recommendations
- Implementation Roadmap
- Source Index

### Step 11: NotebookLM Browser-First Integration

NotebookLM is browser-first when Step 11 is required, but it is not always required.

Default requirement:
- Curated drops under 20 videos: `notebooklm_required: false` unless Jon requests NotebookLM/audio/slides, or the batch is explicitly a study package.
- Playlist sweeps / 20+ videos: `notebooklm_required: true` unless Jon skips it.
- Explicit override: obey Jon's instruction.

If NotebookLM is not required, write `notebooklm/notebooklm-status.json` with `status: skipped`, `reason: small_curated_drop_not_requested`, and continue to final verdict. This skip must not block batch completion.

If NotebookLM is required, it is not blocked until browser attempts have been made.

Inputs:
- enhanced transcripts,
- intelligence reports,
- category compilations,
- master compilation.

Browser procedure:
1. Open `https://notebooklm.google.com/` in controlled browser.
2. Check whether logged in.
3. If not logged in, try user profile/browser when available.
4. Create a notebook named `{batch_id} — YPE Visual Intelligence`.
5. Upload validated sources.
6. Trigger/verify audio overview if available.
7. Trigger/verify slides/studio outputs if available.
8. Record notebook URL/ID.

Output:

```text
notebooklm/notebooklm-status.json
notebooklm/source-list.md
```

Status schema:

```json
{
  "status": "complete|blocked|skipped",
  "browser_attempted": true,
  "logged_in": true,
  "notebook_url": "",
  "notebook_id": "",
  "sources_uploaded": 0,
  "audio_status": "complete|pending|unavailable",
  "slides_status": "complete|pending|unavailable",
  "blocker": null
}
```

Only valid blocked reasons:
- browser unavailable,
- login unavailable,
- 2FA/human confirmation required,
- NotebookLM UI error,
- upload failed after retry,
- feature unavailable.

A vague “external account action required” is not valid unless browser evidence proves it.

---

## 9. Phase D — Content Package

Optional unless requested.

Create:

```text
content-drops/{batch_id}/youtube-script.md
content-drops/{batch_id}/shorts.md
content-drops/{batch_id}/x-article.md
content-drops/{batch_id}/linkedin-post.md
content-drops/{batch_id}/asset-list.md
```

No external posting without Jon approval.

---

## 10. Phase E — Cleanup

Cleanup rules:
- temp downloads may be deleted after frame manifests and vision outputs pass,
- retain referenced frames for MEDIUM/LOW confidence observations,
- failed runs are preserved as diagnostics unless Jon approves deletion,
- remove `.part` files only after logging them.

Output:

```text
logs/cleanup.md
```

---

## 11. Phase F — Visual Intelligence Publication

Optional advanced output:
- NotebookLM slide screenshots,
- animation prompts,
- Grok Imagine/video prompts,
- X article with visual embeds,
- video essay stitch package,
- final publication approval package.

No posting without approval.

---

## 12. EVS — Executable Validation System

EVS should be guardrails, not bureaucracy.

### Required gates

```text
EVS-0  preflight exists and passed
EVS-1  inventory complete
EVS-2  transcripts clean and non-duplicated
EVS-3  batch intent, tiers, and knowledge priority assigned with rationale
EVS-4  timestamp maps transcript-derived
EVS-5  frames match tier expectations and map moments
EVS-5.1 sampling audit confirms frame coverage or requires more frames
EVS-5.5 vision analysis exists and is concrete
EVS-6  enhanced transcripts validated
EVS-7  intelligence reports validated
EVS-8  infographics validated
EVS-9  category compilations validated
EVS-10 master compilation validated
EVS-11 NotebookLM complete/skipped/blocked with browser evidence
EVS-FINAL final verdict and handoff agree
```

### Enhanced transcript EVS checks

For Tier 1:
- word count >= meaningful threshold,
- required sections present,
- `What Was Shown` present,
- at least 5 frame/timestamp citations unless justified,
- frame count meets the minimum visual coverage formula unless `visual_static_downgrade_accepted`,
- sampling audit passed before vision analysis,
- visual observations are descriptive,
- no stub phrases,
- no repeated VTT artifacts,
- source integrity counts are accurate.

For Tier 2:
- required sections present,
- if frames captured, observations included,
- if no frames, reason recorded.

For Tier 3:
- skip reason present.

---

## 13. Failure Handling

When a step fails:

1. Record exact error in `execution-ledger.md`.
2. Update `processing-plan.json` status.
3. Write EVS failure to `evs-ledger.json`.
4. Retry with a targeted fix if safe.
5. If still failing, produce `HANDOFF.md` with exact resume instructions.
6. Alert Jon if the batch is expected to continue but cannot.

Never leave a batch in ambiguous state.

---

## 14. Codex / External Runner Instructions

If running this in Codex Desktop or another agent with computer/browser use:

1. Treat this spec as the source of truth.
2. Start by creating the batch folder and files.
3. Do not ask Jon for a golden sample unless explicitly requested.
4. Use browser for NotebookLM before blocking.
5. Preserve all evidence in the batch folder.
6. Do not claim completion without `final-verdict.md` and passing EVS.
7. Keep the execution spine simple and forward-moving.

Preferred run order:

```text
Preflight
Inventory
Transcripts
Tiers
Timestamp maps
Frame capture
Vision analysis
Enhanced transcripts
Reports
Infographics
Compilations
NotebookLM browser
Final verdict
Cleanup
```

---

## 15. Final Verdict Template

Create only at the end:

```markdown
# Final Verdict — {batch_id}

## Status
batch_complete | incomplete | blocked

## Videos Processed
- Total:
- Tier 1:
- Tier 2:
- Tier 3:

## Artifacts
- Enhanced transcripts:
- Reports:
- Infographics:
- Category compilations:
- Master compilation:
- NotebookLM:

## EVS Summary
- Passed gates:
- Failed gates:
- Warnings:

## Visual Intelligence Quality
- Frames captured:
- Frames analyzed:
- Tier 1 visual coverage:

## NotebookLM
- Browser attempted:
- Notebook URL:
- Audio:
- Slides:

## Remaining Work
None / list exact blockers.

## Recommendation
Use / rerun / partial only / discard.
```

---

## 16. What v7.2 Fixes From AgentPie

AgentPie failure pattern:
- uniform low frame capture,
- no real vision analysis,
- enhanced transcripts structurally upgraded but not visually grounded,
- NotebookLM declared blocked without browser-first attempt,
- golden sample confusion,
- EVS/ledger claimed more than actual scripts proved.

YPE v7 fixes:
- transcript-derived maps required,
- Step 5.5 vision required,
- visual evidence embedded in Step 6,
- golden sample off by default,
- browser-first NotebookLM,
- final completion requires evidence agreement.

YPE v7.2 additions:
- curated drops under 20 explicit URLs default to Tier 1 full treatment,
- tiering is not artificially balanced across small hand-picked batches,
- knowledge acquisition priority is separate from visual complexity,
- Tier 1 has a duration-based minimum visual coverage formula,
- Step 5.1 sampling audit checks whether frames actually cover the key ideas,
- NotebookLM is optional for small curated drops unless requested or required.

---

## 17. One-Screen Summary

YPE v7.2 is simple:

```text
Get the words.
Find the key moments.
Capture the screen at those moments.
Analyze what is visible.
Merge words + visuals into enhanced transcripts.
Extract intelligence.
Create visuals.
Compile the knowledge.
Use NotebookLM through browser.
Validate before claiming done.
```

That is the pipeline.
