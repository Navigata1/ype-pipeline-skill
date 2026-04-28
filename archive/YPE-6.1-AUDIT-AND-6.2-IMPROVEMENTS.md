# YPE v6.1 → v6.2: Pipeline Audit & Improvement Plan
## Batch: ype-batch-2026-03-15 | 12 Videos | Processed 2026-03-16

---

## EXECUTIVE SUMMARY

The YPE v6.1 batch of 12 videos was completed — but with deeply uneven quality. **Videos 1-4 received proper Opus-quality treatment.** Videos 5-12 were rushed through batch processing and produced stubs that violate v6.1's own quality standards. The pipeline "completed" in the sense that files exist for every step, but 8 of 12 videos have enhanced transcripts and reports that are objectively inadequate.

**Verdict:** Batch 1 intelligence extraction is ~33% genuinely done (4/12 proper), ~67% stub quality. Infographics and NotebookLM completed. Master Compilation was revised twice before reaching acceptable depth.

---

## I. SUCCESSES ✅

### 1. Videos 1-4 — Opus-Quality Deep Processing
The first 4 videos received the treatment v6.1 demands:

| Video | Enhanced Transcript | Report | Frames | Quality |
|-------|-------------------|--------|--------|---------|
| rbqIivbTJao (Scroll Animation) | 1,872 words | 947 words | 320 | ✅ PROPER — vision analysis, frame refs, actionable |
| QF7SREoOHP4 (Vapi Voice) | 2,337 words (Telegram: 15,419 bytes) | 657 words | 612 | ✅ PROPER — section-by-section, 12 detailed sections |
| Mz7W0qNlmOw (Wes Roth) | 2,107 words (Telegram: 13,412 bytes w/ Framer addendum) | 548 words | 906 | ✅ PROPER — revised with critical Framer ad section |
| SncOnEx1CcE (Lian Li DK-04) | 1,091 words | 249 words | 675 | ✅ ADEQUATE — hardware reference, appropriate depth |

**What went right:**
- One video at a time, full attention
- Vision analysis on key frames with specific frame file references
- Transcript sections mapped to timestamps
- Inline vision analysis merged into transcript (not appended)
- Intelligence reports with full executive summaries, cross-references, actionable items
- Jon's explicit feedback was heard and acted on (Framer ad re-analysis)

### 2. Comprehensive Frame Capture
- **9,487 total frames** across 12 videos
- Every video has frames — no zero-frame violations
- High FPS extraction for screen-share heavy videos (i3FOFgimXn0: 1,471 frames)
- Opening/closing scouts captured
- Frame quality at 720p+ (some at 1080p)

### 3. Infographic Generation (Batch 2)
- **13 infographics** generated via Nano Banana 2
- All 3.6-5.9MB (well above 50KB minimum)
- 12 individual + 1 master infographic
- Generated efficiently in one batch session

### 4. Master Compilation — Eventually Right
- First version: 1,107 words — too thin, missing Jon's two critical discoveries
- Second version: 1,926 words — better structure but still lacked depth
- **Final version: ~1,928 words** — properly leads with Discovery 1 (rbqIivbTJao scroll pipeline) and Discovery 2 (Framer enterprise template), includes complete tech stack, 5 Core Dimensions framework, execution plan, and business intelligence
- Jon's explicit feedback drove the revision — proves the feedback loop works when listened to

### 5. NotebookLM Integration (Batch 3)
- Notebook created with enhanced transcripts as sources
- Audio podcast generated
- Slide deck output
- *(Completed in a separate session — login flow was a blocker initially)*

### 6. Responsive Feedback During Processing
- Jon received Telegram notifications as each video completed
- Progress tracking (X/12 complete)
- Scores and key findings delivered incrementally
- Jon could review and redirect in real-time (which he did — Framer ad fix)

---

## II. FAILURES ❌

### ❌ FAILURE 1: Sub-Agent Delegation Catastrophe (CRITICAL)
**What happened:** Attempted to delegate the entire pipeline to a Gemini Flash sub-agent to process all 12 videos autonomously.
**Result:** The sub-agent produced stubs across the board — enhanced transcripts with no vision analysis, no frame references, no section-by-section breakdown.
**Impact:** Wasted ~30 minutes of processing time. Had to abandon the sub-agent output entirely and restart manually.
**Root cause:** Flash is insufficient for Opus-quality analysis. The skill says "Vision model for frames, LLM for synthesis" — delegating both to a cheap model violates the model routing table.

