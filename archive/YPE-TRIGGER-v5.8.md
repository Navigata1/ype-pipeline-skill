# ⚡ YPE v5.8 — YouTube Pipeline Experience TRIGGER

## GLOBAL TRIGGER KEYWORDS
Any of these phrases, in ANY channel (Telegram, Slack, Discord, WhatsApp), MUST trigger the full YPE v5.8 pipeline:
- "youtube pipeline"
- "YPE"
- "run the pipeline"
- "pipeline these videos"
- "youtube pipeline experience"
- "process these videos"
- "run YPE"

## WHAT GETS TRIGGERED
1. **Read** `/Users/idc2.0/clawd/skills/youtube-pipeline/METHODOLOGY.md` (the FULL v5.0 spec — 1,982 lines, 15 steps, 5 phases)
2. **Read** this file (`YPE-TRIGGER.md`) for the Quick-Batch pre-phase
3. **Execute** the Quick-Batch Pre-Phase (below)
4. **Execute** the FULL v5.0 pipeline (Steps 0-14, Phases 0/A/B/C/D) — NO MODIFICATIONS, NO SHORTCUTS, NO SKIPPING

## WHAT NEVER HAPPENS
- ❌ Quick summaries passed off as the deliverable
- ❌ Skipping to Phase C after Quick-Batch
- ❌ "Batch reports" replacing intelligence reports
- ❌ Any deviation from METHODOLOGY.md
- ❌ Sub-agents receiving anything other than the full pipeline spec

## PIPELINE VIOLATION PROTOCOL
If Pulse or any sub-agent skips ANY step:
1. Log violation to `brain/mistakes.md`
2. Alert Jon immediately
3. Halt pipeline
4. Revert to last checkpoint
5. Resume from the skipped step

---

## QUICK-BATCH PRE-PHASE (v5.8 Addition)

**Purpose:** Give Jon and Pulse immediate situational awareness BEFORE the deep pipeline runs.
**Duration:** 5-10 minutes max.
**This is the APPETIZER, not the meal.**

### QB-1: Video List Confirmation
- Restate ALL video URLs + titles back to Jon
- Include: upload date, channel name, duration, view count
- Jon confirms list before ANY processing
- If Jon flags a wrong video → swap URL → re-confirm

### QB-2: Transcript Quick-Pull
- `yt-dlp --write-auto-sub --sub-lang en --skip-download` for all videos
- These transcripts are REUSED by Step 2 (no duplicate work — addresses Forge's concern)
- Flag transcript quality: manual vs auto-generated
- Flag transcripts >30KB for chunked processing

### QB-3: Quick Intelligence Synthesis
- Model: Gemini Flash (FREE)
- Per video:
  - Executive summary (3-5 sentences)
  - Top 3 actionable insights
  - Relevance flag: 🔴 HIGH / 🟠 MEDIUM / 🟡 LOW (scored against Jon's current projects)
  - Suggested topic routing (which supergroup topic)
  - Estimated processing cost for full pipeline
- Also include (Scout's additions):
  - Video recency signal (upload date vs today)
  - Channel authority (subscriber count if available)
  - Duplicate/overlap detection (similar titles/topics within batch)

### QB-4: Quick-Batch Delivery
- Deliver compiled quick-batch report to Jon via current channel
- Push immediately applicable config insights to brain/ and knowledge/
- Flag any videos Jon might want to deprioritize before full run

### QB-5: MANDATORY HANDOFF TO FULL PIPELINE
- After QB-4 delivery, **IMMEDIATELY** commence Step 0 of v5.0
- QB transcripts are passed to Step 2 (no re-download)
- Pipeline state initialized from QB metadata
- **THIS HANDOFF IS AUTOMATIC. NO PAUSE. NO "SHOULD I CONTINUE?"**
- The Quick-Batch IS Phase 0.5 — it flows directly into Phase 0

---

## VERSION HISTORY
- **v5.8 (2026-02-24):** Added Quick-Batch Pre-Phase. Added global trigger. Added pipeline violation protocol. Judge agent integration for deliberation gates. All v5.0 content preserved unchanged.
- **v5.0 (2026-02-21):** Definitive consolidated spec. 15 steps, 5 phases. XML-hybrid format.
- **v4.0 (2026-02-12):** Global registry, incremental updates, Sabbath compliance.

---

## AGENT ASSIGNMENTS FOR YPE
| Phase | Primary Agent | Support |
|-------|--------------|---------|
| Quick-Batch | Pulse ⚡ | Scout 🔍 (metadata enrichment) |
| Phase 0 (Registry) | Stash 📚 | — |
| Phase A (Verify/Categorize) | Stash 📚 | Pulse ⚡ (Jon approval) |
| Phase B (Deep Processing) | Stash 📚 + Forge 🔨 | Gemini Vision (frames) |
| Phase C (Synthesis) | Pulse ⚡ | All agents for compilation |
| Phase D (Distribution) | Echo 📢 | Pulse ⚡ (approval gate) |

## JUDGE INTEGRATION
Judge ⚖️ is NOT inserted at every pipeline gate (Forge's concern about latency is valid). 
Judge activates ONLY at:
- **Step 3 gate** — Category assignment deliberation (affects entire pipeline flow)
- **Step 10** — Master compilation review (highest-stakes synthesis)
- **Step 14 gate** — Content package review before external push

All other gates remain Jon-only approval. This adds ~15 min total, not 60.

---

*This file is the TRIGGER. METHODOLOGY.md is the SPEC. Both are required. Neither replaces the other.*
*YPE v5.8 = Quick-Batch Pre-Phase + Full v5.0 Pipeline (unchanged) + Judge at key gates + Global trigger*
*— Jon (North Star) + Pulse Vibe Daily ⚡*
