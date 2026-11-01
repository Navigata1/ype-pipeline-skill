# Review receipts

Use actual paths, hashes and observations. JSON samples illustrate structure only; placeholders cannot satisfy validation. `core.evidence(path)` returns `{path,bytes,sha256}`; `core.identity_hash(run)` binds collection, ordered membership and unique work records.

`videos/ID/analysis.json`:
```json
{
  "reviewer": "actual acting agent and date",
  "transcript_reviewed": true,
  "source_sha256": "from media.json",
  "transcript_sha256": "current transcript.txt hash",
  "analysis_sha256": "current analysis.md hash",
  "inspected_frames": ["f_0001.jpg", "f_0010.jpg", "f_0020.jpg"],
  "inspected_frame_sha256": {"f_0001.jpg":"actual hash","f_0010.jpg":"actual hash","f_0020.jpg":"actual hash"},
  "observations": [{"frame":"f_0010.jpg","timestamp_seconds":42.5,"description":"Concrete visible observation, not a transcript paraphrase."}],
  "claims": [{"text":"Attributed claim","cue_indices":[4,5],"frames":["f_0010.jpg"]}],
  "limitations": ["Sampled viewing, not continuous viewing"]
}
```
Cue indices are zero-based `cues.json` entries. Observations must match manifest times. Claims may cite transcript cues or inspected frames; neither invented timestamps nor uninspected screenshots are valid.

`moments.json`: `{source_sha256, transcript_sha256, transcript_reviewed:true, moments:[{start:10,end:30,importance:"high",reason:"...",capture_seconds:[12,20,28]}]}`. All seconds are finite numbers within the full source duration.

`full-review.json`: `{reviewer, source_faithfulness_checked:true, analysis_sha256, files:{"enhanced-transcript.md":EVIDENCE,"intelligence-report.md":EVIDENCE}}`.

For `timed-source-account/1`, also bind `source_map_sha256`. `enhanced-source-map.json` contains `{source_sha256,transcript_sha256,enhanced_sha256,reviewer,examples_and_qualifications_checked:true,sections:[{heading,cue_start,cue_end,frame_names}]}`. Cue indices are inclusive, and sections collectively cover all canonical caption cues. This verifies accounting, not semantic completeness; review the actual prose against the complete source.

`infographic.json`: `{provider:"native-image-gen",generated_at,tool_call_ref,request:EVIDENCE,file:EVIDENCE,analysis_sha256,visually_reviewed:true,review_notes,dimensions:[width,height]}`. The receipt records a real tool action. The script cannot authenticate the tool provider from a JSON claim.

`synthesis.json`: `{reviewer,collection_digest,file:EVIDENCE,analyses:{"VIDEO_ID":"analysis.md SHA-256"}}`. Its file is `master-compilation.md`.

`categories.json`: `{"categories":[{"name":"Mechanism name","video_ids":["VIDEO_ID"]}]}`. Cover every video in exactly one primary category.

## Audience channel receipts

`run.json` records the options: `community:{enabled,top,max_comments,per_thread,reply_weight,second_labeller}` and `claim_matrix:true`.

`videos/ID/community/` is written by `community` and `community-score`; edit only the labels:

- `comments.json` (`ype-comments/1`): `{video_id,origin,fetched_at,caps,metadata,comments}`. Each comment keeps `id,parent,text,like_count,is_pinned,is_favorited,author_is_uploader,_time_text,timestamp`; nothing names the commenter.
- `top.json`: `{meta,comments}`, the ranked top N with `rank,score,likes,replies,replies_saturated,contested,top_replies`. It must equal a re-rank of `comments.json`.
- `harvest.json`: `{video_id,origin,fetched_at,recorded_at,extractor_version,caps,comments_available,fetched_total,roots,comments:EVIDENCE,top:EVIDENCE}`. `origin` is `fresh-fetch` or `imported-info`.
- `labels.json` and, with the second labeller, `labels.b.json`:
```json
{
  "labeller": "actual model or person",
  "VIDEO_ID": {
    "topics": {"ONE": "agents one-shot well, iterate badly (61:11)", "CRED": "the speaker's credibility", "GEN": "general"},
    "labels": {"1": ["E", "ONE", 1, "", "one-sentence paraphrase of a condition or correction"], "2": ["H", "GEN", 0, "", ""]}
  }
}
```
  Every rank in `top.json`, and no other, is labelled `[stance, topic, substantive 0/1, role "" | "speaker" | "creator", note]`. `labels.b.json` uses the same topics and a different labeller.
- `blind/{sheet.txt,topics.json,PROMPT.md}`: the second labeller's packet. Its topics must still equal `labels.json`.
- `metrics.json` and `community.md`: exact recomputations from the bound inputs, with `bindings:{top_sha256,labels_sha256,labels_b_sha256}`.

