# YouTube Pipeline Experience (YPE) v6.0 — Consolidated Execution Skill

> **Version:** 6.1 (Strict Execution Protocol)
> **Purpose:** Single authoritative source for processing YouTube videos into enhanced transcripts, intelligence reports, and premium infographics. Zero ambiguity. Zero shortcuts.
> **Supersedes:** METHODOLOGY.md (v5.0), YPE-TRIGGER.md (v5.8), SKILL.md.archived, selective-extract.sh, process-video.sh, extract-frames.sh
> **Authors:** Jon (North Star) + Pulse Vibe Daily
> **Consolidated:** 2026-03-02 | **Amended:** 2026-03-02 (v6.1 — Nano Banana 2)
> **Philosophy:** Explicit instructions > agent judgment. Every decision pre-made. Every exception codified.

---

## TRIGGER

Any of these phrases activate the full pipeline:
- "youtube pipeline", "YPE", "run the pipeline", "pipeline these videos"
- "process these videos", "run YPE", "youtube pipeline experience"

When triggered:
1. Read this SKILL.md in full
2. Execute from Phase 0 (Quick-Batch) forward
3. No modifications. No shortcuts. No skipping.

---

## PIPELINE OVERVIEW

```
PHASE 0: QUICK-BATCH (QB-1 → QB-5)         ⏱️ 5-10 min
  └── Inventory → Transcripts → Quick Synthesis → Delivery → Auto-handoff

PHASE A: REGISTRY & CATEGORIZATION (Steps 0-3)
  └── Dedup Check → Inventory → Transcripts → Categorize

PHASE B: PER-VIDEO DEEP PROCESSING (Steps 4-9)
  └── Timestamp Map → Frame Capture → Enhanced Transcript → Report → Infographic → Category Compilation

PHASE C: PLAYLIST-LEVEL SYNTHESIS (Steps 10-13)
  └── Master Compilation → NotebookLM → Content Assembly → Cleanup

PHASE D: CONTENT DISTRIBUTION (Step 14)    ⚠️ ONLY after Steps 0-13 ALL complete
  └── Verification Gate → Jon Review → Multi-Platform Push
```

### Core Deliverables Per Video
1. **Enhanced Transcript** — Original transcript merged with vision analysis. Source of truth. ~95% video value capture.
2. **Intelligence Report** — Dual-axis scored analysis with actionable insights.
3. **Premium Infographic** — Visual knowledge artifact. Not a summary card. Not a text wall.

### Non-Negotiable Rules
- **NO partial distribution.** Step 14 fires only after Steps 0-13 complete.
- **NO skipping frame capture.** Every video gets frames. Period.
- **NO stub outputs.** If transcript >30KB, chunk it. Never truncate.
- **Sabbath compliance.** No pipeline execution Friday sunset → Saturday sunset.

---

## PHASE 0: QUICK-BATCH PRE-PHASE

> The appetizer, not the meal. Gives immediate situational awareness before deep processing.

### QB-1: Video List Confirmation
```
INPUT:  Video URLs/IDs from Jon
OUTPUT: Confirmed inventory table
```
For each video, present:
- Video ID, title, channel name
- Upload date, duration, view count
- Thumbnail (if available)

**GATE:** Jon confirms the list before ANY processing. If Jon flags a wrong video → swap → re-confirm.

### QB-2: Transcript Quick-Pull
```
INPUT:  Confirmed video list
OUTPUT: Raw transcripts (reused by Step 2)
TOOL:   yt-dlp --write-auto-sub --sub-lang en --skip-download
```
For each transcript, flag:
- Manual vs auto-generated
- Word count
- If >30KB → flag for chunked processing in Phase B
- Language (non-English → flag for translation)

**These transcripts are REUSED in Step 2. No duplicate downloads.**

