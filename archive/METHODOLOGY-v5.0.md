<!-- Companion: RUNBOOK.md — execution state & progress tracking -->

<pipeline version="5.0" consolidated="2026-02-21" authors="Jon + Pulse Vibe Daily">

# YouTube Pipeline v5.0 — Definitive Knowledge Ingestion System

> **Version:** 5.0 (Final Consolidated Spec — XML-Hybrid)
> **Purpose:** Process YouTube playlists into enhanced transcripts, intelligence reports, premium infographics, and multi-format content deliverables with cross-playlist deduplication, incremental updates, NotebookLM integration, and content distribution support.
> **Authors:** Jon (North Star Command Protocol) + Pulse Vibe Daily
> **Consolidated:** 2026-02-21
> **Supersedes:** v1.0, v2.0, v3.0, v3.1, v4.0, v4.5, and the original SKILL.md — ALL prior specs are now archived. This is the ONLY authoritative source.

---

<overview>

## Pipeline Overview

This pipeline transforms YouTube playlists into a structured knowledge base through **15 steps (Step 0 through Step 14)** organized in five phases. Every video produces an enhanced transcript (merging spoken content with vision-model analysis of on-screen content), an intelligence report scored on dual axes, and a premium infographic.

### The Core Product (Per Video)

Every video produces TWO deliverables:

1. **Enhanced Transcript** — The original transcript merged with vision analysis, creating a comprehensive knowledge base that captures ~95% of the video's value (vs ~40% from transcript alone). This is the **source of truth**.

2. **Premium Infographic** — A rich visual built FROM the enhanced transcript + captured frames. Shows insights, takeaways, key moments, actionable items. Lets Jon understand the video at a glance without watching it.

**These are NOT summaries. These are knowledge artifacts.** The infographic at every level — video, category, playlist — must meet the premium standard. No "lean cards." No text walls. Every infographic is a deliverable Jon would be proud to put in his library.

### The Core Value Proposition

The value of PVD's content is the **COMPILED, SYNTHESIZED intelligence** — cross-video insights, patterns, gaps identified, Pulse's own intelligent analysis layer on top. **NOT individual video reposts.** The full pipeline must complete Steps 0-13 before ANY content gets pushed externally. Step 14 (Content Distribution) is the handoff to the content pipeline, and it ONLY fires after everything is done.

### Five Phases

```
PHASE 0: REGISTRY & DEDUP (Step 0)
  └── Check ALL videos against global registry BEFORE any processing

PHASE A: PLAYLIST VERIFICATION & CATEGORIZATION (Steps 1-3)
  └── Inventory → Transcripts → Categorize + Combined Approval Gate

PHASE B: PER-CATEGORY DEEP PROCESSING (Steps 4-9)
  └── Timestamp Map → Frames → Enhanced Transcript → Report → Infographic → Category Compilation

PHASE C: PLAYLIST-LEVEL SYNTHESIS (Steps 10-13)
  └── Master Compilation → NotebookLM → Content Deliverables Assembly → Cleanup

PHASE D: CONTENT DISTRIBUTION — POST-PIPELINE (Step 14)
  └── Verification Gate → Jon Review → 8-Platform Push → Anti-gravity Video
  └── ONLY triggers after Steps 0-13 are ALL complete. No partial pushes.
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     GLOBAL VIDEO REGISTRY                       │
│                  (global_processed_registry.json)                │
│            Tracks all processed videos across ALL playlists      │
└──────────┬──────────────────────────────────┬───────────────────┘
           │                                  │
           ▼                                  ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│  STEP 0: REGISTRY CHECK    │   │   INCREMENTAL UPDATE PATH   │
│  (MANDATORY BEFORE ALL)    │   │   Diff → New Videos Only    │
│  Skip/Reuse/Resume/New     │   └──────────┬──────────────────┘
└──────────┬──────────────────┘              │
           │                                 │
           ▼                                 ▼
┌─────────────────────────┐       ┌───────────────────────────┐
│  PHASE A (Steps 1-3)    │       │  For each new/resume video │
│  Playlist Verify &      │       │  → Enter at appropriate    │
│  Categorization          │       │    step in Phase B         │
└──────────┬──────────────┘       └──────────┬────────────────┘
           │                                  │
           ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE B (Steps 4-9) — Per-Category                 │
│  Timestamp Map → Frames → Enhanced Transcript →                 │
│  Report → Infographic → Category Compilation                    │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE C (Steps 10-13) — Playlist-Level             │
│  Master Compilation → NotebookLM → Content Assembly → Cleanup   │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE D (Step 14) — POST-PIPELINE                  │
│  ⚠️ VERIFICATION GATE: All Steps 0-13 complete?                │
│  Jon reviews content package → 8-platform distribution →        │
│  Anti-gravity / Remotion video → Handoff to content pipeline    │
│  NO PARTIAL PUSHES. COMPILED INTELLIGENCE ONLY.                 │
└─────────────────────────────────────────────────────────────────┘
```

### What's New in v5.0

| Enhancement | Impact | Section |
|---|---|---|
| Step 0 FIRST (Registry Check) | Prevents ALL duplicate processing — must run before ANY work | §Step 0 |
| NotebookLM as Phase (Step 11) | Audio podcasts, multi-panel decks, deep research — complementary to pipeline | §Step 11 |
| Content Assembly Phase (Step 12) | Prepare all deliverables — podcasts, slides, infographics, content drafts | §Step 12 |
| Content Distribution POST-PIPELINE (Step 14) | 8-platform push ONLY after full pipeline completion. Compiled intelligence, not reposts. | §Step 14 |
| Anti-gravity Video Creation | Remotion integration for programmatic video from pipeline data | §Step 14 |
| Large Transcript Chunking Fix | Handles >30KB transcripts that caused stub/placeholder output | §Chunking |
| Processing Modes | Singles, small batch (5-10), full playlist — each with specific workflows | §Modes |
| Dual Infographic Standard | PVD = single PNG (social), NotebookLM = multi-panel deck (presentations) | §Step 11 |
| External Drive Storage | Pipeline data → external drive, symlinks from workspace | §Technical |
| Consolidated from 6 prior specs | Eliminates spec drift and lost knowledge | All |

</overview>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                    PHASE 0: REGISTRY & DEDUP                   -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<phase id="0" name="Registry &amp; Dedup">

<step id="0" name="Playlist Registry Check" phase="0">

<meta>
  <input>Playlist URL(s) to process</input>
  <output>processing-plan.json with per-video action assignments</output>
  <models>Local JSON (FREE)</models>
  <gate>Processing plan reviewed by Jon before ANY work begins. Dedup savings reported.</gate>
</meta>

## Step 0: Playlist Registry Check (MANDATORY FIRST)

> **⚠️ THIS STEP RUNS BEFORE ANYTHING ELSE. NO EXCEPTIONS.**
> Before downloading a single transcript, before extracting a single frame, before ANY processing — check the global registry.

### Process

```
1. Fetch all video IDs from playlist(s) via yt-dlp --flat-playlist
2. For EACH video ID, check global_processed_registry.json:

   IF video.id EXISTS in registry:
     IF registry[video.id].qualityTier >= "v4" AND all steps complete:
       ACTION = "skip-reprocess"
       → Link existing assets (symlink or copy from source path)
       → Only run: category assignment + compilation steps
       → Log: "REUSE: {title} — already processed at v4+ in {source_playlist}"
     
     ELSE IF registry[video.id] has partial steps:
       ACTION = "resume"
       → Identify which steps are complete
       → Resume from first incomplete step
       → Log: "RESUME: {title} — resuming from Step {next_step}"
     
     ELSE (qualityTier < "v4" or missing key outputs):
       ACTION = "reprocess"
       → Full pipeline, but note what exists for reference
       → Log: "REPROCESS: {title} — quality tier {tier} needs upgrade"
   
   ELSE:
     ACTION = "process_new"
     → Full pipeline processing (Steps 1-8)
     → Create new registry entry
     → Log: "NEW: {title} — full processing required"

3. Generate processing-plan.json with summary
4. Report to Jon before proceeding:
   "Playlist has X videos. Y already processed (importing). Z need full processing.
    Estimated cost: $N. Estimated time: T."
```

### Processing Plan Format

```json
{
  "playlist_id": "PLxxx123",
  "playlist_url": "https://youtube.com/playlist?list=PLxxx123",
  "plan_generated": "2026-02-20T10:00:00Z",
  "summary": {
    "total_videos": 97,
    "skip_reprocess": 22,
    "resume": 3,
    "reprocess": 5,
    "process_new": 67,
    "estimated_cost_usd": 3.50,
    "estimated_savings_percent": 25.5
  },
  "videos": {
    "dQw4w9WgXcQ": {
      "action": "skip-reprocess",
      "existing_paths": { "...source paths..." },
      "original_playlist": "antigravity",
      "quality_tier": "v4"
    },
    "abc123XYZ": {
      "action": "process_new"
    },
    "def456": {
      "action": "resume",
      "completed_steps": ["transcript", "frames"],
      "resume_from": "enhanced_transcript"
    }
  }
}
```