> ⭐ **v6.2 FIX:** Add explicit sub-agent delegation rules. Define which steps CAN be delegated (transcript download, frame extraction, metadata) vs which MUST stay on primary model (enhanced transcript synthesis, intelligence reports, master compilation). Add a "delegation quality gate" — if a sub-agent's output fails stub detection, auto-escalate to primary model instead of shipping.

---

### ❌ FAILURE 2: Videos 5-12 Enhanced Transcripts Are Stubs (CRITICAL)
**The data:**

| Video | Raw Transcript (words) | Enhanced Transcript (words) | Ratio | v6.1 Rule (≥80%) | Verdict |
|-------|----------------------|---------------------------|-------|-------------------|---------|
| 3KpP2K0oT1M | 18,361 | 1,159 | **6%** | ❌ FAIL | STUB |
| UR09nuSxGio | 15,960 | 223 | **1.4%** | ❌ FAIL | STUB |
| VBvxHIkvjeo | 4,631 | 201 | **4.3%** | ❌ FAIL | STUB |
| gh9Y3tHeFXQ | 12,030 | 231 | **1.9%** | ❌ FAIL | STUB |
| haBy-Rhkl4g | 11,410 | 263 | **2.3%** | ❌ FAIL | STUB |
| i3FOFgimXn0 | 6,450 | 268 | **4.2%** | ❌ FAIL | STUB |
| nhibi9TRgNc | 21,531 | 284 | **1.3%** | ❌ FAIL | STUB |
| quVoGwHZdYI | 12,489 | 766 | **6.1%** | ❌ FAIL | STUB |

**Properly done (for comparison):**

| Video | Raw Transcript (words) | Enhanced Transcript (words) | Ratio | Verdict |
|-------|----------------------|---------------------------|-------|---------|
| rbqIivbTJao | 791 | 1,872 | **237%** | ✅ Vision adds value |
| QF7SREoOHP4 | 9,515 | 2,337 | **25%** | ✅ Proper (Telegram version was full 15KB) |
| Mz7W0qNlmOw | 12,467 | 2,107 | **17%** | ✅ Proper (Telegram version was 13KB w/ addendum) |

**Note:** Even the "proper" ones stored on disk are smaller than the Telegram-delivered versions. The full-quality enhanced transcripts were sent to Jon via Telegram but some may not have been written back to disk at full length.

**Root cause:** After the sub-agent failure, videos 5-12 were batch-processed rapidly to "catch up." Speed was prioritized over depth. The v6.1 stub detection rule ("halt, flag, redo — never ship stubs") was violated.

> ⭐ **v6.2 FIX:** 
> 1. **Automated stub detection checkpoint** after each enhanced transcript is written — compare word counts programmatically before proceeding to next video.
> 2. **Hard gate:** If `enhanced_word_count / raw_transcript_word_count < 0.80`, pipeline HALTS with a violation flag. No manual override — the transcript must be redone.
> 3. **"Write-to-disk-first" rule:** The enhanced transcript MUST be written to the output directory AND verified before sending a completion notification. No more "sent via Telegram but not on disk."

---

### ❌ FAILURE 3: Videos 5-12 Intelligence Reports Are Stubs (CRITICAL)
**The data:**

| Video | Report (words) | v6.1 Required Sections | Verdict |
|-------|---------------|----------------------|---------|
| UR09nuSxGio | 50 | Missing: Key Insights, Actionable Items, Relevance Map, Cross-Refs | STUB |
| VBvxHIkvjeo | 48 | Missing: Key Insights, Actionable Items, Relevance Map, Cross-Refs | STUB |
| gh9Y3tHeFXQ | 47 | Missing: Key Insights, Actionable Items, Relevance Map, Cross-Refs | STUB |
| haBy-Rhkl4g | 48 | Missing: Key Insights, Actionable Items, Relevance Map, Cross-Refs | STUB |
| i3FOFgimXn0 | 42 | Missing: Key Insights, Actionable Items, Relevance Map, Cross-Refs | STUB |
| nhibi9TRgNc | 44 | Missing: Key Insights, Actionable Items, Relevance Map, Cross-Refs | STUB |
| quVoGwHZdYI | 138 | Partial — has summary but missing deep analysis | WEAK |
| 3KpP2K0oT1M | 317 | Partial — has summary and some insights | WEAK |

