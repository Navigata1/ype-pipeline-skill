# Source depth and visual acceptance

New full runs carry `source_fidelity_contract: timed-source-account/1`, `infographic_quality_contract: source-coverage/1` and `notebook_source_contract: one-video/1`. New quick and full runs carry `editorial_contract: source-first/1`. Historical runs are evaluated under their recorded contract; never add fields to an old run to imply a review occurred.

## The expanded source account

Read the complete canonical transcript and make an ordered section map covering every caption cue once. Work section by section when the source is long. Each meaningful timed section of `enhanced-transcript.md` must preserve:

- The full cleaned substance of what was said: explanation, mechanisms, examples, procedures, comparisons, qualifications and conclusions. Remove duplicated captions and disfluency without reducing the account to takeaways. Faithful paraphrase is appropriate; a summary followed by the untouched captions does not meet this requirement.
- What inspected frames add: displayed labels, diagrams, settings, code, demonstrations and important actions, including information not read aloud. Transcribe precisely when legible; describe observed relationships and actions. Attach manifest frame names and source times.
- The combined understanding, distinguishing source claims, visual observations and analyst inference. Preserve competing claims and speaker qualifications. Qualify uncertainty locally rather than replacing the source's explanation with warnings.

After targeted frame inspection, revise the relevant section and resolve stale “not inspected/unknown” passages. An appended discovery does not repair an inconsistent body. Map every written visual observation into a source section. A cue range, frame count or word floor proves accounting only; compare the actual prose with the full source before attesting preservation. Sampling cannot guarantee every visible detail was recovered; record the residual limits honestly and recapture consequential illegible material where feasible.

Keep `analysis.md`, `enhanced-transcript.md`, `intelligence-report.md` and the neutral `master-compilation.md` about the video's own subject. Preserve project applications in `project-applications.md` with source citations and clear inference. User context does not silently authorize interpreting every video through that project. The report may expose this separate document; default per-video NotebookLM sources exclude it. Audience reception remains an opt-in, separately attributed analytical layer.

## Infographic design and review

Before generation, inventory the video's major concepts in `infographic-brief.json`. Each concept needs an ID, title, caption/frame evidence and a concrete `represented_as` description. Include the principal branches of the subject, substantive examples and distinctions that make this video useful. This inventory is an editorial judgment, not an automatic extraction of the first few analysis claims.

Choose a visual form from the actual relationships: a comparison, annotated demonstration, hierarchy, causal map, parallel frameworks, layered system or genuine sequence. Arrows encode a supported sequence, dependency or cause. Parallel controls do not become sequential stages for visual convenience. Richness means explanatory content and relationships, rather than extra decoration. A compact overview can omit fine detail, but it must preserve the major conceptual structure and point to the expanded source for depth. If that needs several panels within the per-video infographic, design them deliberately.

Use the same evidence packet for the brief and generation request. Do not starve the image model with three generic labels and a demand for a premium look. Supply accurate terminology, source-specific examples, substantive panel content and the intended relationships while leaving creative freedom in composition.

Review the actual generated original at reading size and enlarged detail:

1. **Coverage:** account for every main concept in the brief. Missing major branches require revision, not a passing note.
2. **Relationships:** comparisons, dimensions and causality match the source; the layout does not invent an order.
3. **Labels:** names, products, numbers and attribution agree with the enriched source. Distinguish a demonstrated tool from a comparison.
4. **Legibility:** explanatory content is readable and the hierarchy supports understanding.
5. **Specificity:** the image teaches this video. If swapping its title would make it fit many unrelated videos, improve the brief and regenerate.

Use cross-video review checkpoints to catch template drift. A few diverse examples at the start and small batches scaled to complexity help; no fixed batch size proves model capacity. Each video gets its own complete context packet. Judge the image against the source, not only against neighboring images.

## Two gates

`verify` checks required structure, cue coverage, evidence references, hashes, concept accounting and recorded acceptance. It cannot independently prove full preservation, model provenance, creativity, image understanding or remote actions. The acting reviewer must perform the source and image comparisons and record the detailed receipts in `schemas.md`. A mechanically valid file is not semantic acceptance; unresolved substantive or visual failures remain pending.
