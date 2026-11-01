# Coverage, depth, reuse and the Sabbath (v8.3)

Runs created at v8.3 or later carry `depth_contract: depth/1`. Older runs keep their recorded contracts; never add these fields to an old run. Every check below has a written escape for a legitimate exception. The escapes exist so a static talk or a sponsor read is not forced into padding; they are not a way around review.

These rules restore what v4–v7.2 learned and v8.0 dropped: proportionate visual coverage, a sampling audit, recoverable small text, thinness detection, structured reports, category synthesis, caption checks, owner priorities, reuse of reviewed work and Sabbath observance.

## Visual coverage (quick and full)

Minimum frames scale with duration (the v7.2 formula). Inspected frames must reach one third of it.

| Duration | Sampled minimum | Inspected minimum |
|---|---:|---:|
| up to 5 min | 15 | 5 |
| 5–15 min | 30 | 10 |
| 15–30 min | 50 | 17 |
| 30–60 min | 80 | 27 |
| 60–90 min | 120 | 40 |
| over 90 min | 150 | 50 |

`verify` also finds uninspected stretches longer than `max(120 s, duration/8)` between inspected frames and the source edges, and requires an opening frame and a closing frame (within `max(15 s, 5%)` of the end). Run `sampling-audit RUN VIDEO_ID` before writing the review to see the same numbers verify will compute.

Record the result in `analysis.json.sampling_audit`:

- `{"verdict":"pass"}` when coverage meets the table and every long stretch is inspected, or listed in `accepted_gaps` with a reason (for example an unchanging title card).
- `{"verdict":"visual_static_downgrade_accepted","reason":"..."}` only after looking: the screen genuinely adds nothing (talking head, static slide). The reason is at least a sentence.

Fix a shortfall with tools, not a verdict: `capture RUN VIDEO_ID --at SECONDS --purpose "..."` adds frames at original times (closing scouts, a missed demo). For small code or UI text, `capture ... --height 1080` downloads a short higher-resolution derived section (at most 180 s) into the archive's `derived/` folder; the retained source is unchanged and the derived file is hash-bound in the frame manifest. `contact-sheets` builds labelled orientation sheets; `enlarge RUN VIDEO_ID FRAME --box x0,y0,x1,y1` saves a cropped enlargement. Sheets and enlargements are review aids, not inspection evidence.

Every observation records `legibility`: `clear`, `partial` or `illegible`. Partial and illegible readings belong in Uncertainties, with a recapture where the detail matters.

## Spread and inputs

- Claims and observations together must reach every quarter of the source. A source that is silent or repetitive in a quarter records `coverage_exception` with the reason.
- Captions record their provenance (`manual`, `automatic` or `unknown`) in `media.json`. When captions start late, end early or fall silent for long, `verify` asks for `caption_gaps_acknowledged` in `analysis.json`: say what was checked in the frames for that stretch.
- The owner can flag a section with `priority RUN VIDEO_ID --start S --end E --reason "..."`. A priority section needs at least two inspected frames inside it and a claim citing a cue inside it. Sponsor reads and ads are never dismissed without a look; flagging them is how the owner makes that explicit.
- Placeholder text (`TBD`, `[insert`, `lorem ipsum`, `{{`, “summary goes here”) fails verification in every written deliverable.
- `analysis.json.producer.model` names the model that wrote the analysis, separate from the reviewer. Full receipts (`full-review.json`, `infographic.json`) record `producer` too. This makes a delegated stub traceable; it is not a gate on which model may write.

## Full-mode depth

- `intelligence-report.md` has these sections, each about the video's own subject (write “None in this source.” when true): Claims and evidence; Tools and technologies; Code, prompts and configurations; Visual evidence that changed the understanding; Unverified or overstated claims.
- Each source-map section is compared with its cue range. A section under 35% of its source words needs `thin_reason`; a section spanning more than `max(10 min, duration/4)` needs `long_section_reason`. Condensing repetition or filler is legitimate when said; dropping substance is not. Ratios find thin work; they never prove completeness, and padding to pass them is a failure.
- `full-review.json.spot_checks` holds three checks against the source, one in each third of the cues: `{position:"early|middle|late", cue_index, finding}`.
- `master-compilation.md` has a `Gaps` section: topics the collection under-covers or leaves contested.
- Every category with two or more videos has a compilation document with Agreements, Contradictions and Gaps sections, bound in `categories.json` as `compilation: EVIDENCE` plus `analyses: {VIDEO_ID: analysis.md SHA-256}`.

## Reusing reviewed work

A review is reused only when every byte it covered is identical. `carry-over RUN VIDEO_ID --from PRIOR_RUN` copies the prior `analysis.md` and `analysis.json` when the prior video verifies and its source, captions, cues, transcript and every inspected frame are byte-identical in the new run. The receipt gains `carried_over` (from where, when, what was identical) and keeps the original reviewer. It never overwrites, and the report labels the reuse. A prior run under an older contract may need depth fields added to the receipt afterwards; `carry-over` lists what is missing. Full-mode deliverables (expanded account, infographic, notebook) are not carried; redo them.

For a grown or changed playlist, initialize a new run, then `plan-update RUN --from PRIOR_RUN`. It writes `update-plan.json` with added, removed and retained videos, and the sample count to reuse for each carry candidate so frames come out identical. Retained media is reused by hash during acquisition. Synthesis is always redone.

## Sabbath observance

No pipeline work runs from Friday sunset to Saturday sunset (default location Huntsville, AL; `settings.json` `sabbath` block). Work stops `stop_minutes_before_sunset` (default 15) before Friday sunset. Sunset is computed offline (NOAA equation, about a minute of accuracy).

- Any run command during the window checkpoints the run as `paused_sabbath` with `resume_at` and exits with code 75. Nothing is ended or discarded. `status` and `sabbath` stay available.
- Acquisition bounds each download so it stops at the window start; an item cut off by the deadline is not counted as a failed attempt.
- `run RUN` acquires batch after batch and waits through rate-limit backoff and the Sabbath, resuming on its own after Saturday sunset. Leave it running in a terminal for an unattended resume.
- An agent checks `sabbath` before semantic, image or browser work. During the window it stops at a clean checkpoint, reports `resume_local`, and if its harness can schedule a wake-up, schedules one for after `resume_at`. It does not start NotebookLM generation, downloads or comment fetches during the window.
- The next command after the window restores the run's prior status.