`analysis.json` adds `community_metrics_sha256`, the current `metrics.json` hash, when comments were available. `analysis.md` adds `## Community check`.

`claim-matrix.json` (`ype-claim-matrix/1`):
```json
{
  "reviewer": "actual acting agent and date",
  "collection_digest": "core.identity_hash(run)",
  "analyses": {"VIDEO_ID": "analysis.md SHA-256"},
  "metrics": {"VIDEO_ID": "community/metrics.json SHA-256, with --community"},
  "columns": ["VIDEO_ID:speaker", "VIDEO_ID:community"],
  "themes": [{"theme": "A claim two or more videos speak to",
              "cells": {"VIDEO_ID:speaker": "what the speaker says", "VIDEO_ID:community": "not discussed"},
              "evidence": {"VIDEO_ID:speaker": ["61:11", "f_0042.jpg"], "VIDEO_ID:community": []}}]
}
```
Speaker cells cite in-range timestamps, inspected frames or URLs; commenter cells cite `#rank` from that video's `top.json`. `not discussed` cells cite nothing.

`notebooklm/state.json`:
```json
{
  "account_label":"Pulse Vibe Daily","account_verified":true,
  "collection_key":"from run.json","notebook_title":"exact run title",
  "notebook_url":"observed supported notebook URL",
  "source_package_sha256":"current package.json hash",
  "observed_at":"actual ISO timestamp","observed_by":"acting agent",
  "browser_evidence":{"path":"local observation/screenshot receipt","bytes":1,"sha256":"actual"},
  "sources":[{"sha256":"packet hash","remote_source_id":"observed UI identity","visible_title_verified":true}],
  "retrieval_checks":[{"question":"source-specific question","source_citation":"observed citation","matches_local_evidence":true}],
  "audio":{"status":"ready","title":"observed","artifact_id":"observed","opened_and_checked":true,"source_package_sha256":"current"},
  "slides":{"status":"ready","title":"observed","artifact_id":"observed","opened_and_checked":true,"source_package_sha256":"current"}
}
```

While waiting, use queued/generating/waiting_quota/blocked states and record pending reasons. Never populate ready fields in anticipation of success. Save capability/QA evidence without credentials, login codes or private account tokens.

## New source-first full-run acceptance

The historical shapes above remain readable. Newly initialized full runs automatically require the following additional fields; a legacy run is not silently upgraded.

`full-review.json` also binds `source_map_sha256` and records these actual review attestations as `true`: `substance_preserved`, `visuals_integrated`, `source_first`, `project_applications_separate`, `stale_uncertainties_resolved`. Source map sections are ordered, nonoverlapping inclusive cue ranges covering all canonical cues. Each has a nonempty heading present in the account; `frame_names` contains the inspected frames integrated into that section, including every written visual observation somewhere in the map. These are structural checks plus attestations, not a proof that mapped prose preserves the full source.

`infographic-brief.json`:
```json
{
  "enhanced_sha256": "current enhanced-transcript.md hash",
  "source_map_sha256": "current enhanced-source-map.json hash",
  "composition": {"form": "parallel frameworks with annotated examples", "rationale": "Explain why this form matches the source relationships"},
  "concepts": [{"id":"actual-main-concept", "title":"Source-specific concept", "cue_indices":[0], "frames":["f_0010.jpg"], "represented_as":"What the image should explain about it"}]
}
```
Each concept cites valid caption indices, inspected frames, or both. The inventory must represent the major source concepts; no fixed count proves completeness.

`infographic.json` additionally binds `brief: EVIDENCE`, `enhanced_sha256` and:
```json
{
  "quality_review": {
    "reviewer":"actual acting reviewer and date",
    "concept_ids":["actual-main-concept"],
    "coverage_checked":true,
    "relationships_checked":true,
    "labels_checked":true,
    "legibility_checked":true,
    "source_specificity_checked":true,
    "review_notes":"Concrete observations from the generated image, with any revisions and remaining scope limits"
  }
}
```
All brief concept IDs must appear exactly once in the image review. Image/request/brief/source hashes bind the accepted revision. A later source or brief change makes the image review stale.

`notebooklm/package.json` carries `source_contract: one-video/1` and exactly one packet with a `video_id` for each unique video. It does not prepend a master or application source, combine videos, or split an oversized video. Packet contents are the neutral expanded account and written visual evidence; captions may additionally be retained in the packet. For `caption_mode: references`, the video URL is sufficient as a local reference; a second remote import is not required. `state.json.sources` records one distinct observed remote identity for each packet, bound to its hash, with the intended visible title verified. The source IDs/titles and retrieval content still require actual browser observation.