### Registry Maintenance Rules
- Every time a video completes v4+ processing, it's added/updated in the global registry
- Registry is playlist-agnostic — tracks ALL videos across ALL playlists
- Quality tier determines reuse eligibility: only v4+ gets reused
- If a video needs frame extraction that was deferred, flag for frame-only processing, NOT full reprocess

<registry-update>
Create or update registry entries for all videos in the processing plan. Set `action` field per video. Record `plan_generated` timestamp. No processing outputs yet — this is planning only.
</registry-update>

</step>

</phase>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--            PHASE A: PLAYLIST VERIFICATION & CATEGORIZATION     -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<phase id="A" name="Playlist Verification &amp; Categorization">

<step id="1" name="Playlist Inventory &amp; Enhanced Metadata" phase="A">

<meta>
  <input>YouTube playlist URL(s) — only videos marked `process_new` or `resume` from Step 0</input>
  <output>playlist-inventory.json, per-video .info.json metadata files</output>
  <models>yt-dlp (FREE)</models>
  <gate>Jon verifies playlist contents before processing. `verified_by_jon: true` required.</gate>
</meta>

## Step 1: Playlist Inventory & Enhanced Metadata

### Process

1. Extract full playlist metadata:

```bash
yt-dlp \
  --flat-playlist \
  --write-info-json \
  --skip-download \
  --download-archive processed_videos.txt \
  -o "metadata/%(id)s" \
  "{playlist_url}"
```

2. Build `playlist-inventory.json`:

```json
{
  "playlist_id": "PLxxx123",
  "playlist_title": "AI Tools 2025",
  "playlist_url": "https://youtube.com/playlist?list=PLxxx123",
  "extraction_date": "2026-02-20",
  "verified_by_jon": false,
  "total_videos": 97,
  "videos": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "Video Title Here",
      "duration": "00:12:34",
      "upload_date": "2025-06-15",
      "channel": "Channel Name",
      "view_count": 125000,
      "description_snippet": "First 200 chars of description...",
      "position": 1,
      "step0_action": "process_new"
    }
  ]
}
```

3. **⚠️ MANDATORY VERIFICATION PROTOCOL:**
   - Present the FULL title list to Jon
   - Total video count, duration range (shortest/longest), channel distribution
   - Any videos flagged as unavailable/private
   - Jon opens the playlist in YouTube UI and compares — every title must match
   - If ANY title doesn't match what Jon sees → **FULL STOP**, investigate redirect
   - Only after Jon says "these are my videos" → set `verified_by_jon: true`

**Gate:** `verified_by_jon: true` in inventory. No processing without this.

### Title = Source of Truth
Video IDs can change when playlists are reorganized/rebuilt. YouTube reassigns IDs. From this point forward:
- **Title matching** determines if a video has been processed, NOT ID alone
- Use fuzzy matching (threshold 80%) for title comparison
- If IDs change but titles match → update registry, preserve assets

<registry-update>
Record `title`, `duration`, `upload_date`, `channel`, `view_count`, `file_paths.info_json` for each video.
</registry-update>

</step>

---

<step id="2" name="Transcript Download" phase="A">

<meta>
  <input>Video IDs from Step 0 plan (process_new and resume only)</input>
  <output>Timestamped transcript files</output>
  <models>yt-dlp + text processing (FREE). Whisper API fallback (~$0.01, rare).</models>
  <gate>All transcripts downloaded. Transcripts >30KB flagged for chunking. Quality-checked.</gate>
</meta>

## Step 2: Transcript Download

### Corrected Transcript Fallback Order

**Manual/human-created → Auto-generated → Whisper API**

Manual subtitles are highest quality (human-created). Auto-generated are good quality and almost always available. Whisper API is expensive and only used when both subtitle sources fail.

```bash
yt-dlp \
  --write-sub \
  --write-auto-sub \
  --sub-lang en \
  --sub-format json3 \
  --skip-download \
  -o "transcripts/%(id)s" \
  "{video_url}"
```

- `--write-sub` downloads manual/human-created subtitles if available
- `--write-auto-sub` downloads auto-generated subtitles as fallback
- yt-dlp automatically prefers manual subs when both exist
- `json3` format provides superior timestamp precision compared to VTT

### Post-Download Processing

1. **Detect subtitle source:** Check if manual or auto-generated (via info.json markers)
2. **Convert to timestamped text format:**
   ```
   [00:00:15] Speaker introduces the topic of AI agents
   [00:00:32] First key concept: autonomous decision making
   [00:01:05] Demo begins - screen sharing starts
   ```
3. **Quality check:**
   - Word count < 100 for video > 5 min → flag as likely failed
   - Auto-generated confidence < 70% → flag for Whisper re-transcription
