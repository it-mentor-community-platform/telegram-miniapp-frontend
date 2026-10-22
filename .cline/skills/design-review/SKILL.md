---
name: design-review
description: Read-only review of requirements, library-first JSON specifications, and generated Penpot library/custom instances.
---

# Design review

Review without changes unless fixes are explicitly requested. Read referenced
requirements, design documentation, tokens, PrimeVue registry, custom
components, pages, Penpot config, and related live Penpot objects. Run
`python3 scripts/validate-design.py`.

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