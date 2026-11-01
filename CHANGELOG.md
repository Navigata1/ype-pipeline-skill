# CHANGELOG — YPE Pipeline Skill

This changelog tracks the evolution of YPE (YouTube Pipeline Experience) from early recovery/title-matching work into the current v8 quick/full skill and evidence-checking runner.

## v8.3 — Coverage, depth, reuse and Sabbath observance

**Date:** 2026-10-31

A review of v2 through v8.1 found mechanisms that made YPE thorough and dependable which the v8 rewrite dropped without retiring them. v8.3 restores them as checks with a written escape for legitimate exceptions, never as padding targets or blocking golden samples. Runs created at v8.3 carry `depth_contract: depth/1`; older runs keep their contracts.

- **Reuse reviewed work.** `carry-over` reuses a verified review only when source, captions, cues, transcript and every inspected frame are byte-identical, and labels the reuse. `plan-update` compares a grown playlist with a prior run (restores the v4–v5 registry and incremental updates).
- **Proportionate visual coverage.** The v7.2 duration formula for sampled frames, a third of it for inspected frames, a computed gap audit, opening and closing scouts, and a recorded `sampling_audit` verdict. `sampling-audit` prints what verify will compute.
- **Recoverable small text.** `contact-sheets`, `enlarge`, and `capture --at` for targeted frames; `capture --height` downloads a short higher-resolution derived section without touching the retained source. Observations record legibility.
- **Thin work detection.** Claims and observations must reach every quarter of the source; full source-map sections under 35% of their source words or over `max(10 min, duration/4)` need a reason; three early/middle/late spot checks; template placeholders fail.
- **Deeper synthesis.** Required intelligence-report sections (claims and evidence; tools and technologies; code, prompts and configurations; visual evidence that changed the understanding; unverified or overstated claims), category compilations with agreements, contradictions and gaps for categories holding two or more videos, and a Gaps section in the master compilation.
- **Input fidelity.** Caption provenance (manual, automatic, unknown), acknowledged caption gaps, and owner-flagged `priority` sections that need inspected frames and a cited claim.
- **Portability and provenance.** The NotebookLM account comes from `settings.json`, not code; each analysis and full receipt records the producing model; the v8.1 entry is dated.
- **Sabbath observance** (from v4–v6.1). No pipeline work from Friday sunset (stopping 15 minutes before) to Saturday sunset, computed offline for the configured location. A command in the window checkpoints the run as `paused_sabbath` and exits 75 without ending it; downloads stop at the window start without counting as failures; `run` acquires until done and resumes on its own after sunset.
- 173 tests (45 new), passing under the workspace venv and system Python. An independent review cleared the Sabbath window arithmetic and gate; its nine bug findings are fixed, each with a regression test that fails on the pre-fix code.

Deliberately not restored: fuzzy title matching, the blocking golden sample, raw-media deletion and project-impact scoring.

## v8.1 — Source-first depth

**Date:** 2026-10-30

- Restore full section-by-section source substance and integrated visual discoveries; project applications are a separate downstream report.
- Activate source maps and semantic acceptance by default for new full runs; historical receipt contracts stay readable.
- Bind infographic concept plans and source revisions to explicit coverage, relationship, label, legibility and specificity review.
- Package exactly one enriched NotebookLM source per unique video, with capacity blockers instead of automatic blending/splitting.
- Retain the optional audience channel and claim matrix as distinct analytical layers.
- Add synthetic behavioral tests for the new contracts, including 37 videos producing 37 sources.

## v8.0 — Quick/full skill with an evidence-checking runner

**Date:** 2026-10-29

- Replaced the single long instruction file with a small skill (`skills/ype-pipeline/`) plus a Python runner (`ype.py`: init, acquire, import-cache, sample, verify, render, package, register-notebook).
- Added **quick** and **full** modes; quick still requires the complete transcript and inspected frames.
- Runs are durable: bounded sequential acquisition, atomic checkpoints, single-writer locks, rate-limit backoff with a recorded retry time, and no delete operation.
- `verify` binds review receipts to retained source, caption, transcript, frame and analysis bytes, and fails on any later change.
- Captions use the conservative `caption-time-v1` cleanup with an audit of every decision.
- Added the opt-in audience channel: `--community`, `--second-labeller` and `--synthesis`.
- Added a unittest suite: 104 synthetic tests plus a check that a workspace's README-linked example still verifies.
- Moved the v7.2 skill to `archive/v7.2/`; it is also kept as `references/full-v7.2-source.md` for full mode.

