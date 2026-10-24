# Repository design workflow

## Sources and approval

- Business behavior comes from referenced documents in the sibling `meta`
  workspace.
- Approved JSON under `design/` is the UI source of truth; Penpot is generated.
- `design/exports/` is generated output.
- Generated Penpot mockups are reference-quality layout and implementation
  guides, not pixel-perfect browser specifications. They must communicate clear
  hierarchy, readable content, sensible proportions, and recognizable controls.
- Present material designs and schema/custom-component changes for explicit
  approval before writing JSON or Penpot.

## Library-first JSON

- Inspect `design/libraries/primevue.library.json` before proposing components.
- Use `type: library-component` for registered generic controls.
- Compose one-off arrangements directly on pages.
- Use `type: custom-component` only for recurring domain concepts with an
  approved rationale in `design/components/*.component.json`.
- Never create a custom wrapper merely to rename a registered control.
- Keep runtime props in `props`; keep product behavior in `action`.
- `design.appearance` and `design.state` are representative Penpot metadata and
  must be allowlisted by the registry.
- Update registry, then tokens, then custom components, then pages.
- Store pages at `design/pages/<feature>/<screen>.page.json` and record sources
  and assumptions on new or materially revised pages.
- Run `python3 scripts/validate-design.py` before Penpot synchronization.

## Penpot safety

- Read `design/penpot.json` and discover current IDs before every sync.
- Authenticate read-only before writes.
- Before any artwork writes, compare required composition with live source mains
  and record planned operations/destinations and API evidence per
  `design/CONFORMANCE.md`. Method existence is not operation permission.
- Never call `appendChild`/`insertChild` on component copies or inherited
  containers, or reparent inherited descendants out of a copy. Inspect ancestry.
  Other structural mutations require context-specific documented support; do not
  probe by trial writes. Assemble complete new mains before registration/copying;
  nested copies remain structurally immutable. Incompatible trees require
  separate approval; no detaching, redraws, or sibling-overlay fallback.
- Validate destinations before creating instances. Use small write batches,
  record IDs immediately and re-read parentage/native links and settled bounds.
  On partial failure stop writes, collect a fresh complete snapshot and inventory
  partial objects. No automatic rollback/deletion without an authorized supported
  cleanup plan and fresh post-write preservation evidence.
- Missing pages require supported creation permission; never create a page before
  the baseline to evade preservation. Page-only scope does not permit main edits.
- Synchronize PrimeVue templates to the configured library page and prefix.
- Synchronize project custom components to the configured custom page/prefix.
- Both kinds must be native reusable components; custom components must retain
  nested library instances where specified.
- Multi-state custom components use native `State` variants matching JSON.
- Page library/custom nodes are native copy instances from the requested
  family. Detached reproductions are invalid.
- Representative semantic fidelity is required for library templates;
  pixel-for-pixel PrimeVue parity is not.
- Before writes, inspect and record the target bounds and nearby generated
  sibling frame summaries. After writes, re-read the changed scope and reject
  material clipping, unreadable labels, broken alignment, disproportionate
  controls, containment failures, detached instances, duplicates, and
  unintended sibling changes. Minor pixel variance is acceptable.
- When a visual reference is supplied, inspect it and follow its important
  hierarchy and proportions without treating it as a pixel-perfect target.
- Visual export fallback is bounded: try the full frame once, then one smaller
  changed section. If both fail, complete structural/bounds checks, report that
  visual verification is unavailable, and require manual review.
- Keep generated artwork in canonical frames, update by stable name, avoid
  duplicates, and never overwrite manual content.
- If required native operations are unsupported, stop and report the block.

## Review and reporting

- Design review is read-only unless fixes are requested.
- Report requirements, assumptions, registry changes, custom rationales,
  changed JSON, Penpot operations, validation, and remaining limitations.
- Never commit credentials, API tokens, or private screenshots.