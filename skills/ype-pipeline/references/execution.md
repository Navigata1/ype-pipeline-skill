# Material execution and resumption

Run from the skill folder, or resolve `scripts/ype.py` relative to it. Shell paths below are placeholders; select concrete run/archive paths from the workspace settings and user request. Do not download anything before the user's testing cue when the handoff says to wait.

```sh
python3 scripts/ype.py init "$RUN" --mode quick --playlist "$PLAYLIST" --archive "$ARCHIVE"
# Curated inputs instead: --title "A useful collection" --url URL --url URL
python3 scripts/ype.py acquire "$RUN" --max-items 2 --budget-seconds 900
python3 scripts/ype.py status "$RUN"
python3 scripts/ype.py sample "$RUN" VIDEO_ID --count 100
python3 scripts/ype.py verify "$RUN"
python3 scripts/ype.py render "$RUN"
```

With the audience channel (see `community.md`):

```sh
python3 scripts/ype.py init "$RUN" --mode quick --playlist "$PLAYLIST" --archive "$ARCHIVE" --community --second-labeller --synthesis
python3 scripts/ype.py enable "$RUN" --community 100          # or widen an existing run
python3 scripts/ype.py community "$RUN" VIDEO_ID              # or --from-info INFO.json
python3 scripts/ype.py community-blind "$RUN" VIDEO_ID        # with --second-labeller, after topics are fixed
python3 scripts/ype.py community-score "$RUN" VIDEO_ID
python3 scripts/ype.py claim-matrix "$RUN" skeleton           # then: claim-matrix "$RUN" check
```

Reuse, review tools and the Sabbath (details in `depth.md`):

```sh
python3 scripts/ype.py sabbath                                  # observance window; no work inside it
python3 scripts/ype.py run "$RUN"                                # acquire until done; waits through backoff and the Sabbath
python3 scripts/ype.py plan-update "$RUN" --from "$PRIOR_RUN"    # a grown playlist: what is new, removed, reusable
python3 scripts/ype.py carry-over "$RUN" VIDEO_ID --from "$PRIOR_RUN"
python3 scripts/ype.py sampling-audit "$RUN" VIDEO_ID
python3 scripts/ype.py contact-sheets "$RUN" VIDEO_ID
python3 scripts/ype.py enlarge "$RUN" VIDEO_ID f_0041.jpg --box 0,0,400,200
python3 scripts/ype.py capture "$RUN" VIDEO_ID --at 712.5 --purpose "closing scout"   # add --height 1080 for small text
python3 scripts/ype.py priority "$RUN" VIDEO_ID --start 300 --end 360 --reason "owner flagged demo"
```

A command during the Sabbath checkpoints the run as `paused_sabbath` and exits 75; the run is not ended.

`init` obtains playlist metadata only; curated explicit URLs need no network until acquisition. Inventory retains every position and deduplicates work by video ID. Playlist enumeration is capped at 1,000 and refuses a truncated/cap-sized result. Unavailable entries and explicit skips remain coverage gaps. There is no silent “complete enough” conversion.

Acquisition processes at most two items by default, sequentially. Each item checkpoints before/after work; five unsuccessful attempts require inspection. A 429 ends the current batch and records exponential retry-after, capped at one hour. Authentication/private-video errors require owner input. Completed compatible materials are reused by identity and SHA-256. Timeouts preserve partial files. Re-run the same command after the recorded delay; do not create a duplicate run to avoid backoff. No daemon automatically consumes the next 400 entries.

Default download policy is at most 720p and 2 GiB final media per video. Check available disk before each item; keep a 15 GiB reserve. During download, check retained working bytes and free space every 250 ms, with a 2.5× file budget plus 50 MiB allowance for merging/partials. These are local resource bounds, not a guarantee against provider limits or instantaneous overshoot between checks. A stricter policy cannot silently reuse a larger source. Do not overwrite/delete it to satisfy the new policy. Explicitly choose a compatible existing source or a separate derived capture.

Use approximately 60 scout frames for static talks, 100 for ordinary explainers, and 250+ for dense code/UI; choose for the actual video. Deduplication reduces retained count. Scout selection preserves original source presentation times in the manifest; targeted seeks are approximate nearest-frame times. Never infer original time from deduplicated indices. Interrupted frame directories are renamed and preserved before a fresh attempt.

For a source already captured by `video-analysis`, use `import-cache RUN VIDEO_ID FOLDER`. It requires matching `metadata.json`, one source video, and SRT/VTT captions; the receipt says `cached-reprocessing`. It does not establish a fresh download. Existing standalone frame files without original timestamps are not silently promoted into the new timestamp manifest.

Captions are English-first. Missing captions stop that item; use an explicitly approved timestamped ASR/translation path and record its provenance before analysis. Do not invent a transcript or claim continuous watching from sampled images.

Each run has one writer lock. The shared archive has a separate writer lock, so two active runs cannot download into it concurrently. Use a new run for a changed input/sampling policy; keep original runs and source media. The notebook registry reuses the same remote notebook independently of local run revisions.