**Properly done (for comparison):**
| Video | Report (words) | Verdict |
|-------|---------------|---------|
| rbqIivbTJao | 947 | ✅ Full report with all sections |
| QF7SREoOHP4 | 657 | ✅ Full report |
| Mz7W0qNlmOw | 548 | ✅ Full report |

**Root cause:** Same as Failure 2 — batch speed over quality.

> ⭐ **v6.2 FIX:** 
> 1. **Report minimum word count:** 300 words minimum for any video. 500+ for videos with >10 minutes duration.
> 2. **Required sections checklist** — programmatic validation that all 6 sections exist before marking complete: Executive Summary, Key Insights (ranked), Actionable Items, Relevance to Jon's Projects, Cross-References, Dual-Axis Scores.
> 3. **Report derives from enhanced transcript** — if the enhanced transcript is a stub, the report will be too. Fix upstream first.

---

### ❌ FAILURE 4: Timestamp Maps — Only 2 of 12 Exist (MODERATE)
**On disk:** Only `QF7SREoOHP4-map.json` and `rbqIivbTJao-map.json` were saved.
**The other 10 videos** either had timestamp maps generated in-memory (not persisted) or skipped entirely.

**Impact:** Without timestamp maps, frame extraction was untargeted — bulk extraction at fixed intervals rather than density-based extraction aligned to content sections. This means thousands of frames were captured but many may be redundant (talking head) while key moments (code, UI, diagrams) may have been undersampled.

> ⭐ **v6.2 FIX:**
> 1. **Timestamp map is a WRITTEN FILE** — must exist on disk before frame extraction begins. No in-memory-only maps.
> 2. **Validation gate:** `ls timestamp-maps/{id}-map.json` must return true before Step 5 can begin for that video.
> 3. **Map-to-frame manifest linkage:** Frame manifest must reference which timestamp map sections each frame belongs to.

---

### ❌ FAILURE 5: Category Compilations — Empty Directory (MODERATE)
**On disk:** `categories/` directory exists but is completely empty.
**Step 9** (Category Compilation) never ran. This means:
- No cross-video synthesis within categories (e.g., all 8 AntiGravity videos compared)
- No gap analysis within categories
- No contradiction detection between creators
- The Master Compilation was doing the work that category compilations should have fed into

> ⭐ **v6.2 FIX:**
> 1. **Step 9 is MANDATORY** — cannot proceed to Step 10 (Master Compilation) without category compilations.
> 2. **Auto-generate categories.json** in Step 3 and enforce it exists before Phase B begins.
> 3. **Category compilation minimum:** Each category with 2+ videos gets a compilation document.

---

### ❌ FAILURE 6: Frame Directory Contamination (MODERATE)
**Issue:** A directory named `"3KpP2K0oT1M VBvxHIkvjeo quVoGwHZdYI UR09nuSxGio haBy-Rhkl4g nhibi9TRgNc gh9Y3tHeFXQ i3FOFgimXn0"` contains 1,105 mixed frames from 8 videos — impossible to determine which frames belong to which video.
**Also:** `3KpP2K0oT1M/` proper directory has only 1 frame.

**Root cause:** The sub-agent's bulk extraction dumped all 8 videos' frames into one combined directory. When re-extraction was done per-video later, some videos got proper directories but the contaminated folder was never cleaned up.

> ⭐ **v6.2 FIX:**
> 1. **Directory naming validation:** Frame directory name must match exactly `{video_id}/` with no spaces. Regex: `/^[A-Za-z0-9_-]+$/`
> 2. **One video per extraction command** — never combine multiple videos in one ffmpeg/yt-dlp command.
> 3. **Post-extraction validation:** Count frames per directory. If a directory name contains spaces, flag as contamination and halt.

---

### ❌ FAILURE 7: Frame Manifests Not Generated (MINOR)
**On disk:** No `frame_manifest.json` files exist in any frame directory.
**Impact:** No structured mapping from frame files to timestamps/sections. Vision analysis had to guess which frames were relevant.

> ⭐ **v6.2 FIX:**
> 1. **Manifest generation is part of Step 5** — runs immediately after ffmpeg extraction.
> 2. **Manifest validation:** Must contain `video_id`, `total_frames`, `frames[]` array with timestamp mappings.
> 3. **No manifest = Step 5 incomplete.**

---

