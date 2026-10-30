# Quick analysis contract

Purpose: answer the user's build/workflow question from the complete transcript and selected visible evidence, with a calm expandable HTML report. Do not spend time on images or NotebookLM unless requested.

For each video, write `videos/VIDEO_ID/analysis.md` with these exact headings:

- `## Thesis` — what the video argues, attributed to its speaker.
- `## What was said` — meaningful progression, mechanisms and qualifications, with source timestamps.
- `## What the frames add` — concrete visible support or tension, with manifest frame names/times.
- `## Uncertainties` — sampled scope, illegible UI, speculative claims, absent tests and other limits.
- `## Application` — a small, specific useful change to the user's current work; distinguish inference.

When the run has `--community`, add `## Community check`: how the comments received the video's claims, which corrections hold against the transcript or frames, and the stated limits. Follow `community.md`; with `--synthesis`, also fill `claim-matrix.json` once the analyses are final.

The script checks headings, evidence links and receipt hashes. It cannot establish that a summary is good. Read the whole transcript, not only search snippets. Inspect enough frames to cover the important argument; the minimum three is a mechanical floor, not adequate coverage for every video. Use originals when contact-sheet text is too small. If only text is available, report partial text analysis; it cannot pass the two-channel completion contract.

Write `analysis.json` only after actual review. Include transcript/source hashes, inspected frame hashes, grounded claims and observations. Bind prose after final edits. For multiple videos, write `master-compilation.md` plus `synthesis.json`: convergence, disagreements, reusable mechanisms and the specific next experiment. The synthesis must retain source distinctions, not blend all authors into a single claim.

`verify` must pass before presenting a quick run as complete. `render` still produces an explicitly incomplete report when something is missing. Preserve raw videos, original captions, timestamped transcript, frames, analysis and receipts. Deliver captured/inspected counts and the distinction between fresh capture, cached reprocessing and synthetic fixtures.