### QB-3: Quick Intelligence Synthesis
```
INPUT:  All transcripts
OUTPUT: Per-video quick assessment
MODEL:  Cheapest available (Gemini Flash / DeepSeek)
```
Per video:
- Executive summary (3-5 sentences)
- Top 3 actionable insights
- Relevance score: 🔴 HIGH / 🟠 MEDIUM / 🟡 LOW (scored against Jon's current projects)
- Suggested topic routing
- Video recency signal (upload date vs today)
- Channel authority indicator
- Duplicate/overlap detection within batch

### QB-4: Quick-Batch Delivery
```
OUTPUT: Compiled QB report delivered to Jon
```
- Push immediately applicable insights to knowledge base
- Flag any videos Jon might want to deprioritize

### QB-5: Mandatory Handoff
```
ACTION: Automatically commence Step 0
```
- QB transcripts passed to Step 2 (no re-download)
- Pipeline state initialized from QB metadata
- **THIS HANDOFF IS AUTOMATIC. NO PAUSE. NO "SHOULD I CONTINUE?"**

---

## PHASE A: REGISTRY & CATEGORIZATION

### Step 0: Registry Check (MANDATORY FIRST)
```
INPUT:  Video IDs from QB-1
OUTPUT: processing-plan.json
TOOL:   Check against global_processed_registry.json
```

For EACH video ID:
- **EXISTS + v4+ quality + all steps complete** → `skip-reprocess` (symlink existing assets)
- **EXISTS + partial steps** → `resume` (pick up from first incomplete step)
- **EXISTS + quality < v4** → `reprocess` (full pipeline)
- **NOT EXISTS** → `process_new` (full pipeline)

Report to Jon:
```
"Playlist has X videos. Y already processed (importing). Z need full processing.
 Estimated cost: $N. Estimated time: T."
```

**GATE:** Jon approves processing plan before proceeding.

### Step 1: Playlist Inventory & Enhanced Metadata
```
INPUT:  Processing plan
OUTPUT: metadata/{id}.json per video
```
Per video:
- Title, channel, upload date, duration, view count
- Description (first 500 chars)
- Tags/keywords
- Playlist position

### Step 2: Transcript Download
```
INPUT:  Video IDs
OUTPUT: transcripts/{id}.md
TOOL:   yt-dlp (or reuse QB-2 transcripts)
```
- Reuse QB-2 transcripts — do NOT re-download
- Verify completeness (word count > 100)
- Flag quality issues
- For each: record `word_count`, `is_auto_generated`, `language`

### Step 3: LLM Categorization
```
INPUT:  All transcripts + metadata
OUTPUT: categories.json
MODEL:  Gemini Flash (FREE)
```
Assign each video to a category. Categories are defined per playlist.

**GATE:** Combined approval — Jon reviews category assignments + any flags from Steps 1-2.

---

## PHASE B: PER-VIDEO DEEP PROCESSING

> Steps 4-9 run for EVERY video marked `process_new` or `reprocess` in Step 0.

### Step 4: Timestamp Map Generation
```
INPUT:  transcripts/{id}.md
OUTPUT: timestamp-maps/{id}-map.json
MODEL:  Gemini Flash (FREE — transcript analysis only)
```

#### Large Transcript Handling
If transcript > 30KB:
1. Split into overlapping chunks (25KB each, 2KB overlap)
2. Process each chunk independently
3. Merge results, deduplicate sections by timestamp proximity (<10s = same section)

#### Four Capture Categories
Every section must be classified as one of:
1. **Insight** — New information, revelations, "aha" moments
2. **Takeaway** — Lessons learned, principles, wisdom
3. **Key Moment** — Demos, code on screen, UI reveals, architecture diagrams, tool usage
4. **Actionable Item** — Specific things Jon can implement today

#### Section Schema
```json
{
  "id": 1,
  "start_timestamp": "HH:MM:SS",
  "end_timestamp": "HH:MM:SS",
  "start_seconds": 0,
  "end_seconds": 26,
  "type": "insight | takeaway | key_moment | actionable",
  "topic": "Brief description",
  "summary": "1-2 sentences capturing substance",
  "needs_vision": true,
  "vision_density": "high | medium | low",
  "importance": "high | medium | low",
  "key_insights": [
    { "timestamp": "HH:MM:SS", "insight": "Description" }
  ]
}
```

#### Vision Classification Rules

**`needs_vision: true`** when the section contains ANY of:
- Code, terminal output, or IDE visible on screen
- UI demonstrations or app walkthroughs
- Slides, diagrams, flowcharts, or architecture visuals
- Tool configuration or settings screens
- Browser/website demonstrations
- Physical demonstrations or product reveals
- Data visualizations, charts, or dashboards
- Screen recordings or multi-window setups

**`needs_vision: false`** ONLY when:
- Pure talking head with no screen share
- Audio-only philosophical discussion
- Interviewer/interviewee with static background
- No visual content is referenced or implied in the transcript

**When uncertain, default to `needs_vision: true`.** Over-capture is always preferred to under-capture.

#### Vision Density Rules
- **`high`** (2-3 fps equivalent) — Code scrolling, terminal output, rapidly changing UI, live typing
- **`medium`** (1 fps equivalent) — Slides, diagrams, static UI demos, settings screens
- **`low`** (0.5 fps equivalent) — Occasional screen share, talking head with background content

#### Frame Budget Caps
```
Video < 5 min:                                    max 50 frames
Video 5-30 min:                                   max 150 frames
Video > 30 min:                                   max 200 frames
Video > 60 min, < 3 vision sections (podcast):    max 10 frames
Video > 60 min, > 10 vision sections (tutorial):  max 300 frames
```

If section densities would exceed budget, reduce `vision_density` on lower-importance sections until within budget. Never reduce to zero — minimum 1 frame per section.

#### Mandatory Sections (Non-Negotiable)

These sections are ALWAYS included in the timestamp map regardless of transcript content:

1. **OPENING SCOUT (0:00 - 0:10)**
   ```json
   {
     "id": 0,
     "start_timestamp": "00:00:00",
     "end_timestamp": "00:00:10",
     "type": "key_moment",
     "topic": "Opening Scout — Visual Hook Assessment",
     "summary": "Mandatory capture of video opening to assess visual style, production quality, and hook strategy.",
     "needs_vision": true,
     "vision_density": "high",
     "importance": "high"
   }
   ```
   **Purpose:** The first 10 seconds reveal production quality, visual style, whether there's a cold open with graphics, code, or demo footage. This CANNOT be determined from transcript. Always capture.

2. **CLOSING SCOUT (last 10 seconds)**
   ```json
   {
     "id": -1,
     "start_timestamp": "{duration - 10s}",
     "end_timestamp": "{duration}",
     "type": "key_moment",
     "topic": "Closing Scout — Outro & CTA Assessment",
     "summary": "Mandatory capture of video closing for CTA patterns, endscreen strategy, and final visual.",
     "needs_vision": true,
     "vision_density": "medium",
     "importance": "medium"
   }
   ```

#### Minimum Requirements
- Minimum 5 sections per video (including mandatory opening/closing scouts)
- If fewer than 5 non-mandatory sections identified → flag video for manual review
- Every section gets at least 1 frame in Step 5

#### Output Format
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "total_duration": "HH:MM:SS",
  "total_duration_seconds": 754,
  "frame_budget": 150,
  "estimated_frames": 87,
  "mandatory_sections": 2,
  "sections": [ "..." ],
  "stats": {
    "total_sections": 14,
    "vision_sections": 10,
    "non_vision_sections": 2,
    "mandatory_sections": 2,
    "insights": 4,
    "takeaways": 3,
    "key_moments": 5,
    "actionable_items": 2
  }
}
```

**GATE:** Every video has a timestamp map. Every map has ≥ 5 sections. Opening scout present.

---

### Step 5: Frame Capture (Single-Pass)
```
INPUT:  timestamp-maps/{id}-map.json
OUTPUT: frames/{id}/frame_NNNN_tNNNN.jpg + frame_manifest.json
TOOLS:  yt-dlp (download) + ffmpeg (extraction)
```

#### 5a: Download Video
```bash
yt-dlp \
  -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --merge-output-format mp4 \
  -o "downloads/{id}.%(ext)s" \
  "{video_url}"