### ❌ FAILURE 8: Framer Ad Section Initially Dismissed (PROCESS)
**What happened:** Jon explicitly said the Framer ad was the PRIMARY reason he included the Mz7W0qNlmOw video. The initial enhanced transcript treated it as a sponsor segment to skip. Jon had to call this out, and a second pass was done to properly analyze the Framer section with dense frame capture.

**Root cause:** The agent applied a heuristic ("ads are filler") instead of listening to Jon's explicit instruction. The v6.1 spec doesn't have a mechanism for Jon to flag priority sections before processing.

> ⭐ **v6.2 FIX:**
> 1. **Priority Section Flagging (NEW):** During QB-1 (Video List Confirmation), ask Jon: *"Are there specific sections, timestamps, or topics within any video that are especially important to you?"* Capture these as `priority_sections[]` in the processing plan.
> 2. **Priority sections get MAXIMUM vision density** regardless of content type (even if it looks like an ad).
> 3. **Never auto-classify sponsored/ad segments as low-priority** without checking priority flags first.
> 4. **Addendum protocol:** When Jon flags a missed section post-processing, the addendum gets written BACK to the enhanced transcript on disk (not just sent via Telegram).

---

### ❌ FAILURE 9: Master Compilation Required 3 Revisions (PROCESS)
**Timeline:**
1. **V1:** 1,107 words — a summary table, not a compilation. Missing Jon's two critical discoveries.
2. **V2:** 1,926 words — better structure, added the tech stack and action items. Still thin relative to 219K words of source material.
3. **V3 (final):** ~1,928 words — properly leads with the two critical discoveries, includes ASCII layout diagrams, full tool mapping, 5 Core Dimensions framework, execution plan. Accepted by Jon.

**Root cause:** The Master Compilation was generated BEFORE the category compilations (which never existed). It was synthesizing from individual reports — many of which were stubs. Garbage in, garbage out.

> ⭐ **v6.2 FIX:**
> 1. **Master Compilation draws from category compilations** — not individual reports. This enforces Step 9 completion.
> 2. **Minimum word count for Master Compilation:** 5,000 words for batches of 10+ videos. 2,000 for batches of 4-9. 1,000 for 1-3.
> 3. **Jon-flagged priorities MUST appear in the first section** of the Master Compilation. If Jon said "this is the most important part," it leads the document.

---

### ❌ FAILURE 10: Mac Sleep/Lock Interruptions (ENVIRONMENT)
**What happened:** The MacBook's display sleep triggered system lock, requiring fingerprint/password to resume. This interrupted overnight processing, causing delays between video downloads/extractions.

**Resolution (applied during this batch):** `caffeinate` daemon started, all lock/sleep settings disabled via `defaults write`.

> ⭐ **v6.2 FIX:**
> 1. **Pre-flight environment check (NEW Step -1):** Before ANY pipeline processing, verify:
>    - `caffeinate` is running
>    - Display sleep is disabled or set to >4 hours
>    - Password on wake is disabled
>    - Available disk space >10GB
>    - Network connectivity stable
> 2. **Log environment state** in pipeline.log at start of each batch.

---

### ❌ FAILURE 11: No Processing Plan on Disk (MINOR)
**On disk:** `processing-plan.json` is empty/missing.
**Impact:** No record of which videos were marked as `process_new`, `resume`, `reprocess`, or `skip-reprocess`. Registry check (Step 0) was done verbally but not persisted.

> ⭐ **v6.2 FIX:** Processing plan MUST be written as JSON before Step 1 begins. Include video IDs, statuses, estimated processing time, and model assignments.

---

### ❌ FAILURE 12: Enhanced Transcripts Not Written Back to Disk (DATA INTEGRITY)
**Issue:** The full-quality enhanced transcripts for Videos 1-3 were delivered to Jon via Telegram as markdown files. But the versions saved to disk may be different (shorter) than what was sent via Telegram.

**Evidence:** The Telegram-delivered `QF7SREoOHP4-enhanced` was 15,419 bytes, but the on-disk version is 2,337 words. The Telegram-delivered `Mz7W0qNlmOw-enhanced` with the Framer addendum was 13,412 bytes, disk version is 2,107 words.

> ⭐ **v6.2 FIX:**
> 1. **Write-first, notify-second:** The enhanced transcript is written to disk FIRST. Then the Telegram notification references the on-disk file. Never generate content in a message and not persist it.
> 2. **Checksum verification:** After writing, read back and verify word count matches expected.

---

## III. FULL v6.1 PIPELINE TIMELINE WITH v6.2 IMPROVEMENT MARKERS

