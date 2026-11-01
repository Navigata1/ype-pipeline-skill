# YPE Pipeline Skill

**YPE (YouTube Pipeline Experience)** turns YouTube videos and playlists into evidence-grounded research: the complete transcript, sampled frames with their original timestamps, a per-video analysis that separates what was said from what was shown, and an expandable HTML report. Full mode adds enhanced transcripts, intelligence reports, native image-generated infographics and a playlist-named NotebookLM notebook with audio and slides.

Current version: **YPE v8.3**. The v7.2 single-file skill is kept in [`archive/v7.2/`](archive/v7.2/SKILL.md).

## What changed in v8

v7.2 was a long instruction file; v8 is a small skill plus a Python runner that does the repetitive work and refuses to accept stale evidence.

- **Two modes.** *Quick* reads the whole transcript, inspects sampled frames and writes a per-video analysis. *Full* adds the deeper deliverables and the NotebookLM adapter. Audio and slides are separate required results.
- **Durable, resumable runs.** Bounded acquisition (two videos per call by default), atomic checkpoints, single-writer locks, rate-limit backoff that returns a retry time, and no delete operation.
- **Evidence binding.** Retained source and caption hashes, frame manifests with original presentation times, and review receipts bound to the exact bytes reviewed. `verify` fails when anything changes after review.
- **Audience channel (opt-in).** `--community` ranks a video's top comments and scores how its claims landed; `--second-labeller` adds a blind labeller from another model family and reports Cohen's kappa; `--synthesis` builds a cited cross-video claim matrix.

## Source-first depth in v8.1

Full mode preserves the complete cleaned spoken substance section by section, integrates inspected visual discoveries, and reviews source coverage explicitly. Project applications live in a separate `project-applications.md`. Infographics need a source-backed concept plan and acceptance for coverage, relationships, labels, legibility and source specificity.

New full runs package exactly one neutral enriched source per unique video. Capacity limits stop packaging instead of silently combining videos, splitting one video or reducing substance. Audience reception and the claim matrix remain opt-in analytical layers in the local report. Existing runs keep their recorded contracts.

These checks bind evidence and recorded review; they cannot independently prove semantic quality or remote actions.

## Coverage, reuse and the Sabbath in v8.3

v8.3 restores what earlier versions learned and the v8 rewrite dropped: frame coverage scaled to duration with a gap audit, recoverable small text (contact sheets, enlargements, higher-resolution derived captures), thinness and spread checks, structured intelligence reports and category compilations, caption provenance and owner priority sections, and reuse of reviewed work across runs when the evidence is byte-identical. See [`references/depth.md`](skills/ype-pipeline/references/depth.md).

YPE observes the Sabbath: no pipeline work from Friday sunset to Saturday sunset for the location in `settings.json`. A run in progress is paused and checkpointed, not ended, and `ype.py run` resumes acquisition on its own after sunset.

## Layout

```text
skills/ype-pipeline/        # the skill: SKILL.md, references/, scripts/, agents/
tests/                      # unittest suite (synthetic fixtures)
AGENTS.md                   # workspace rules for agents
settings.example.json       # copy to settings.json and set your archive
archive/                    # earlier versions, history only
runs/                       # created locally per run; not committed
```

The skill treats the folder two levels above `skills/ype-pipeline/` as its workspace, so clone this repository where you want runs to live and link the skill into your agent's skills folder:

```sh
ln -s "$PWD/skills/ype-pipeline" ~/.claude/skills/ype-pipeline
cp settings.example.json settings.json
```

## Requirements

Python 3 with Pillow (python-markdown is optional; a small built-in renderer is used without it). Acquisition needs `yt-dlp`, `ffmpeg` and `ffprobe`. Full mode needs an agent with vision, native image generation and browser control.

## Use

```sh
python3 skills/ype-pipeline/scripts/ype.py init runs/MY-RUN --mode quick --playlist 'PLAYLIST_URL' --archive '/path/to/archive'
python3 skills/ype-pipeline/scripts/ype.py acquire runs/MY-RUN
python3 skills/ype-pipeline/scripts/ype.py sample runs/MY-RUN VIDEO_ID --count 100
# the agent reads the transcript, inspects frames, writes analysis.md and analysis.json
python3 skills/ype-pipeline/scripts/ype.py verify runs/MY-RUN
python3 skills/ype-pipeline/scripts/ype.py render runs/MY-RUN
```

See [`SKILL.md`](skills/ype-pipeline/SKILL.md) and its references for the full contract.

## Tests

```sh
python3 -m unittest discover -s tests
```

The suite uses synthetic fixtures. `tests/test_linked_example.py` re-verifies a workspace's README-linked example run and skips in a checkout with no `runs/` folder.

## What the scripts do not prove

Scripts enforce identity, hashes, locks, frame times, receipt consistency and packet contents. Semantic accuracy, adequate sampling, actual image inspection, image-generation provenance and remote NotebookLM actions are agent attestations, recorded so they can be audited, not independently proven.