```
- Default 720p
- If Step 6 produces LOW confidence on code blocks → re-download at 1080p, re-extract those sections only

**⚠️ EVERY video gets downloaded. There is no "0 vision sections = skip download" path.** The mandatory opening/closing scouts guarantee minimum 2 vision sections per video.

#### 5b: Build Extraction Plan

From the timestamp map, build the ffmpeg filter:

**For `needs_vision: true` sections:**
| Vision Density | Frame Interval (30fps source) | Approx FPS |
|---|---|---|
| `high` | every 15th frame: `not(mod(n,15))` | ~2 fps |
| `medium` | every 30th frame: `not(mod(n,30))` | ~1 fps |
| `low` | every 60th frame: `not(mod(n,60))` | ~0.5 fps |

**For `needs_vision: false` sections:**
- Extract exactly 1 frame at the midpoint of the section
- This is a "scout frame" — captures ambient visual context

**For mandatory sections (opening/closing scout):**
- Opening (0-10s): 3 frames at 0s, 5s, 10s
- Closing (last 10s): 2 frames at -10s and -5s from end

#### 5c: Single-Pass Extraction

Build ONE ffmpeg command from the complete plan:
```bash
ffmpeg -i "downloads/{ID}.mp4" \
  -vf "select='...combined filter...',setpts=N/FRAME_RATE/TB" \
  -vsync vfr \
  -q:v 2 \
  "frames/{ID}/frame_%04d.jpg"