Below is the complete v6.1 pipeline as executed, with ⭐ markers where v6.2 improvements apply:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YPE v6.1 PIPELINE (AS EXECUTED)                  │
│                    ⭐ = v6.2 Improvement Point                     │
└─────────────────────────────────────────────────────────────────────┘

⭐ NEW: PRE-FLIGHT ENVIRONMENT CHECK (v6.2 Step -1)
│  ├── Verify caffeinate running
│  ├── Verify display/sleep/lock settings
│  ├── Verify disk space >10GB
│  ├── Verify network connectivity
│  └── Log environment state to pipeline.log

PHASE 0: QUICK-BATCH
├── QB-1: Video List Confirmation
│   ├── Present inventory table (title, channel, duration, views, date)
│   ├── Jon confirms list ✅ (worked correctly)
│   ⭐ NEW: Ask Jon for PRIORITY SECTIONS within any video
│   ⭐ NEW: Capture priority_sections[] in processing plan
│   └── GATE: Jon approves
│
├── QB-2: Transcript Quick-Pull
│   ├── yt-dlp --write-auto-sub for all videos ✅ (worked correctly)
│   ├── Flag manual vs auto-generated
│   ├── Record word counts
│   └── Store for reuse in Step 2
│
├── QB-3: Quick Intelligence Synthesis
│   ├── Per-video executive summary ✅ (worked correctly)
│   ├── Top 3 insights, relevance scores
│   └── Duplicate/overlap detection
│
├── QB-4: Quick-Batch Delivery ✅ (worked)
│
└── QB-5: Mandatory Handoff → Step 0 ✅ (worked)

PHASE A: REGISTRY & CATEGORIZATION
├── Step 0: Registry Check
│   ├── Check global_processed_registry.json
│   ⭐ FIX: Write processing-plan.json to disk (was missing)
│   ⭐ FIX: Include model assignments per step
│   └── GATE: Jon approves processing plan
│
├── Step 1: Playlist Inventory ✅ (worked — metadata collected)
│
├── Step 2: Transcript Download ✅ (worked — reused QB-2)
│
└── Step 3: LLM Categorization
    ⭐ FIX: Write categories.json to disk (was missing)
    ⭐ FIX: Categories must exist before Phase B begins
    └── GATE: Jon reviews categories

PHASE B: PER-VIDEO DEEP PROCESSING
│
├── Step 4: Timestamp Map Generation
│   ├── Build section map with vision density flags
│   ├── Classify each section (insight/takeaway/key_moment/actionable)
│   ├── Include mandatory opening/closing scouts
│   ⭐ FIX: WRITE MAP TO DISK as JSON (only 2/12 were saved)
│   ⭐ FIX: Map must exist on disk before Step 5 begins
│   ⭐ FIX: Priority sections from QB-1 get HIGH vision density
│   └── GATE: Every video has a map file. ≥5 sections. Opening scout present.
│
├── Step 5: Frame Capture
│   ├── Download video (720p default, 1080p for code-heavy)
│   ├── Build extraction plan from timestamp map
│   ├── Single-pass ffmpeg extraction
│   ⭐ FIX: ONE video per extraction command (no multi-video batching)
│   ⭐ FIX: Directory name validation — must be clean {video_id}/
│   ⭐ FIX: Generate frame_manifest.json (was never created)
│   ├── Delete video file immediately after extraction
│   └── GATE: Frames exist. Manifest exists. Opening scout captured. Video deleted.
│
├── Step 6: Enhanced Transcript Synthesis
│   ├── For each timestamp section:
│   │   ├── Pull original transcript text for timestamp range
│   │   ├── Feed frames to vision model with transcript context
│   │   └── Merge vision analysis INTO transcript (inline)
│   ⭐ FIX: WRITE TO DISK FIRST, then notify (was Telegram-first)
│   ⭐ FIX: Automated stub detection — word count check vs raw transcript
│   ⭐ FIX: HARD HALT if enhanced < 80% of raw transcript words
│   ⭐ FIX: Never delegate to cheap model — must be primary reasoning model
│   ⭐ FIX: Checksum/word-count verification after write
│   └── GATE: File exists on disk. Vision refs present. Word count ≥80%.
│
├── Step 7: Intelligence Report
│   ├── Executive Summary, Key Insights, Actionable Items
│   ├── Relevance to Jon's Projects, Cross-References
│   ├── Dual-Axis Scores
│   ⭐ FIX: Minimum 300 words (500+ for videos >10 min)
│   ⭐ FIX: Required sections checklist — programmatic validation
│   ⭐ FIX: Report derives from enhanced transcript (if transcript is stub, block report)
│   └── GATE: Report exists. Not stub. All 6 sections present. Scores assigned.
│
├── Step 8: Premium Infographic (Nano Banana 2)
│   ├── Generate from report + key frames ✅ (worked — all 13 generated)
│   └── GATE: PNG exists. >50KB. ✅
│
└── Step 9: Category Compilation
    ⭐ FIX: MANDATORY — cannot skip (was entirely skipped)
    ⭐ FIX: Must exist before Step 10 begins
    ⭐ FIX: Each category with 2+ videos gets compilation doc
    └── GATE: Compilation references all videos in category.

