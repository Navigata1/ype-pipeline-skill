# CHANGELOG — YPE Pipeline Skill

This changelog tracks the evolution of YPE (YouTube Pipeline Experience) from early recovery/title-matching work into the current v7.2 concrete visual intelligence pipeline.

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