4. **⚠️ CHECK TRANSCRIPT SIZE** (see [Chunking Protocol](#chunking-protocol)):
   - If transcript > 30KB → mark for chunked processing in Steps 4 and 6
5. **Whisper fallback (only if both subtitle sources fail):**
   ```bash
   yt-dlp -x --audio-format mp3 -o "audio/%(id)s.mp3" "{video_url}"
   ```
   - Process through Whisper API
   - Delete audio file after transcription

<registry-update>
Record `transcript_path` and `transcript_source` (manual_sub, auto_sub, or whisper). Flag if >30KB.
</registry-update>

</step>

---

<step id="3" name="LLM Categorization (Combined Approval Gate)" phase="A">

<meta>
  <input>All transcripts from Step 2 + reused transcripts from Step 0</input>
  <output>Category assignments + first category sample output</output>
  <models>Gemini Flash (FREE — categorization doesn't need expensive models)</models>
  <gate>Jon approves BOTH categories AND processing quality in ONE round</gate>
</meta>

## Step 3: LLM Categorization (Combined Approval Gate)

### Categorization Process

1. Feed all video titles + first 500 chars of each transcript to LLM
2. Generate 7-12 thematic categories with:
   - Category name
   - Category description (1-2 sentences)
   - Assigned video count (minimum 3, maximum 10 per category)
   - Representative video titles (2-3 per category)
   - Every video in exactly one category (including reused videos from Step 0)

### Combined Approval Gate

1. Present proposed categories to Jon
2. SIMULTANEOUSLY process one video completely through Steps 4-8 as a quality proof
3. Present to Jon: "Here are the proposed categories AND here's the full output for one video (enhanced transcript + report + infographic). Categories + quality acceptable?"
4. Jon approves or redirects

**This reduces approval rounds from 2 to 1.**

### Category Drift — Handling Uncategorized Videos

When a new video doesn't match any existing category at >60% confidence:
1. **Flag it:** Mark with `"category": "uncategorized"`
2. **Notify Jon:** "New video '{title}' doesn't fit existing categories. Options: (a) create new category, (b) assign to closest match: {suggestion}"
3. **Don't block:** Video is fully processed individually — all outputs exist. It just doesn't contribute to any category compilation yet.
4. **Auto-create threshold:** If 3+ videos accumulate as "uncategorized" with similar themes, suggest a new category automatically.

<registry-update>
Record `category` assignment for each video. Log approval timestamp and Jon's response.
</registry-update>

</step>

</phase>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--            PHASE B: PER-CATEGORY DEEP PROCESSING               -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<phase id="B" name="Per-Category Deep Processing">

<step id="4" name="Timestamp Map Generation" phase="B">

<meta>
  <input>Timestamped transcript for one video</input>
  <output>timestamp-maps/{id}-map.json</output>
  <models>Gemini Flash (FREE — transcript analysis, no vision needed)</models>
  <gate>Every video has a timestamp map with ≥5 insights. Videos with 0 vision sections skip Step 5.</gate>
</meta>

## Step 4: Timestamp Map Generation

The LLM analyzes the FULL transcript BEFORE any video download and identifies every section containing material worth capturing.

### ⚠️ Large Transcript Handling
If transcript > 30KB, use the chunking protocol. Split into overlapping chunks, process each, merge results, deduplicate sections.

### Four Capture Categories

1. **Insights** — New information, revelations, "aha" moments
2. **Takeaways** — Lessons learned, principles, wisdom
3. **Key Moments** — Demos, code on screen, UI reveals, architecture diagrams, tool usage
4. **Actionable Items** — Specific things Jon can implement today

<prompt name="timestamp-map-generation">
```
Analyze this timestamped transcript. Identify EVERY section containing:
1. Insights (new information, revelations)
2. Takeaways (lessons, principles)
3. Key Moments (demos, code, UI, diagrams — visible screen content)
4. Actionable Items (specific implementable steps)

For each section provide:
- start_timestamp (HH:MM:SS)
- end_timestamp (HH:MM:SS)
- type (insight / takeaway / key_moment / actionable)
- topic (brief description of what this section covers)
- summary (1-2 sentences capturing the substance)
- needs_vision (true/false — would seeing the screen add value?)
- vision_density (if needs_vision: "high" / "medium" / "low")
- importance (high / medium / low)

Vision density guidelines:
- "high" (2-3 fps): Code, terminal output, rapidly changing UI
- "medium" (1 fps): Slides, diagrams, static UI demonstrations
- "low" (0.5 fps): Talking head with occasional screen share

Not every section needs vision. Talking-head philosophy = no vision needed.
Code on screen, UI demo, diagram = vision needed.

Be THOROUGH. This map determines what gets captured. Missing a key moment
means it's lost from the final knowledge base.

MINIMUM: 5 key insights per video. If you cannot identify 5, flag the video.

Transcript:
{timestamped_transcript}
```
</prompt>

### Frame Budget Caps

```
Video < 5 min:                                  max 50 frames
Video 5-30 min:                                 max 150 frames
Video > 30 min:                                 max 200 frames
Video > 60 min, < 3 vision sections (podcast):  max 10 frames
Video > 60 min, > 10 vision sections (tutorial): max 300 frames
```

If the timestamp map's section densities would exceed the budget, reduce `vision_density` on lower-importance sections until within budget.

### Output Format

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "total_duration": "00:12:34",
  "frame_budget": 150,
  "estimated_frames": 87,
  "sections": [
    {
      "start": "00:01:30",
      "end": "00:04:15",
      "type": "key_moment",
      "topic": "Live coding demo — building the agent",
      "summary": "Speaker demonstrates state management using JSON checkpoints in VS Code",
      "needs_vision": true,
      "vision_density": "high",
      "importance": "high",
      "key_insights": [
        {
          "timestamp": "00:02:10",
          "insight": "Novel approach to state management using JSON checkpoints"
        }
      ]
    }
  ],
  "stats": {
    "total_sections": 12,
    "vision_sections": 5,
    "insights": 4,
    "takeaways": 3,
    "key_moments": 3,
    "actionable_items": 2
  }
}
```

<registry-update>
Record `timestamp_map_path` and `vision_sections_count` for each video.
</registry-update>

</step>

---

<step id="5" name="Smart Frame Capture (Single-Pass)" phase="B">

<meta>
  <input>timestamp-maps/{id}-map.json + downloaded video file</input>
  <output>frames/{id}/frame_NNNN_tNNNN.jpg + frames/{id}/frame_manifest.json</output>
  <models>yt-dlp (download) + ffmpeg (single-pass extract) — FREE</models>
  <gate>Frame count matches estimate from timestamp map. Each frame traceable to section + timestamp. Video file deleted.</gate>
</meta>

## Step 5: Smart Frame Capture (Single-Pass)

### Step 5a: Download Video

```bash
yt-dlp \
  -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
  --merge-output-format mp4 \
  -o "downloads/%(id)s.%(ext)s" \
  "{video_url}"
```

**Default 720p.** If Step 6 produces LOW confidence on code blocks, re-download at 1080p and re-extract just those sections.

**For videos with 0 vision sections:** Skip download entirely. No frames needed.

**Storage note:** If external drive available, download to external drive path:
```bash
-o "/Volumes/New Volume/PVD-Workspace/youtube-pipeline/downloads/%(id)s.%(ext)s"
```

### Step 5b: Single-Pass Frame Extraction

Build the COMPLETE extraction plan from the timestamp map, then execute in ONE ffmpeg pass:

```bash
ffmpeg -i "downloads/{ID}.mp4" \
  -vf "select='between(t\,90\,255)*not(mod(n\,15))+between(t\,420\,510)*not(mod(n\,30))',setpts=N/FRAME_RATE/TB" \
  -vsync vfr \
  -q:v 2 \
  "frames/{ID}/frame_%04d.jpg"
```

- `between(t,90,255)` = timestamps 1:30 to 4:15 in seconds
- `not(mod(n,15))` ≈ 2fps for 30fps source
- `not(mod(n,30))` ≈ 1fps for 30fps source
- `-vsync vfr` = variable frame rate (only selected frames)
- `-q:v 2` = high quality JPEG

**This decodes the stream ONCE.** For 5 vision sections, this is 5x faster than separate invocations.

### Step 5c: Frame Naming & Manifest

```
frames/{video_id}/
├── frame_0001_t0090.jpg
├── frame_0002_t0091.jpg
├── ...
├── frame_0087_t0510.jpg
└── frame_manifest.json
```

### Step 5d: Video File Deletion

**CRITICAL:** Delete video file IMMEDIATELY after frame extraction:
```bash
rm -f "downloads/{video_id}.*"
```

<registry-update>
Record `frames_directory` and `frames_extracted` count. Confirm video file deletion.
</registry-update>

</step>

---

<step id="6" name="Enhanced Transcript Synthesis" phase="B">

<meta>
  <input>Original timestamped transcript + captured frames + timestamp map</input>
  <output>enhanced-transcripts/{id}-enhanced.md</output>
  <models>Gemini Pro Vision (FREE for frame analysis) + Opus 4.6 (for synthesis merge)</models>
  <gate>ALL mapped sections covered. Every vision section has frame descriptions merged. "Synthesized Knowledge" present for every section. No section left as raw transcript when frames were available.</gate>
</meta>

## Step 6: Enhanced Transcript Synthesis

**THIS IS THE CORE STEP. The source of truth for the entire library.**

### ⚠️ Large Transcript Handling
If transcript > 30KB, use the chunking protocol. Process sections individually, then merge. Do NOT send the entire transcript in one prompt — this causes stub/placeholder output.

### Two Processing Modes

**Mode A — Full Synthesis (videos WITH frames):**

For each section in the timestamp map:
1. Pull the original transcript text for that time range
2. If `needs_vision: true` AND frames exist → feed frames to vision model with transcript context
3. Vision model describes EVERYTHING visible that adds to or differs from what was said
4. **Synthesize:** Merge What Was Said + What Was Shown + What was shown but NOT said
5. Link specific frames as references

<prompt name="vision-analysis-per-section">
```
You are analyzing frames from a YouTube video alongside the transcript.

SECTION: {type} — "{topic}"
TIMESTAMP: {start} → {end}
TRANSCRIPT FOR THIS SECTION:
{transcript_text}

FRAMES: [attached — captured during this section]

Describe EVERYTHING visible that adds to or differs from the transcript:
- Code on screen (transcribe EXACTLY, character by character)
- UI elements, settings, configurations
- Diagrams, architecture, workflows
- Terminal output, error messages
- URLs, file paths, tool versions
- Anything the speaker shows but doesn't verbally explain

Be exhaustive. This becomes the permanent knowledge record.
```
</prompt>

**Mode B — Transcript Enhancement (videos WITHOUT frames):**

LLM re-structures and enriches the raw transcript with better organization, extracted knowledge, and clearer sections. No vision data, but still a significant upgrade from raw auto-captions. Knowledge coverage: ~60%.

### Enhanced Transcript Format

```markdown
# Enhanced Transcript: {EXACT VIDEO TITLE}

**Video ID:** {id}
**Duration:** {duration}
**Channel:** {channel}
**Upload Date:** {upload_date}
**Category:** {category}
**Transcript Source:** {manual_sub / auto_sub / whisper}
**Enhancement Mode:** {Vision+Transcript / Transcript-Only}
**Knowledge Coverage:** ~{95/60}%
**Processing Date:** {ISO-8601}

---

## Section 1: {topic} [{start} → {end}]
**Type:** {insight / takeaway / key_moment / actionable}
**Importance:** {high / medium / low}

### What Was Said:
{cleaned transcript text for this section — full content, not summarized}

### What Was Shown: ← (vision-enhanced sections only)
{exhaustive description of visual content from frames}

> ⚠️ VISION TRANSCRIPTION — Code Block (verify against frame_NNNN_tNNNN.jpg)
> Confidence: {HIGH / MEDIUM / LOW}
```python
{exact code transcribed character by character from frames}
```

- **UI:** {description of interface elements, settings, buttons visible}
- **Config:** {parameters, settings, file paths visible}
- **Diagram:** {description of any visual diagrams, architecture, flowcharts}
- **Terminal:** {exact terminal output if visible}

### Synthesized Knowledge:
{THE CRITICAL MERGE — combined understanding from audio + visual:
 - What was explained verbally AND demonstrated visually
 - What was SHOWN but NOT verbally explained (gaps filled by vision)
 - What was SAID but NOT shown (context that exists only in audio)
 - The unified understanding that captures ~95% of the video's value}

### Key Frame References:
- `frame_0012_t0102.jpg` — {what it shows and why it matters}
- `frame_0015_t0105.jpg` — {what it shows and why it matters}

---

## Section 2: {topic} [{start} → {end}]
{repeat for each section in timestamp map}

---

## Unstructured Sections
{transcript segments BETWEEN mapped sections — included for completeness
but not vision-enhanced. These cover transitions, small talk, intros/outros.}

---

## Metadata
- Original transcript word count: {count}
- Enhanced sections: {count}
- Vision-enhanced sections: {count}
- Frames analyzed: {count}
- Confidence distribution: {X HIGH, Y MEDIUM, Z LOW}
- Enhancement method: {Mode A / Mode B}
```

### Vision Output Validation Protocol

1. **Always include frame reference** with every vision transcription
2. **Confidence scoring** for each vision block:
   - `HIGH` — Clear screen, standard code/text, high resolution frames
   - `MEDIUM` — Partial occlusion, small text, unusual fonts
   - `LOW` — Blurry, rapid motion, heavily stylized text
3. **For code blocks:** Cross-reference syntax (does it parse?). Flag unusual character sequences.
4. **For LOW confidence code at 720p:** Flag for 1080p re-download and re-extraction of that specific section only.
5. **For terminal/command output:** Validate command syntax where possible.

<registry-update>
Record `enhanced_transcript_path`. Update step status to complete. Flag confidence issues.
</registry-update>

</step>

---

<step id="7" name="Intelligence Report" phase="B">

<meta>
  <input>Enhanced transcript from Step 6</input>
  <output>reports/{id}-report.md</output>
  <models>Opus 4.6 (highest intelligence for analysis)</models>
  <gate>≥5 distinct insights, ≥3 actionable items, ≥3 takeaways, all with timestamps. Dual score present.</gate>
</meta>

## Step 7: Intelligence Report

Built FROM the enhanced transcript (not raw transcript).

### Report Structure

```markdown
# Intelligence Report: {EXACT VIDEO TITLE}

**Video ID:** {id} | **Duration:** {duration}
**Channel:** {channel} | **Upload Date:** {upload_date} | **Views:** {view_count}
**Category:** {category}
**Report Generated:** {date} | **Knowledge Coverage:** ~{95/60}%
**Frames Analyzed:** {count}

## Executive Summary
{2-3 sentences — the video's core value proposition}

## Key Insights (minimum 5 required — cite timestamps)

### Insight 1: {Title}
**Timestamp:** [{HH:MM:SS}]
**Description:** {detailed explanation}
**Applicability:** {how this applies to Jon's projects/business}

## Actionable Items (minimum 3 — things Jon can implement)
1. [{HH:MM:SS}] {Specific action} — **Implementation:** {brief how-to}

## Takeaways (lessons and principles)
1. [{HH:MM:SS}] {Takeaway with context}

## Key Moments (with frame references)
1. [{HH:MM:SS}] {What happened} — See: `frame_NNNN_tNNNN.jpg`

## Tools & Technologies
| Tool | Context | How Used | Relevant To |

## Architecture / Workflows
{diagrams, flows, system designs shown or described}

## Code / Prompts / Configs
{exact transcriptions from enhanced transcript}

## Scoring
| Metric | Score | Justification |
|---|---|---|
| Pulse Readiness | {X}/10 | {Why} |
| Jon Impact | {X}/10 | {Why} |
| **Weighted Score** | **{X.X}/10** | **(Pulse × 0.4) + (Jon × 0.6)** |

## Cross-References
{Other videos in the pipeline that relate}
```

### Dual Scoring System

**Pulse Readiness Score (1-10):** How ready for immediate real-world application?
- 8-10: Ready to implement today
- 5-7: Needs some adaptation
- 1-4: Theoretical/conceptual

**Jon Impact Score (1-10):** How relevant to Jon's specific projects and business?
- 8-10: Directly applicable to current projects (RLA Forge, Sabbath Echo, WreckPix, etc.)
- 5-7: Generally useful for Jon's tech stack
- 1-4: Interesting but tangential

**Weighted Score:** `(Pulse × 0.4) + (Jon Impact × 0.6)`

**Minimum threshold:** ≥5 distinct insights, ≥3 actionable items, ≥3 takeaways.

<registry-update>
Record `report_path`, `pulse_readiness_score`, `jon_impact_score`, `weighted_score`.
</registry-update>

</step>

---

<step id="8" name="Premium Video Infographic" phase="B">

<meta>
  <input>Intelligence report from Step 7 + key frames from Step 5</input>
  <output>infographics/{id}-infographic.png (1200×800px)</output>
  <models>Nano Banana Pro / Gemini 3 Pro Image (FREE)</models>
  <gate>Premium design standard met. Not a text card. Readable at 50% zoom. Score badge color-coded.</gate>
</meta>

## Step 8: Premium Video Infographic

**EVERY video gets a premium infographic. No "lean cards." No text walls.**

<prompt name="nano-banana-pro-infographic">
```
Create a premium, visually rich dark-themed infographic (1200x800) that captures 
the complete intelligence from a YouTube video analysis.

TITLE: "{title}"
SCORE: {weighted_score}/10
CATEGORY: {category}
DURATION: {duration}

TOP INSIGHTS: {top 3-5 insights}
ACTIONABLE ITEMS: {top 2-3 actions}
KEY MOMENT HIGHLIGHT: "{most important key moment}"
TOOLS/TECH: {tool_list}

MANDATORY DESIGN REQUIREMENTS:
- Dark gradient background (#0a0a0f to #12121a)
- Bold title at top with category-specific accent color
- Score badge — PROMINENT, color-coded:
  - Green (#10b981) for score ≥ 8
  - Amber (#f59e0b) for score ≥ 6
  - Red (#ef4444) for score < 6
- Insight cards with DISTINCT ICONS per insight
- Actionable items in a "DO THIS" zone with green accent
- Key moment highlight box with purple (#8b5cf6) accent
- Tool/tech shown as branded pill badges at bottom
- Color-coded sections:
  - Insights = cyan (#06b6d4)
  - Actions = green (#10b981)
  - Key moments = purple (#8b5cf6)
  - Tools = amber (#f59e0b)
- "⚡ Pulse Vibe Daily" watermark bottom-right
- Modern tech dashboard aesthetic — premium newsletter quality
- NOT a text card. NOT a wall of text.
- Must include visual DESIGN ELEMENTS: icons, badges, cards, dividers, gradients
```
</prompt>

### Rate Limiting (Adaptive Exponential Backoff)

```
attempt = 1
max_attempts = 5
while attempt <= max_attempts:
    response = generate_infographic(report_data)
    if response.status == "rate_limited":
        wait_time = min(2^attempt + random(0, 1), 60)
        sleep(wait_time)
        attempt += 1
    elif response.status == "success":
        break
```

<registry-update>
Record `infographic_path`. Set video `status` → `"complete"` if all Steps 0-8 done.
</registry-update>

</step>

---

<step id="9" name="Category Compilation + Category Infographic" phase="B">

<meta>
  <input>All enhanced transcripts + reports + infographics from this category</input>
  <output>playlists/{playlist_id}/categories/{category_slug}/compilation.md + category-infographic.png</output>
  <models>Opus 4.6 (synthesis) + Nano Banana Pro (infographic)</models>
  <gate>Jon reviews the complete category output before proceeding to next category.</gate>
</meta>

## Step 9: Category Compilation + Category Infographic

### Compilation Document Structure

```markdown
# Category Compilation: {Category Name}

**Playlist:** {Playlist Title}
**Videos in Category:** {count}
**Average Weighted Score:** {X.X}/10
**Generated:** {date}

## Category Overview
{2-3 paragraph synthesis}

## Videos (Ranked by Weighted Score)
### 1. {Video Title} — Score: {X.X}/10
{Summary + Top 3 Insights + Link to enhanced transcript}

## Cross-Video Insights
{Patterns that emerge from seeing multiple videos together}

## Unified Tool/Tech Landscape
{All tools across category with frequency + context}

## Category Action Items
{Consolidated, deduplicated, prioritized takeaways}

## Cross-Category Connections
{Themes that bridge this category with others}
```

### Version Archival for Categories

Categories are versioned. Each compilation creates a new version:
```
categories/{category_slug}/
├── v1/
│   ├── compilation.md
│   ├── infographic.png
│   └── metadata.json
├── v2/
│   └── ...
└── current -> v2/        # Symlink to latest
```

- Previous versions are NEVER deleted
- Every 3rd version = full recompile from all source transcripts (clean slate)
- Other versions = incremental (previous + new enhanced transcripts)

### Category Recompilation Triggers

| Trigger | Condition |
|---|---|
| Threshold | Category gets 3+ new videos since last compile |
| Manual | Jon requests category refresh |
| Full recompile | Every 3rd version (v3, v6, v9...) |

<registry-update>
Record category compilation version, path, and date. Update category status in playlist state.
</registry-update>

</step>

</phase>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--              PHASE C: PLAYLIST-LEVEL SYNTHESIS                 -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<phase id="C" name="Playlist-Level Synthesis">

<step id="10" name="Cross-Category Master Compilation" phase="C">

<meta>
  <input>All category compilations from Step 9</input>
  <output>playlists/{playlist_id}/master-compilation.md</output>
  <models>Opus 4.6</models>
  <gate>Only begins after ALL categories processed and Jon-approved.</gate>
  <prerequisite>All categories from Step 9 complete and Jon-approved.</prerequisite>
</meta>

## Step 10: Cross-Category Master Compilation

Merge all category compilations into a master document:
- Playlist-level executive summary
- Category rankings by average weighted score
- Cross-category theme analysis
- Top 10 insights across the entire playlist
- Master action item list (deduplicated and prioritized)
- Meta-analysis (what topics are over/under-represented?)

### Master Compilation Versioning

```
compilations/
├── v1/
│   ├── master-report.md
│   ├── master-infographic.png
│   ├── podcast-script.md
│   └── metadata.json
├── v2/
│   └── ...
└── current -> v1/
```

<registry-update>
Record master compilation version, path, and timestamp. Update playlist-level status.
</registry-update>

</step>

---

<step id="11" name="NotebookLM Integration Phase" phase="C">

<meta>
  <input>All enhanced transcripts from Step 6, category compilations from Step 9</input>
  <output>NotebookLM notebook with audio podcast, infographic deck, slide deck, deep research reports</output>
  <models>Google NotebookLM (Pro account: navigata1@gmail.com)</models>
  <gate>Notebook created, enhanced transcripts uploaded, all outputs generated.</gate>
  <prerequisite>This is a MANDATORY phase for any playlist completing Phase C.</prerequisite>
</meta>

## Step 11: NotebookLM Integration Phase

> **This is a MANDATORY phase for any playlist completing Phase C.**
> NotebookLM and the PVD pipeline are COMPLEMENTARY, not replacements.

### What NotebookLM Adds (That PVD Pipeline Doesn't)

| Capability | PVD Pipeline | NotebookLM |
|---|---|---|
| Single shareable PNG infographic | ✅ | ❌ |
| Multi-panel infographic deck | ❌ | ✅ |
| Audio podcast (AI-generated voices) | ❌ | ✅ |
| Slide deck | ❌ | ✅ |
| Deep Research (50+ auto-discovered sources) | ❌ | ✅ |
| Infinite context window (no token limit) | ❌ | ✅ |
| Intelligence reports with scoring | ✅ | ❌ |
| Vision-enhanced transcripts | ✅ | ❌ |

### Dual Infographic Standard

- **PVD pipeline** = single shareable PNG (social media / Telegram / quick reference)
- **NotebookLM** = multi-panel deck (presentations / deep content / client delivery)
- **They're complementary. KEEP BOTH.**

### NotebookLM Process

1. **Create a topic-specific notebook** — one per category or for the full playlist
2. **Upload enhanced transcripts** as sources (NOT raw transcripts)
3. **Generate outputs:**
   - Audio Overview (podcast) — NotebookLM ONLY handles audio podcasts
   - Infographic deck (multi-panel)
   - Slide deck
   - Deep Research report (auto-discovers ~50 additional sources)
4. **Save notebook ID** in pipeline metadata for future reference

### Audio Podcast Rule

- **Audio podcasts = NotebookLM only** — these are the AI-generated conversational summaries
- **PVD pipeline generates VIDEO/faceless scripts** — for YouTube Shorts, TikTok, etc.
- These are different products. Do not conflate them.

### NotebookLM Prompts (from context/prompt-frameworks)

Use the established prompt library for NotebookLM:
- Study Guide / Learning Path → for playlist-level knowledge synthesis
- Technical Architecture Review → for code-heavy categories
- Competitive Analysis → for market-focused categories
- Action Item Extractor → for business categories
- Social Media Content Pack → feeds into Step 12

<registry-update>
Record NotebookLM notebook ID, generated output types, and paths to downloaded assets.
</registry-update>

</step>

---

<step id="12" name="Content Deliverables Assembly" phase="C">

<meta>
  <input>Master compilation, category compilations, NotebookLM outputs, all infographics</input>
  <output>Podcast scripts, slide decks, playlist infographic, platform content drafts (NOT pushed yet)</output>
  <models>Opus 4.6 + Nano Banana Pro (FREE)</models>
  <gate>All deliverables assembled and ready for review. Content package complete. NO EXTERNAL PUSH — that's Step 14.</gate>
  <prerequisite>Steps 10-11 complete.</prerequisite>
</meta>

## Step 12: Content Deliverables Assembly

> **⚠️ THIS STEP PREPARES DELIVERABLES. IT DOES NOT PUSH CONTENT EXTERNALLY.**
> Content distribution to social platforms happens ONLY in Step 14, AFTER the full pipeline (Steps 0-13) is complete and Jon has reviewed the content package.

This step assembles all the content artifacts from the completed pipeline into a distribution-ready package. Think of it as staging — everything gets built and formatted, but nothing leaves the building until Step 14's verification gate passes.

### 12a: Podcast Script

**Model:** Opus 4.6

```markdown
Structure:
- Cold open: Hook with the single most impactful insight
- Introduction: What this playlist covers and why it matters
- Category segments: One segment per category, hitting top insights
- Deep dive: 2-3 highest-scoring videos get extended discussion
- Actionable close: Top 5 things to do after listening
- Target length: 15-25 minutes speaking time (1500-2500 words)
```

### 12b: Slide Deck

- Title slide
- One overview slide per category
- One slide per top-10 insight
- Closing slide with action items
- Use infographics as visual elements
- Dark theme, arrow-key navigation

### 12c: Cross-Platform Content Drafts

For each completed category or playlist, **draft** content for 8 platforms. These are DRAFTS — they get finalized and pushed in Step 14.

| Platform | Format | Length |
|---|---|---|
| X (Twitter) | Thread (5-7 tweets) | 280 chars each |
| LinkedIn | Professional post | 1300 chars |
| Instagram | Carousel (10 slides) | Image + caption |
| TikTok | Script (60s) | 150-200 words |
| YouTube Shorts | Script (45s) | 100-150 words |
| Telegram | Post with infographic | 500-1000 chars |
| Snapchat | Story (5 snaps) | Visual + overlay text |
| Facebook | Post with link | 500 chars |

**Content drafts live in:** `context/content-drops/{drop-name}/`

### 12d: Playlist-Level Infographic

**Tool:** Nano Banana Pro (1200×800px)

Top-level visual summary — same premium design standard:
- Total videos processed, total insights extracted
- Category distribution breakdown
- Top 5 insights across all categories
- Highest-scoring videos highlighted

<registry-update>
Record all deliverable paths (podcast script, slide deck, playlist infographic, content draft directory). Mark Step 12 as complete. Content package is staged, NOT distributed.
</registry-update>

</step>

---

<step id="13" name="Post-Pipeline Cleanup" phase="C">

<meta>
  <input>All completed pipeline outputs from Steps 0-12</input>
  <output>Reclaimed storage. Retained source-of-truth files only.</output>
  <models>Local scripts (FREE)</models>
  <gate>All source-of-truth files validated before ANY deletion. Missing outputs = skip cleanup for that video.</gate>
  <prerequisite>Runs AFTER all playlist processing is complete (after Step 12).</prerequisite>
</meta>

## Step 13: Post-Pipeline Cleanup

### Source of Truth Validation

Before deleting ANY files for a video, confirm ALL outputs exist:
```
✅ Enhanced transcript: enhanced-transcripts/{id}-enhanced.md
✅ Intelligence report: reports/{id}-report.md
✅ Infographic: infographics/{id}-infographic.png
✅ Registry entry status: "complete"
```

**If ANY output is missing → SKIP cleanup for that video, log warning.**

### Cleanup Operations (Per Video)

1. **Delete downloaded video files** (catches Step 5d stragglers)
2. **Delete raw timestamped transcript** (enhanced version is the source of truth)
3. **Delete timestamp map** (captured in enhanced transcript structure)
4. **Delete frame manifest**
5. **Delete audio files** (Whisper fallback)
6. **Tiered frame deletion:**
   ```
   IF all vision sections have HIGH confidence → Delete entire frames/ directory
   IF any section has MEDIUM or LOW confidence:
     → Move referenced frames to archive/{id}/
     → Delete remaining frames
     → Set retention_expiry = cleanup_date + 30 days
   ```

### Files NEVER Deleted

| File | Reason |
|---|---|
| `{id}-enhanced.md` | Source of truth |
| `{id}-report.md` | Analysis layer |
| `{id}-infographic.png` | Visual deliverable |
| `{id}.info.json` | Metadata |
| `global_processed_registry.json` | System backbone |
| All Phase C outputs | Compilations, podcast, slides, infographics |
| All Step 12 deliverables | Content package (staged for Step 14) |

### Storage Impact (per 15-min 720p video)

| File Type | Typical Size | Action |
|---|---|---|
| Downloaded video | 100-250 MB | DELETE |
| Extracted frames | 15-40 MB | MOSTLY DELETE |
| Raw transcript | 5-15 KB | DELETE |
| **Total reclaimed** | **~125-310 MB** | — |
| **Total retained** | **~235-580 KB** | Enhanced transcript + report + infographic + info.json |

**50-video playlist:** Reclaim 6-15 GB → retain ~30-50 MB = **99%+ storage reduction**

<registry-update>
Mark cleanup complete for each video. Record storage reclaimed. Flag any videos where cleanup was skipped due to missing outputs.
</registry-update>

</step>

</phase>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--         PHASE D: CONTENT DISTRIBUTION (POST-PIPELINE)          -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<phase id="D" name="Content Distribution (POST-PIPELINE)">

<step id="14" name="Content Distribution &amp; External Push" phase="D">

<meta>
  <input>ALL completed outputs from Steps 0-13 — the full content package</input>
  <output>Published content across 8 platforms + Anti-gravity/Remotion video</output>
  <models>Opus 4.6 (finalization) + Remotion (video rendering)</models>
  <gate>VERIFICATION: All Steps 0-13 marked complete in registry. Jon reviews content package before ANY external push.</gate>
  <prerequisite>Steps 0-13 ALL complete. No partial pushes. No exceptions.</prerequisite>
</meta>

## Step 14: Content Distribution & External Push

> **⚠️ THIS STEP ONLY TRIGGERS AFTER THE FULL PIPELINE IS DONE.**
> The value of PVD's content is the COMPILED, SYNTHESIZED intelligence — cross-video insights, patterns, gaps identified, Pulse's own intelligent analysis layer on top. **NOT individual video reposts.**
>
> No content leaves the building until Steps 0-13 are ALL complete and Jon has reviewed the assembled package.

This is the handoff point to the content pipeline. Step 12 assembled all deliverables; Step 14 finalizes, reviews, and pushes them to the world.

### Verification Gate (MANDATORY)

Before ANY external push:

1. **Pipeline Completion Check:**
   - All Steps 0-13 marked complete in registry
   - No outstanding stubs or failed processing
   - All category compilations finalized
   - Master compilation reviewed
   - NotebookLM outputs generated

2. **Content Package Review:**
   - Master compilation (cross-category synthesis) — complete and coherent
   - Playlist-level infographic — premium quality
   - NotebookLM podcast audio — generated and reviewed
   - NotebookLM slide deck + multi-panel infographic deck — ready
   - Category compilations with cross-video insights — all categories covered
   - Pulse's own gap analysis and intelligent insights layer — added on top
   - Per-video infographics — supporting assets, not the main product

3. **Jon Approval:**
   - Content package presented to Jon for review
   - Jon explicitly approves the package
   - Any corrections or additions made before distribution
   - **THEN and ONLY THEN** → proceed to push

### 14a: 8-Platform Distribution

Push the compiled content package (NOT individual video reposts) to all platforms:

| Platform | Format | Length | Content Source |
|---|---|---|---|
| X (Twitter) | Thread (5-7 tweets) | 280 chars each | Cross-video synthesis + key insights |
| LinkedIn | Professional post | 1300 chars | Master compilation highlights |
| Instagram | Carousel (10 slides) | Image + caption | Category infographics + playlist infographic |
| TikTok | Script (60s) | 150-200 words | Top insights, scripted for vertical |
| YouTube Shorts | Script (45s) | 100-150 words | Highest-scoring video highlights |
| Telegram | Post with infographic | 500-1000 chars | Playlist infographic + key takeaways |
| Snapchat | Story (5 snaps) | Visual + overlay text | Visual insights from infographic deck |
| Facebook | Post with link | 500 chars | Master compilation summary |

**Each platform gets format-optimized content.** Not copy-paste. Not reposts. The compiled intelligence, formatted for each platform's native experience.

**Content drops finalized in:** `context/content-drops/{drop-name}/`

### 14b: Anti-gravity / Remotion Video Creation

When applicable, pipeline data feeds into programmatic video creation:

- **Remotion skill:** Claude Code can generate motion graphics from pipeline data
- **Text-to-Video:** Prompt Claude to create product demos, social ads from insights
- **Asset Extraction:** Use captured frames + infographics as video assets
- **Brand-aligned:** Use PVD brand guidelines (dark theme, accent colors)

Workflow: Enhanced transcript → Key insights → Video script → Remotion code → Render

### 14c: Content Pipeline Handoff

This step IS the handoff to PVD's broader content pipeline:
- Pipeline outputs become raw material for ongoing content creation
- Category compilations feed recurring content themes
- NotebookLM podcasts become standalone content products
- Infographic decks become presentation assets
- Gap analysis identifies topics for future content

<registry-update>
Record distribution date, platforms pushed to, content drop paths, Remotion video path (if applicable). Mark playlist as "distributed." This is the final pipeline step.
</registry-update>

</step>

</phase>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                         SYSTEMS                                -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<systems>

## Pipeline Systems

<global-registry>

### Global Video Registry

The registry is the foundational system enabling cross-playlist deduplication, incremental updates, and processing state recovery.

#### Registry File: `global_processed_registry.json`

```json
{
  "registryVersion": 1,
  "lastUpdated": "2026-02-20T10:00:00Z",
  "total_videos": 112,
  "videos": {
    "VIDEO_ID_HERE": {
      "title": "Exact Video Title",
      "duration": 1800,
      "playlist": "Source Playlist Name",
      "pipeline_version": "v5.0",
      "added": "ISO-8601",
      "processedAt": "ISO-8601",
      "sourcePlaylist": "playlist-name",
      "assetsPath": "path/to/assets/",
      "hasEnhancedTranscript": true,
      "hasReport": true,
      "hasInfographic": true,
      "hasFrames": false,
      "qualityTier": "v5",
      "steps": {
        "transcript": true,
        "frames": true,
        "enhanced": true,
        "report": true,
        "infographic": true
      }
    }
  }
}
```

#### Registry Rules

1. **Video ID is the primary key.** YouTube video IDs are globally unique.
2. **Update after each processing step.** Don't wait until completion.
3. **Never delete registry entries.** Storage is cheap; reprocessing is not.
4. **Playlist assignments accumulate.** A single video can belong to unlimited playlists.
5. **Title stored alongside ID** — enables recovery if IDs change during playlist reorganization.

</global-registry>

---

<cross-playlist-dedup>

### Cross-Playlist Deduplication Protocol

#### Scenario: Playlist B Contains Videos Already Processed in Playlist A

```
Playlist A (already processed):
├── Video 1 ✅ | Video 2 ✅ | Video 3 ✅ | Video 4 ✅

Playlist B (new):
├── Video 2 ← DUPLICATE (reuse) | Video 3 ← DUPLICATE (reuse)
├── Video 5 ← NEW | Video 6 ← NEW
```

#### Flow

1. **Step 0:** Registry check → Videos 2,3 = reuse; Videos 5,6 = process_new
2. **Step 1:** Extract Playlist B inventory
3. **Step 2:** Download transcripts for Videos 5 and 6 ONLY
4. **Step 3:** Categorize ALL 4 videos (using existing transcripts for 2 and 3)
5. **Steps 4-8:** Process Videos 5 and 6 only
6. **For Videos 2 and 3:** Symlink existing outputs into Playlist B's category folders
7. **Step 9:** Category compilations include ALL videos (reused + new)
8. **Steps 10-14:** Full playlist-level synthesis and distribution

**Note:** Same video may have DIFFERENT category assignments in different playlists. This is expected.

</cross-playlist-dedup>

---

<incremental-updates>

### Incremental Playlist Updates

When a previously processed playlist gains new videos.

#### Playlist State Tracking

```json
{
  "PLxxx123": {
    "playlist_title": "AI Tools 2025",
    "last_processed": "2026-02-01T10:00:00Z",
    "video_count_at_last_process": 42,
    "video_ids_at_last_process": ["id1", "id2", "..."],
    "categories": ["Category A", "Category B"]
  }
}
```

#### Process

1. Re-extract playlist inventory (`--flat-playlist`)
2. Diff: `new_videos = current - last_processed`
3. **New videos:** Check registry (Step 0) → process new/unregistered
4. **Removed videos:** Do NOT delete outputs. Update playlist state. Flag for Jon.
5. **Regenerate:** Affected category compilations + playlist-level outputs
6. **Video-level outputs are IMMUTABLE** — enhanced transcripts, reports, infographics never regenerated unless explicitly requested

#### Triggers

- **Manual:** Jon requests playlist refresh ("Refresh the Claw playlist")
- **Scheduled:** Playlist poll cron (daily at 6 AM CST)
- **Threshold:** When yt-dlp detects N+ new videos

#### Cron Configuration

```json
{
  "name": "YouTube Playlist Poll — Claw",
  "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "America/Chicago" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Poll the Claw YouTube playlist. Compare against global_processed_registry.json. If new videos found, process each individually. Report findings to Topic 22.",
    "model": "gemini"
  }
}
```

</incremental-updates>

---

<processing-modes>

### Processing Modes

#### Mode 1: Singles Processing
**When:** 1-3 new videos detected via cron poll
**Flow:** Step 0 → Step 2 (transcript) → Step 4-8 (full individual processing) → Category assignment → Update registry
**Cost:** ~$0.03-0.05 per video
**Time:** ~5-10 min per video

#### Mode 2: Small Batch (5-10 videos)
**When:** Manual trigger or 5-10 new videos accumulated
**Flow:** Full Steps 0-8, process one category at a time, generate category compilations
**Cost:** ~$0.15-0.50
**Time:** ~30-60 min

#### Mode 3: Full Playlist Processing
**When:** New playlist submitted or major refresh requested
**Flow:** Full Steps 0-14, all phases, all deliverables
**Cost:** ~$3-5 for ~100 videos
**Time:** 2-4 hours (can be spread across sessions)

#### Mode Selection

```
IF new_video_count <= 3:
  → Singles mode (immediate, no compilation update)
  → Category recompile triggers at threshold (3+)

ELIF new_video_count <= 10:
  → Small batch mode
  → Category recompiles for affected categories
  → Skip master compilation unless manual request

ELSE:
  → Full playlist mode
  → All steps, all phases, all deliverables
  → Step 14 distribution ONLY after full pipeline completion
```

</processing-modes>

---

<chunking-protocol>

### Large Transcript Chunking Fix

> **CRITICAL BUG FIX:** Transcripts > 30KB cause sub-agents to generate stub/placeholder content instead of real analysis. This was identified during the Claw playlist processing where 46 out of 86 transcripts produced stubs.

#### The Problem

When a full transcript exceeds ~30KB (typically videos >30 minutes), sending the entire text in a single LLM prompt causes:
- Truncated or stub output ("See full transcript for details")
- Placeholder content that passes cursory checks but lacks substance
- Loss of insights from the latter portions of long transcripts

#### The Fix: `enhance-transcript.sh` Protocol

For any transcript > 30KB:

1. **Measure transcript size:**
   ```bash
   TRANSCRIPT_SIZE=$(wc -c < "transcripts/{id}-timestamped.txt")
   if [ "$TRANSCRIPT_SIZE" -gt 30000 ]; then
     echo "CHUNKED PROCESSING REQUIRED"
   fi
   ```

2. **Split into overlapping chunks:**
   - Chunk size: 15KB with 2KB overlap
   - Split at paragraph/sentence boundaries (never mid-sentence)
   - Each chunk includes section context (which timestamp range it covers)

3. **Process each chunk independently:**
   - Step 4 (timestamp map): Generate per-chunk, then merge and deduplicate
   - Step 6 (enhanced transcript): Process each section individually, merge into full document

4. **Merge and validate:**
   - Check for duplicate sections (from overlapping regions)
   - Verify no gaps in timestamp coverage
   - Confirm minimum insight count met across the full document

5. **Quality gate for chunked transcripts:**
   - Enhanced transcript word count must be > 80% of original transcript word count
   - If output is < 50% of input length → flag as potential stub, reprocess
   - Manual spot-check: first section, middle section, last section must all have substantive content

#### Detecting Stubs (Retroactive)

For previously processed transcripts that may be stubs:
```bash
# Check if enhanced transcript is suspiciously short
ENHANCED_SIZE=$(wc -c < "enhanced-transcripts/{id}-enhanced.md")
ORIGINAL_SIZE=$(wc -c < "transcripts/{id}-timestamped.txt")
RATIO=$(echo "$ENHANCED_SIZE / $ORIGINAL_SIZE" | bc -l)

if (( $(echo "$RATIO < 0.5" | bc -l) )); then
  echo "LIKELY STUB — needs reprocessing: {id}"
fi
```

</chunking-protocol>

---

<dashboard-integration>

### Dashboard Integration

After pipeline processing (any mode), update the PVD Command Dashboard:

#### Files to Update

1. **`dashboard-data/pipeline.json`** — Pipeline-level statistics:
   - `videosAnalyzed`: Count of videos with completed reports
   - `transcripts`: Count of completed transcripts
   - `framesExtracted`: Total frames across all videos
   - `infographics`: Count of generated infographics
   - `queueNew`: Videos awaiting processing
   - `status`: Current pipeline status
   - `stepsComplete` / `stepsTotal`: Phase-level progress (now 15 steps, 0-14)
   - `compilationReport`, `podcastScript`, `slideDeck`: Boolean deliverable flags

2. **`dashboard-data/youtube-skill.json`** — Detailed YouTube data:
   - `playlists.claw.categories`: Category breakdown with video counts
   - `playlists.claw.status`: Processing status
   - `playlists.claw.totalVideos`, `transcripts`, `framesComplete`, etc.
   - `playlists.antigravity`: Completed playlist data
   - `globalRegistry`: Total videos and last updated timestamp
   - `deliverables`: Compilation, podcast, slide deck counts

3. **Infographic assets** → Copy to dashboard `public/` directory for display

#### Update Flow

```
Pipeline run completes (any mode)
  → Read current state from RUNBOOK.md
  → Update pipeline.json with accurate counts
  → Update youtube-skill.json with category data
  → Git commit + Vercel deploy (if dashboard repo)
```

#### Dashboard Panel Reference

The `PipelinePanel.tsx` component reads:
- Top stats: `videosAnalyzed`, `transcripts`, `framesExtracted`
- Pipeline steps progress bar: `stepsComplete` / `stepsTotal`
- Completion by step: Progress bars for transcripts, frames, infographics
- Deliverables checklist: infographics, compilation, podcast, slides
- Categories: Name, count, reports ready

</dashboard-integration>

</systems>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                        REFERENCE                               -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<reference>

## Technical Reference

<tools>

### Required Tools

| Tool | Purpose | Version |
|---|---|---|
| yt-dlp | Video/subtitle/metadata download | Latest stable |
| ffmpeg | Frame extraction | 4.4+ |
| Opus 4.6 | Reports (7), synthesis (9-10, 12) | Current |
| Gemini Flash | Categorization (3), timestamp maps (4) | Current — FREE |
| Gemini Pro Vision | Frame analysis (6) | Current — FREE |
| Nano Banana Pro | Infographic generation (8, 9, 12d) | Current — FREE |
| Whisper API | Fallback transcript (2, rare) | Latest |
| NotebookLM | Audio podcasts, deep research (11) | Pro account |
| Remotion | Programmatic video creation (14b) | Latest |

</tools>

---

<model-routing>

### Model Routing (Cost Optimization)

| Step | Model | Cost |
|---|---|---|
| 0 Registry Check | Local JSON | FREE |
| 1 Inventory | yt-dlp | FREE |
| 2 Transcripts | yt-dlp / Whisper | FREE / ~$0.01 |
| 3 Categorize | Gemini Flash | FREE |
| 4 Timestamp Map | Gemini Flash | FREE |
| 5 Frames | ffmpeg | FREE |
| 6 Enhanced Transcript | Gemini Pro Vision + Opus | FREE / ~$0.03 |
| 7 Report | Opus 4.6 | ~$0.02 |
| 8 Video Infographic | Nano Banana Pro | FREE |
| 9 Category Compilation | Opus + Nano Banana Pro | FREE / ~$0.05 |
| 10 Master Compilation | Opus 4.6 | ~$0.10 |
| 11 NotebookLM | Google NotebookLM | FREE (Pro) |
| 12 Content Assembly | Opus 4.6 + Nano Banana Pro | ~$0.05 |
| 13 Cleanup | Local scripts | FREE |
| 14 Content Distribution | Opus 4.6 + Remotion | ~$0.05 |

**Estimated total for ~100 videos: ~$3-5**

</model-routing>

---

<file-organization>

### File Organization

```
pipeline-workspace/
├── global_processed_registry.json    # Step 0 — cross-playlist dedup
├── playlist_states.json              # Incremental update tracking
├── processed_videos.txt              # yt-dlp download archive
│
├── metadata/                         # Step 1
│   └── {id}.info.json
│
├── transcripts/                      # Step 2
│   └── {id}-timestamped.txt
│
├── timestamp-maps/                   # Step 4
│   └── {id}-map.json
│
├── frames/                           # Step 5
│   └── {id}/
│       ├── frame_0001_t0090.jpg
│       └── frame_manifest.json
│
├── enhanced-transcripts/             # Step 6 — SOURCE OF TRUTH
│   └── {id}-enhanced.md
│
├── reports/                          # Step 7
│   └── {id}-report.md
│
├── infographics/                     # Step 8 — PREMIUM EVERY VIDEO
│   └── {id}-infographic.png
│
├── playlists/                        # Per-playlist organized outputs
│   └── {playlist_id}/
│       ├── playlist-inventory.json
│       ├── processing-plan.json
│       ├── categories/
│       │   └── {category_slug}/
│       │       ├── v{N}/
│       │       │   ├── compilation.md
│       │       │   ├── category-infographic.png
│       │       │   └── metadata.json
│       │       └── current -> v{N}/
│       ├── compilations/
│       │   └── v{N}/
│       │       ├── master-report.md
│       │       ├── master-infographic.png
│       │       ├── podcast-script.md
│       │       └── metadata.json
│       ├── notebooklm/              # Step 11 outputs
│       │   ├── notebook-id.txt
│       │   └── generated-outputs/
│       └── content-drops/           # Step 12 drafts + Step 14 finals
│           └── {drop-name}/
│
├── archive/                          # Step 13 — retained MEDIUM/LOW frames
│   └── {id}/
│       └── frame_NNNN.jpg
│
├── downloads/                        # TEMP — deleted after frame extraction
└── audio/                            # TEMP — deleted after Whisper
```

### External Drive Storage

When SSD space is limited (128GB), pipeline data should target external drive:
```
/Volumes/New Volume/PVD-Workspace/youtube-pipeline/
├── pipeline-v4-claw/     # Claw playlist processing data
├── pipeline-v4/          # Antigravity playlist data
├── playlist/             # Raw playlist transcripts
├── pipeline-engine/      # Processing scripts
└── pipeline-poc/         # Original POC data
```

Create symlinks from workspace:
```bash
ln -s "/Volumes/New Volume/PVD-Workspace/youtube-pipeline/pipeline-v4-claw" \
  "context/transcripts/pipeline-v4-claw"
```

</file-organization>

---

<quality-standards>

### Quality Standards & Scoring

#### Minimum Quality Thresholds

| Output | Minimum Standard |
|---|---|
| Enhanced Transcript | ALL vision sections covered. "Synthesized Knowledge" present for every section. Word count > 80% of original. |
| Intelligence Report | ≥5 distinct insights, ≥3 actionable items, ≥3 takeaways, all with timestamps |
| Infographic | 1200×800px, premium design (not text card), readable at 50% zoom |
| Category Compilation | Ranked by weighted score, cross-video insights, deduplicated actions |
| Podcast Script | 15-25 minutes speaking time |
| Content Drafts | All 8 platforms drafted, platform-specific formatting |
| Content Package (Step 14) | ALL steps 0-13 complete. Master compilation reviewed. Jon-approved. |

#### Stub Detection Rules

An output is a STUB if:
- Enhanced transcript is < 50% the word count of the original transcript
- Report contains fewer than 3 specific insights (not generic filler)
- Insights reference only the video title without specific timestamp/content details
- Report contains placeholder text like "See full report" or "More details to follow"

**If a stub is detected: HALT, log, reprocess with chunking protocol.**

#### Score Distribution Expectations

| Weighted Score | Expected % | Interpretation |
|---|---|---|
| 9.0-10.0 | 5-10% | Exceptional — immediate, high-impact |
| 7.0-8.9 | 20-30% | Strong — clear value for Jon's projects |
| 5.0-6.9 | 40-50% | Moderate — useful context |
| 3.0-4.9 | 15-20% | Low — tangential or theoretical |
| 1.0-2.9 | 0-5% | Minimal — consider excluding from compilations |

</quality-standards>

---

<metrics>

### Pipeline Metrics & Monitoring

#### Processing Efficiency

| Metric | How to Measure |
|---|---|
| Deduplication rate | `reused / total × 100` |
| Processing time per video | Wall clock Step 2 → Step 8 |
| API cost per video | Sum of all LLM + vision + infographic calls |
| Storage per video (retained) | Enhanced transcript + report + infographic + info.json |
| Stub rate | `stubs_detected / total_processed × 100` — target < 5% |

#### Quality Metrics

| Metric | Target |
|---|---|
| Avg insights per video | ≥ 5 |
| Vision sections with LOW confidence | < 10% |
| Transcript fallback to Whisper | < 5% |
| Stub transcripts | 0% (with chunking fix) |

#### Registry Health

| Metric | Target |
|---|---|
| Entries with all steps complete | > 95% |
| Orphaned entries (no playlist) | Review quarterly |
| Entries with partial steps | Investigate and resolve |

</metrics>

</reference>

---

<!-- ═══════════════════════════════════════════════════════════════ -->
<!--                          RULES                                 -->
<!-- ═══════════════════════════════════════════════════════════════ -->

<rules>

<operational-rules>

## Operational Rules (NON-NEGOTIABLE)

1. **Step 0 FIRST — ALWAYS** — Check registry before ANY processing. No exceptions.
2. **Human verification** — Jon confirms playlist titles match before ANY processing.
3. **Category-first** — Process one category at a time, never bulk all videos.
4. **Transcript drives frames** — Timestamp map BEFORE any video download.
5. **Enhanced transcript = source of truth** — Everything downstream builds from it.
6. **Synthesized Knowledge in every section** — The three-part merge (Said + Shown + Merged) is mandatory.
7. **PREMIUM infographic at EVERY level** — Video, category, playlist. No shortcuts. No text cards.
8. **Jon approves categories + sample** before scaling (combined gate).
9. **Title + ID = source of truth** for video identity (titles for matching, IDs for dedup).
10. **Delete videos after frame extraction** — Disk space limited (128GB SSD).
11. **Registry updated after every operation** — Enables resume from any failure.
12. **Test run first** for any new playlist before full processing.
13. **Quality > quantity** — A single excellent infographic beats 97 text cards.
14. **Chunking for large transcripts** — NEVER send >30KB in a single prompt. Split and merge.
15. **NotebookLM = mandatory Phase C step** — Complementary to pipeline, not optional.
16. **Nothing is ever deleted from registry** — Versions are archived, old compilations preserved.
17. **Content distribution is POST-PIPELINE ONLY (Step 14)** — Full pipeline (Steps 0-13) must complete before ANY content is pushed externally. The value is COMPILED intelligence, not individual video reposts. No partial pushes.
18. **🕊️ SABBATH COMPLIANCE** — No pipeline processing during Sabbath (Friday sunset → Saturday sunset, Huntsville AL). If a batch is mid-processing when Sabbath begins:
    - Checkpoint current progress to registry (status: "partial", completed_steps logged)
    - Halt all processing 15 minutes before Friday sunset
    - Resume automatically after Saturday sunset
    - No cron jobs, no downloads, no API calls during Sabbath window
    - Devotional delivery IS allowed during Sabbath (worship, not work)

</operational-rules>

</rules>

---

## Changelog

### v5.0 (2026-02-21) — CONSOLIDATED (XML-Hybrid Reformat)
- **REFORMATTED:** Entire spec into XML-hybrid two-file structure (METHODOLOGY.md + RUNBOOK.md)
- **RESTRUCTURED:** Content distribution moved from Step 12 to Step 14 (POST-PIPELINE). Full pipeline must complete before ANY external push.
- **ADDED:** Step 14 — Content Distribution & External Push with verification gate and Jon approval requirement
- **RENAMED:** Step 12 → "Content Deliverables Assembly" (preparation only, no external push)
- **ADDED:** Phase D (Content Distribution) as fifth pipeline phase
- **ELEVATED:** Step 0 (Registry Check) to FIRST position — must run before ALL processing
- **ADDED:** Step 11 — NotebookLM Integration Phase (mandatory for Phase C)
- **ADDED:** Anti-gravity / Remotion video creation integration in Step 14
- **ADDED:** Large Transcript Chunking Fix (>30KB handling)
- **ADDED:** Processing Modes (singles, small batch, full playlist)
- **ADDED:** Dual infographic standard (PVD PNG + NotebookLM deck)
- **ADDED:** External drive storage support with symlinks
- **ADDED:** Category version archival with full recompile every 3rd version
- **ADDED:** Category drift handling (uncategorized videos)
- **ADDED:** Stub detection rules and retroactive fix protocol
- **ADDED:** Cron configuration for playlist polling
- **ADDED:** Dashboard integration section (pipeline.json + youtube-skill.json)
- **FIXED:** 46 stub transcripts from chunking bug documented and fix protocol included
- **CLARIFIED:** Audio podcasts = NotebookLM; Video scripts = PVD pipeline
- **PRESERVED:** All v4.0 features (registry, dedup, incremental, Sabbath, quality gates)

### v5.0 (2026-02-20) — CONSOLIDATED (Original)
- Consolidated all knowledge from v1.0, v2.0, v3.0, v3.1, v4.0, v4.5 into single authoritative spec

### v4.0 (2026-02-12) — LOCKED
- Global Video Registry, Step 1.5 Registry Check, Step 13 Cleanup
- Incremental updates, vision confidence scoring, combined approval gate
- Sabbath compliance, frame budget caps, single-pass extraction

### v3.1 (2026-02-11)
- Category-first processing, enhanced transcript as source of truth, premium infographics

### v3.0 (2026-02-11)
- Category-first architecture introduced

### v2.0 (2026-02-10)
- Hardened 8-step pipeline, title-based matching, recovery plan

### v1.0 (2026-02-10)
- Initial pipeline definition

---

*v5.0 CONSOLIDATED — The ONLY authoritative YouTube pipeline spec.*
*All prior versions (v1-v4.5) and the original SKILL.md are archived. Do not reference them for current process.*
*Knowledge ingestion library. Enhanced transcripts as source of truth. Premium infographics at every level.*
*Cross-playlist dedup. NotebookLM integration. Content distribution POST-PIPELINE ONLY. Sabbath-compliant.*
*Changes require Jon's explicit approval.*
*— Jon (North Star Command Protocol) + Pulse Vibe Daily ⚡*

</pipeline>