## v7.2 — Curated Drop Logic + Maximum Knowledge Acquisition

**Date:** 2026-04-28

- Promoted live pipeline to **YPE v7.2**.
- Added **Batch Intent Comes Before Tiering**:
  - explicit URL drops under 20 videos default to `curated_drop`,
  - curated drops default all processable videos to Tier 1,
  - any downgrade requires a written reason,
  - large playlist links / 20+ videos use normal Tier 1/2/3 prioritization.
- Added **Knowledge Acquisition Priority** separate from visual complexity.
- Added **Minimum Visual Coverage Formula** by duration.
- Added **Step 5.1 Sampling Audit** before vision analysis.
- Made NotebookLM optional for small curated drops unless Jon requests it or the batch is meant to become a study/audio package.
- Updated EVS to validate batch intent, knowledge priority, sampling audit, and visual coverage.

## v7.0 — Concrete Visual Intelligence Pipeline

**Date:** 2026-04-28

- Rebuilt the live YPE skill after the AgentPie failure audit.
- Restored the v4/v5 direct execution spine:
  `transcripts → key moments → frames → vision → enhanced transcripts → reports → infographics → compilations → NotebookLM → final package`.
- Kept v6.x evidence discipline without allowing validation bureaucracy to stall obvious progress.
- Made golden sample **OFF by default**.
- Added **NotebookLM Browser-First Rule**: try logged-in browser/user profile before declaring Step 11 blocked.
- Required transcript-derived timestamp maps instead of uniform frame grids.
- Required Step 5.5 vision analysis before Step 6 enhanced transcripts.
- Defined final completion as EVS + final verdict agreement, not file counts.

## v6.6 — Deterministic Enforcement Draft

**Date:** 2026-04-27 / 2026-04-28

- Created as a proposed enforcement overlay after the AgentPie run stalled and produced weak visual-enhanced outputs.
- Added a state-machine mindset:
  - `processing-plan.json`,
  - `execution-ledger.md`,
  - `evs-ledger.json`,
  - handoff files.
- Clarified that the original v6.5 skill was rich in instructions but not strict enough about legal next actions.
- Added recovery logic around visual timeouts, golden sample confusion, and false completion.
- Superseded by v7.0/v7.2, which simplified and hardened the core ideas.

## v6.5.8 — Canonical Playlist Intelligence + Coverage Resolution

**Date:** 2026-04-21

- Added canonical playlist intelligence layer.
- Split registry into playlist registry, batch history, and topic index concepts.
- Focused on distinguishing:
  - processed directly,
  - covered by registry,
  - truly unprocessed.
- Intended to prevent raw playlist counts from being reported as actionable backlog without reconciliation.
- Preserved v6.5 architecture but added more registry intelligence.

## v6.5.2 — EVS Hardening + NotebookLM Truth Mandate

**Dates:** 2026-03-30 and 2026-04-02

- Hardened EVS after prior false-completion/Step 11 issues.
- Made Phase-C EVS gate blocking after NotebookLM deliverables.
- Added/locked Phase F Visual Intelligence Publication:
  - NotebookLM slide deck,
  - Grok Imagine animated clips,
  - X articles,
  - visual essay packages.
- Proven on the Apr 1 45-video batch, which produced enhanced transcripts, reports, infographics, category compilations, master compilation, NotebookLM audio, and slides.

## v6.5 — Sustainable Quality Architecture

**Date:** 2026-03-16

- Introduced the three-part architecture:
  1. Executable Validation System (EVS),
  2. Tiered Autonomy,
  3. Golden Sample Protocol.