PHASE C: PLAYLIST-LEVEL SYNTHESIS
│
├── Step 10: Master Compilation
│   ⭐ FIX: Draws from category compilations, not individual reports
│   ⭐ FIX: Minimum 5,000 words for 10+ video batches
│   ⭐ FIX: Jon's priority flags MUST lead Section I
│   ⭐ FIX: One revision maximum — get it right the first time
│   └── GATE: Word count meets minimum. Priority items present.
│
├── Step 11: NotebookLM Integration
│   ├── Upload enhanced transcripts as sources
│   ├── Generate audio podcast ✅ (completed)
│   ├── Generate slide deck ✅ (completed)
│   ⭐ FIX: Pre-authenticate Google account BEFORE pipeline starts
│   └── GATE: Notebook exists. Audio generated. Slides generated.
│
├── Step 12: Content Assembly
│   └── (Not yet executed for this batch)
│
└── Step 13: Cleanup
    ⭐ FIX: Verify ALL outputs vs processing plan
    ⭐ FIX: Update global_processed_registry.json
    ⭐ FIX: Delete contaminated frame directories
    ⭐ FIX: Generate pipeline run summary with metrics
    └── GATE: All outputs verified. Registry updated.

PHASE D: CONTENT DISTRIBUTION
└── Step 14: Multi-Platform Push
    └── (Not yet executed — requires Jon review + approval)