```

If single-pass filter becomes too complex (>20 sections), split into max 3 passes.

#### 5d: Frame Naming & Manifest
```
frames/{video_id}/
├── frame_0001_t0000.jpg    ← Opening scout
├── frame_0002_t0005.jpg    ← Opening scout
├── frame_0003_t0010.jpg    ← Opening scout
├── frame_0004_t0090.jpg    ← Section 1 (vision)
├── ...
├── frame_0087_t0744.jpg    ← Closing scout
└── frame_manifest.json
```

Manifest format:
```json
{
  "video_id": "abc123",
  "total_frames": 87,
  "capture_method": "ype-v6-strict",
  "sections_mapped": 14,
  "vision_sections": 10,
  "scout_frames": 5,
  "frames": [
    {
      "file": "frame_0001_t0000.jpg",
      "timestamp_sec": 0,
      "section_id": 0,
      "section_type": "mandatory_opening",
      "topic": "Opening Scout"
    }
  ]
}
```

#### 5e: Video File Deletion
```bash
rm -f "downloads/{video_id}.*"
```
**CRITICAL:** Delete video IMMEDIATELY after frame extraction. No exceptions. Disk space is limited.

#### 5f: Validation
- Frame count > 0 for every video
- Manifest exists and is valid JSON
- Opening scout frames (3) present
- At minimum: `mandatory_frames(5) + 1_per_non_vision_section`

**GATE:** Every video has frames. Frame count matches manifest. Opening scout captured. Video file deleted.

---

### Step 6: Enhanced Transcript Synthesis
```
INPUT:  transcripts/{id}.md + frames/{id}/ + timestamp-maps/{id}-map.json
OUTPUT: enhanced-transcripts/{id}-enhanced.md
MODEL:  Vision model for frames, LLM for synthesis
```

For each section in the timestamp map:
1. Pull the original transcript text for that timestamp range
2. If `needs_vision: true` AND frames exist → feed frames to vision model with transcript context
3. If `needs_vision: false` → scout frame provides ambient context only
4. Merge vision analysis INTO transcript (inline, not appended)

#### Vision Analysis Prompt (per frame batch)
```
Analyze these frames from a YouTube video. Context from transcript:
"{transcript_section_text}"

For each frame, describe:
1. What is visible on screen (code, UI, diagram, slide, etc.)
2. Any text that is readable
3. How this visual content relates to what's being said
4. Anything the transcript MISSES that the frame reveals

Be specific. Quote visible text exactly. Note UI elements, file names,
terminal commands, configuration values.
```

#### Confidence Scoring
After vision analysis, rate confidence:
- **HIGH** — Clear screen content, readable text, vision adds significant value
- **MEDIUM** — Partial visibility, some text readable, moderate value add
- **LOW** — Blurry, small text, minimal value add → flag for 1080p re-extraction

#### Large Transcript Chunking
If enhanced transcript would exceed 30KB:
1. Process each timestamp map section individually
2. Merge into full document preserving section order
3. Cross-reference between sections
4. Never truncate or summarize sections to fit size limits

#### Output Format
```markdown
# Enhanced Transcript: {Title}

## Video Metadata
- **Channel:** {channel}
- **Duration:** {duration}
- **Processed:** {date}
- **Vision Frames:** {count}