- Tried to reduce Jon’s manual involvement while preserving quality.
- Added tiering so not every video received the same amount of visual work.
- Added model-routing and quality-gate concepts to reduce stub outputs.
- Later issues: golden sample became too easy to misapply as a blocker, and tiering could mis-handle hand-selected batches.

## v6.2 — Audit-Driven Improvement Plan

**Date:** 2026-03-16

- Created after the v6.1 batch produced uneven quality.
- Identified that some outputs were technically present but intellectually weak or stub-like.
- Added improvement points around:
  - sub-agent delegation limits,
  - stub detection,
  - write-to-disk discipline,
  - processing plan persistence,
  - priority-section handling,
  - evidence-based validation.
- Served as a bridge from v6.1 into the more hardened v6.5 architecture.

## v6.1 — Nano Banana 2 + Audit Baseline

**Date:** 2026-03-02 / 2026-03-15

- Added Nano Banana 2 / Gemini image-generation path for infographics.
- Replaced the older HTML-to-PNG infographic path with direct PNG generation.
- Improved visual output quality and removed some Chrome/Puppeteer dependency.
- The later v6.1 audit found that files could exist while enhanced transcripts/reports remained shallow.

## v6.0 — Consolidated Execution Skill

**Date:** 2026-03-02

- Consolidated methodology and trigger docs into one execution skill.
- Added mandatory opening/closing scouts.
- Added scout frames for non-vision sections.
- Added every-video-gets-frames rule.
- Added stricter density-based extraction and violation protocol.
- Attempted to eliminate agent judgment on whether frames were needed.

## v5.8 — Quick-Batch Trigger + Judge Gates

**Date:** 2026-02-24

- Added Quick-Batch pre-phase.
- Added global trigger language for invoking YPE across channels.
- Added violation protocol.
- Added Judge-agent checkpoints at key gates.
- Preserved v5.0 as the underlying full pipeline.

## v5.0 — Definitive Knowledge Ingestion System

**Date:** 2026-02-20 / 2026-02-21

- Consolidated scattered v1-v4.5 knowledge into one authoritative spec.
- Added/standardized:
  - Step 0 registry check,
  - cross-playlist deduplication,
  - title-based matching,
  - NotebookLM integration,
  - content distribution/deliverables,
  - large transcript chunking fixes,
  - external drive/symlink considerations,
  - technical reference sections.
- Used XML-hybrid structure in the methodology version.

## v4.5 — Incremental Processing + Dedup Improvements

**Date:** 2026-02-13 / 2026-02-20 references

- Improved incremental playlist processing.
- Elevated cross-playlist dedup into a proper first step.
- Added category version archival and cron/update concepts.
- Historical Claw playlist run showed strong throughput:
  - 90 transcripts downloaded,
  - 70/90 frame extractions passed at one checkpoint,
  - long videos could produce hundreds of frames.

## v4.0 — Locked Registry + Sabbath Compliance

**Date:** 2026-02-12

- Locked in global video registry concepts.
- Added incremental update behavior.
- Formalized Sabbath compliance.
- Added cleanup as a formal late step.
- Strengthened category-first and registry-first design.

## v3.1 — Category-First Architecture

**Date:** 2026-02-10 / 2026-02-11

- Refined the v3 category-first redesign.
- Improved category organization and output mapping.
- Helped move YPE from isolated video processing toward playlist knowledge architecture.

## v3.0 — Pipeline Redesign

**Date:** 2026-02-10 / 2026-02-11

- Introduced a fuller category-first architecture.
- Treated enhanced transcripts as a source of truth for downstream reports and compilations.
- Began moving away from simple transcript extraction toward knowledge synthesis.

## v2.0 — Recovery + Title-Based Matching

**Date:** 2026-02-10 / historical recovery docs

- Introduced recovery logic and title-based matching after earlier file/identity mismatch issues.
- Focused on reconstructing what belonged to which video.
- Laid groundwork for later registry and dedup systems.

## Notes

Earlier v1.x iterations existed as proof-of-concept scripts and manual workflows. v2.0 is the first version tracked here because Jon specifically requested version history from v2.0 forward.