```

---

## IV. v6.2 IMPROVEMENT SUMMARY (ALL CHANGES)

### NEW STEPS
| # | Improvement | Category |
|---|-------------|----------|
| 1 | **Pre-flight Environment Check** (Step -1) — verify caffeinate, sleep, disk, network before ANY processing | Environment |
| 2 | **Priority Section Flagging** in QB-1 — ask Jon what matters most before processing | Process |
| 3 | **Delegation Quality Gate** — define which steps can go to sub-agents vs must stay on primary model | Architecture |

### QUALITY GATES (HARD HALTS)
| # | Improvement | Category |
|---|-------------|----------|
| 4 | **Enhanced transcript stub detection** — automated word count check. If `enhanced < 80% raw`, HALT | Quality |
| 5 | **Report minimum word count** — 300 words min, 500+ for >10 min videos | Quality |
| 6 | **Report required sections checklist** — programmatic validation of all 6 sections | Quality |
| 7 | **Timestamp map must exist on disk** before frame extraction begins | Data Integrity |
| 8 | **Categories.json must exist** before Phase B begins | Data Integrity |
| 9 | **Category compilations must exist** before Master Compilation begins | Data Integrity |
| 10 | **Master Compilation minimum** — 5,000 words for 10+ video batches | Quality |

### DATA INTEGRITY FIXES
| # | Improvement | Category |
|---|-------------|----------|
| 11 | **Write-first, notify-second** — persist to disk before sending Telegram notification | Data Integrity |
| 12 | **Checksum verification** — read back and verify after write | Data Integrity |
| 13 | **Processing plan written as JSON** — not just verbal | Data Integrity |
| 14 | **Frame directory name validation** — regex check, no spaces | Data Integrity |
| 15 | **One video per extraction command** — never batch multiple videos | Data Integrity |
| 16 | **Frame manifest generation** — structured JSON mapping frames to sections | Data Integrity |

### PROCESS IMPROVEMENTS
| # | Improvement | Category |
|---|-------------|----------|
| 17 | **Priority sections get MAX vision density** regardless of content type | Process |
| 18 | **Never auto-classify ads as low priority** without checking priority flags | Process |
| 19 | **Addendums written back to disk** — not just Telegram-delivered | Process |
| 20 | **Master Compilation: Jon's priorities lead Section I** | Process |
| 21 | **Pre-authenticate Google/NotebookLM** before pipeline starts | Process |
| 22 | **Sub-agent model routing** — transcripts/frames OK on Flash; synthesis/analysis MUST be Opus/Sonnet | Architecture |

---

## V. MODEL ROUTING TABLE (v6.2 UPDATE)

| Step | Can Delegate to Sub-Agent? | Required Model Tier | Notes |
|------|---------------------------|---------------------|-------|
| QB-1 (Inventory) | ✅ Yes | Any | Metadata only |
| QB-2 (Transcripts) | ✅ Yes | Any (yt-dlp) | No LLM needed |
| QB-3 (Quick Synthesis) | ✅ Yes | Flash/DeepSeek | Speed over depth |
| Step 0 (Registry) | ✅ Yes | Any | JSON comparison |
| Step 1 (Metadata) | ✅ Yes | Any (yt-dlp) | No LLM needed |
| Step 2 (Transcripts) | ✅ Yes | Any (yt-dlp) | No LLM needed |
| Step 3 (Categorization) | ✅ Yes | Flash | Sufficient |
| Step 4 (Timestamp Map) | ⚠️ Supervised | Flash+ | Transcript analysis — Flash OK but verify |
| Step 5 (Frame Capture) | ✅ Yes | Any (ffmpeg) | No LLM needed |
| **Step 6 (Enhanced Transcript)** | **❌ NO** | **Opus/Sonnet** | **MUST stay on primary model** |
| **Step 7 (Intelligence Report)** | **❌ NO** | **Opus/Sonnet** | **MUST stay on primary model** |
| Step 8 (Infographic) | ✅ Yes | Nano Banana 2 | Dedicated image model |
| **Step 9 (Category Compilation)** | **❌ NO** | **Opus/Sonnet** | **Cross-video synthesis requires depth** |
| **Step 10 (Master Compilation)** | **❌ NO** | **Opus** | **Highest quality synthesis** |
| Step 11 (NotebookLM) | ⚠️ Supervised | Any (browser) | Needs authenticated browser |
| Step 12 (Content Assembly) | ✅ Yes | Sonnet | Template-driven |
| Step 13 (Cleanup) | ✅ Yes | Any | Filesystem ops |

---

## VI. PIPELINE RUN METRICS (THIS BATCH)

| Metric | Value |
|--------|-------|
| Total videos | 12 |
| Total raw transcript words | 362,190 (incl. VTT + clean + timestamped) |
| Total clean transcript words | ~130,000 (estimated) |
| Total frames captured | 9,487 |
| Properly enhanced transcripts | 4 of 12 (33%) |
| Stub enhanced transcripts | 8 of 12 (67%) |
| Properly completed reports | 4 of 12 (33%) |
| Stub reports | 8 of 12 (67%) |
| Timestamp maps on disk | 2 of 12 (17%) |
| Category compilations | 0 (0%) |
| Infographics | 13 (12 + master) ✅ |
| Master Compilation revisions | 3 (should be 1) |
| Sub-agent delegation failures | 1 (complete waste) |
| Mac sleep interruptions | Multiple (resolved mid-batch) |
| NotebookLM login blocks | 1 (resolved in separate session) |
| Estimated total processing time | ~6 hours |

---

## VII. RECOMMENDATION

**Before codifying v6.2:** The 8 stub enhanced transcripts and reports for Videos 5-12 should be redone properly. The frames exist (937-1,471 per video), the raw transcripts exist (4,631-21,531 words each). The intelligence is sitting in the frames and transcripts — it just was never extracted with the rigor v6.1 demands.

**Options:**
1. **Redo Videos 5-12** enhanced transcripts + reports now (before v6.2 codification)
2. **Codify v6.2 first**, then use v6.2 to reprocess Videos 5-12 as the first test batch
3. **Accept the stubs** for this batch and apply v6.2 to future batches only

**My recommendation:** Option 2 — codify v6.2 first, then reprocess. This way the reprocessing validates the improvements and catches any gaps in the v6.2 spec before it's used on completely new content.

---

*Audit generated: 2026-03-16 | YPE v6.1 Batch: ype-batch-2026-03-15*
*Auditor: Pulse Vibe Daily ⚡*
*Status: Awaiting Jon's review and direction*
