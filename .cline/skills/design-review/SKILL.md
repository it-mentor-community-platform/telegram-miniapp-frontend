---
name: design-review
description: Read-only review of requirements, library-first JSON specifications, and generated Penpot library/custom instances.
---

# Design review

Review without changes unless fixes are explicitly requested. Read referenced
requirements, design documentation, tokens, PrimeVue registry, custom
components, pages, Penpot config, and related live Penpot objects. Run
`python3 scripts/validate-design.py`.

## Mandatory live structural gate

Read `design/CONFORMANCE.md` and `design/penpot.json`. JSON-only reviews remain
supported: validate and review the specifications, but explicitly report live
structural and visual verification as **not performed**. Never infer live
conformance from JSON validation, counts, old snapshots, or a successful sync.

Whenever claiming live structural verification:

1. Authenticate read-only and discover the current configured file/page/object
   IDs. Generate a fresh collector with
   `python3 scripts/audit-penpot-drift.py --recursive --emit-transfer-js /tmp/review-collect.js`
   and execute its exact body in the plugin context. Do not mutate artwork,
   stamp identities, repair drift, or synchronize templates during review.
2. Follow the network-free chunk handoff in `design/CONFORMANCE.md`: assemble
   all ordered chunks from the same immutable capture, decode with
   `--recursive --decode-transfer /tmp/review-transfer.json --snapshot-output /tmp/review.json`,
   and keep snapshots/credentials untracked. Do not rely on localhost fetch,
   summarized evidence, or stored snapshots from a previous task. Successful
   decoding alone is not structural verification.
3. Run the Python recursive comparator. For whole-file review use
   `python3 scripts/audit-penpot-drift.py --recursive --snapshot /tmp/review.json`.
   For selected scopes discover exact names with `--recursive --manifest`, then
   use `--recursive --snapshot /tmp/review.json --inspect --scope <exact-scope>`
   (repeat `--scope` as needed). Inspection still requires complete, fresh
   full-file collection; it does not check outside-scope preservation or imply
   whole-file conformance. Never manufacture a baseline or compare a snapshot
   against itself to obtain a scoped review PASS. Do not use `--allow-family`.
4. Report **PASS / FAIL / BLOCKED**, exact requested scopes and checked family/
   source-linkage coverage, snapshot file ID and freshness/completeness, issues,
   and that scoped inspection does not check preservation. Convert observed
   error diagnostics into findings with exact paths/object IDs, evidence,
   impact, and correction. **BLOCKED** means incomplete verification, not a
   proven artwork defect; report any independent observed errors separately.
   Unsupported evidence, missing transport, stale/incomplete collection, or
   unavailable tools must never produce an unqualified all-clear. BLOCKED need
   not halt independent requirements, JSON, accessibility, or visual checks.

The legacy count audit and ad hoc agent inspection are diagnostic only, not
substitutes for this gate. A structural PASS does not prove requirements,
runtime accessibility, visual quality, or every library appearance/state.
Keep those checks separate. This is an instruction-based workflow, not an
automatic hook for manual Penpot edits.

## Checks

- Every user-facing requirement maps to a page/action/state or justified
  exclusion; roles, validation, and failure states are represented.
- Generic controls use registered `library-component` nodes.
- Page-local composition is preferred over unjustified custom components.
- Every custom component has a domain rationale, valid props/variants, and
  non-cyclic composition using nested library instances where applicable.
- Library props, slots, actions, appearances, states, bindings, tokens, and
  references are valid.
- Accessibility covers labels, target size, contrast, focus/disabled/loading
  states, keyboard behavior, and content clarity.
- PrimeVue Penpot templates are native, correctly named, recognizable as their
  controls, and approximately token-aligned. Cosmetic runtime differences are
  not defects.
- Penpot mockups provide reference-quality hierarchy and layout guidance, not
  pixel-perfect implementation specifications. Exact CSS metrics and minor
  cosmetic variance are not defects.
- Text is readable and not materially clipped, overlapping, or implausibly
  constrained; labels remain within controls and are approximately aligned.
- Spacing, relative proportions, information hierarchy, and mobile composition
  are sensible. Grossly oversized controls, excessive unexplained empty space,
  and obviously unusable targets are defects.
- Custom Penpot families/variants are native and retain specified nested
  library copies.
- Page nodes are instances from the correct library/custom family, frames are
  on correct feature pages, generated content is contained, and stable names
  are unique.
- Detached substitutes, component documentation boards, unknown library
  controls, ambiguous legacy nodes, and generic custom duplicates are blocking.

List findings by Blocking, Major, then Minor, with exact path/object, evidence,
impact, and correction. State assumptions, checks completed, checks blocked,
and residual manual visual-review risk even when no findings exist. When a
visual reference is supplied, inspect it and state which hierarchy and
proportion cues were followed; do not score pixel-by-pixel similarity. If
exports are unavailable, review live structure and bounds but explicitly mark
visual verification as blocked.
Try a full-frame export once, then one smaller section if it fails. If both
fail, complete available structural/bounds checks and require manual visual
review; do not claim visual verification.