## Section 1: {topic} [{start} - {end}]
**Type:** {insight|takeaway|key_moment|actionable}

{Original transcript text}

> 🖼️ **Vision Analysis** (frame_0004_t0090.jpg)
> {What the frame reveals that the transcript doesn't capture}
> Visible text: "{exact quoted text from screen}"

{Continue for all sections}

## Key Findings Summary
{Cross-section insights that emerge from combining transcript + vision}
```

**GATE:** Enhanced transcript exists. Vision sections include frame references. No stub/placeholder text. Word count ≥ 80% of original transcript.

---

### Step 7: Intelligence Report
```
INPUT:  enhanced-transcripts/{id}-enhanced.md
OUTPUT: reports/{id}-report.md
MODEL:  Primary reasoning model
```

Generate a structured intelligence report:
- Executive Summary (3-5 sentences)
- Key Insights (ranked by importance)
- Actionable Items (specific, implementable)
- Relevance to Jon's Projects (mapped to active projects)
- Cross-Reference Opportunities (connections to other processed videos)
- Dual-Axis Score:
  - **Information Density:** 1-10 (how much new knowledge per minute)
  - **Actionability:** 1-10 (how immediately implementable)

**GATE:** Report exists. Not a stub. Contains all required sections. Scores assigned.

---

### Step 8: Premium Infographic (Nano Banana 2)
```
INPUT:  reports/{id}-report.md + key frames from Step 5
OUTPUT: infographics/{id}.png
MODEL:  Nano Banana 2 (Gemini 3.1 Flash Image) — primary infographic generator
TOOL:   uv run {nano-banana-pro-skill-dir}/scripts/generate_image.py
```

#### Why Nano Banana 2
- 10x better visual quality than Nano Banana Pro (v1)
- Faster generation, lower cost
- Native image output — no HTML→PNG conversion pipeline needed
- Eliminates Chrome/Puppeteer rendering dependency (which previously blocked PNG generation)

#### Generation Method
Build a detailed prompt from the intelligence report, then generate directly:

```bash
uv run {baseDir}/scripts/generate_image.py \
  --prompt "{infographic_prompt}" \
  --filename "infographics/{id}.png" \
  --resolution 2K
```

If key frames should be composited into the infographic:
```bash
uv run {baseDir}/scripts/generate_image.py \
  --prompt "{infographic_prompt}" \
  --filename "infographics/{id}.png" \
  -i "frames/{id}/frame_0001_t0000.jpg" \
  -i "frames/{id}/{best_key_frame}.jpg" \
  --resolution 2K
```

#### Infographic Prompt Construction
Build the prompt from the intelligence report. Include:
1. Video title, channel, duration, date
2. Dual-axis scores (Information Density + Actionability)
3. Executive summary (3-5 sentences)
4. Top 3-5 insights (ranked)
5. Actionable items (checklist)
6. Category/tags
7. Visual style: "Premium knowledge infographic, dark theme, modern data visualization, clean typography, color-coded sections, NOT a text wall"

#### Design Requirements
- Rich visual layout — NOT a text card
- Data visualizations for scores
- Color-coded sections by type (insight/takeaway/key_moment/actionable)
- Jon would be proud to put this in his library
- Minimum 1024x1536px (2K resolution)
- Each infographic visually distinct — no cookie-cutter templates

#### Fallback
If Nano Banana 2 fails or GEMINI_API_KEY unavailable:
1. Fall back to HTML generation + browser PNG capture
2. Log the fallback as a non-blocking warning
3. Continue pipeline — do not halt for infographic failures

**GATE:** PNG exists. File size > 50KB (not a stub/error image). Visually verified if possible.

---

### Step 9: Category Compilation
```
INPUT:  All reports + infographics for a category
OUTPUT: categories/{slug}/compilation.md + category infographic
```

Cross-video synthesis within category:
- Common themes across videos
- Contradictions or disagreements
- Progression of ideas
- Gap analysis — what's NOT covered
- Category-level infographic (same premium standard)

**GATE:** Compilation references all videos in category. Not just concatenation.

---

## PHASE C: PLAYLIST-LEVEL SYNTHESIS

### Step 10: Master Compilation
```
INPUT:  All category compilations
OUTPUT: MASTER-COMPILATION.md
```
- Cross-category patterns
- The "so what" — what does this playlist teach Jon overall
- Priority-ranked action items across all videos

### Step 11: NotebookLM Integration
```
INPUT:  Enhanced transcripts + master compilation
OUTPUT: NotebookLM notebook link + audio podcast + slide deck
```
- Upload enhanced transcripts as sources
- Generate audio overview (podcast format)
- Generate multi-panel presentation deck

### Step 12: Content Assembly
```
INPUT:  All pipeline outputs
OUTPUT: content-drops/{playlist}/
```
- 8-platform content drafts (X, LinkedIn, IG, TikTok, YT Short, Telegram, Snap, FB)
- Each piece references compiled intelligence, NOT individual video reposts
- Remotion video script for Anti-gravity channel

### Step 13: Cleanup
```
ACTIONS:
1. Delete any remaining video files (catches Step 5e stragglers)
2. Verify all outputs exist and are non-stub
3. Update global_processed_registry.json
4. Archive timestamp maps (captured in enhanced transcripts)
5. Generate pipeline run summary with metrics
```

---

## PHASE D: CONTENT DISTRIBUTION

### Step 14: Multi-Platform Push
```
PREREQUISITE: Steps 0-13 ALL complete. No exceptions.
```

**VERIFICATION GATE:**
- [ ] Every video has: enhanced transcript, report, infographic
- [ ] Category compilations complete
- [ ] Master compilation complete
- [ ] Content drops drafted
- [ ] Jon has reviewed and approved content package

Only after verification → execute distribution via content pipeline.

---

## PROCESSING MODES

### Singles Mode (1-3 videos)
- Full pipeline per video
- No category compilation needed if single category
- Fastest path to complete deliverables

### Small Batch Mode (4-15 videos)
- QB pre-phase for situational awareness
- Batch Steps 1-3 (inventory, transcripts, categorization)
- Step 4-8 per video (can parallelize with sub-agents)
- Steps 9-13 after all individual processing complete

### Full Playlist Mode (16+ videos)
- QB pre-phase mandatory
- Category-first processing (complete one category before next)
- Progress checkpoints every 10 videos
- Incremental delivery: category compilations as they complete

---

## VIOLATION PROTOCOL

If ANY of these rules are broken:
1. **Log violation** to `memory/{date}.md` with exact step, rule, and rationale
2. **Alert Jon** immediately — do not continue silently
3. **Halt pipeline** at current step
4. **Do not self-correct and continue** — wait for Jon's direction

### Common Violations (Explicitly Prohibited)
- ❌ Skipping frame capture because "transcript looks text-only"
- ❌ Using 1 frame per section instead of density-based extraction
- ❌ Downloading at <720p without explicit approval
- ❌ Passing off QB-3 synthesis as intelligence reports
- ❌ Generating "lean card" infographics instead of premium
- ❌ Skipping opening/closing scout frames
- ❌ Truncating large transcripts instead of chunking
- ❌ Running Step 14 before Steps 0-13 complete
- ❌ Scope-creeping the video list without Jon's approval

---

## QUALITY STANDARDS

### Stub Detection
A stub is any output that:
- Is shorter than 30% of expected length
- Contains placeholder text ("TODO", "TBD", "will be completed")
- Lacks required sections from the output format
- Enhanced transcript shorter than original transcript

**If a stub is detected: halt, flag, redo. Never ship stubs.**

### Enhanced Transcript Quality
- Must include vision analysis for every `needs_vision: true` section
- Must reference specific frame files
- Must capture readable on-screen text verbatim
- Word count ≥ 80% of original transcript (vision adds, never subtracts)

### Infographic Quality
- Not a text dump with a colored header
- Contains actual data visualizations
- Includes frame captures where relevant
- Minimum 800x1200px resolution
- Jon would put it in his library

---

## TECHNICAL REFERENCE

### File Structure
```
{batch-dir}/
├── transcripts/          # Step 2 — raw transcripts
├── metadata/             # Step 1 — per-video metadata JSON
├── timestamp-maps/       # Step 4 — section maps with vision flags
├── frames/               # Step 5 — captured frames + manifests
│   └── {video_id}/
│       ├── frame_0001_t0000.jpg
│       └── frame_manifest.json
├── enhanced-transcripts/ # Step 6 — SOURCE OF TRUTH
├── reports/              # Step 7 — intelligence reports
├── infographics/         # Step 8 — HTML + PNG
├── categories/           # Step 9 — per-category compilations
├── downloads/            # TEMP — deleted after frame extraction
├── categories.json       # Step 3 — category assignments
├── processing-plan.json  # Step 0 — registry check results
└── MASTER-COMPILATION.md # Step 10
```

### Model Routing
| Task | Model | Reason |
|---|---|---|
| Categorization (Step 3) | Gemini Flash | Free, sufficient |
| Timestamp maps (Step 4) | Gemini Flash | Free, transcript-only |
| Vision analysis (Step 6) | Image model (configured) | Frame analysis |
| Enhanced transcript (Step 6) | Primary reasoning model | Synthesis quality |
| Intelligence report (Step 7) | Primary reasoning model | Analysis quality |
| Infographic (Step 8) | Nano Banana 2 (Gemini 3.1 Flash Image) | Direct PNG generation, no HTML intermediate |
| Quick synthesis (QB-3) | Cheapest available | Speed over depth |

### Dependencies
- `yt-dlp` — video/transcript download
- `ffmpeg` — frame extraction
- `python3` — manifest generation, timestamp parsing
- Nano Banana 2 (`uv run generate_image.py`) — direct infographic PNG generation
- Browser/Puppeteer — fallback only if Nano Banana 2 unavailable

### Sabbath Compliance
- No pipeline execution Friday sunset → Saturday sunset
- If pipeline is mid-run at Friday sunset: save state, halt, resume Saturday sunset
- Cron jobs: pause during Sabbath window

---

## AGENT ASSIGNMENTS

| Phase | Primary Agent | Support |
|-------|--------------|---------|
| Quick-Batch | Pulse ⚡ | Scout 🔍 (metadata enrichment) |
| Phase A (Registry) | Stash 📚 | — |
| Phase A (Verify/Categorize) | Stash 📚 | Pulse ⚡ (Jon approval) |
| Phase B (Deep Processing) | Stash 📚 + Forge 🔨 | Vision model (frames) |
| Phase C (Synthesis) | Pulse ⚡ | All agents for compilation |
| Phase D (Distribution) | Echo 📢 | Pulse ⚡ (approval gate) |

### Judge Integration
Judge ⚖️ activates ONLY at:
- **Step 3 gate** — Category assignment deliberation
- **Step 10** — Master compilation review
- **Step 14 gate** — Content package review before external push

All other gates remain Jon-only approval.

---

## VERSION HISTORY

| Version | Date | Changes |
|---|---|---|
| v6.1 | 2026-03-02 | Nano Banana 2 (Gemini 3.1 Flash Image) replaces HTML→PNG infographic pipeline. Direct PNG generation, 10x quality improvement, eliminates Chrome/Puppeteer dependency. |
| v6.0 | 2026-03-02 | Consolidated from METHODOLOGY.md + YPE-TRIGGER.md. Added: mandatory opening/closing scouts, scout frames for non-vision sections, every-video-gets-frames rule, violation protocol with explicit prohibitions, stub detection, strict density-based extraction. Eliminated agent judgment on frame capture. |
| v5.8 | 2026-02-24 | Added Quick-Batch pre-phase, global trigger, violation protocol, Judge agent gates |
| v5.0 | 2026-02-21 | Definitive consolidated spec. 15 steps, 5 phases. XML-hybrid format. |
| v4.0 | 2026-02-12 | Global registry, incremental updates, Sabbath compliance |
| v3.1 | 2026-02-10 | Category-first architecture |
| v1.0-v3.0 | Various | Original pipeline iterations |

---

*This file is the ONLY authority. METHODOLOGY.md is retained in archive as background reference only.*
*When this skill is invoked, follow it line by line. No improvisation. No optimization shortcuts.*
*If something isn't covered here, STOP and ask Jon before proceeding.*
*— Jon (North Star) + Pulse Vibe Daily ⚡ | 2026-03-02*
