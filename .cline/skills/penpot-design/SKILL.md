---
name: penpot-design
description: Synchronize approved library-first JSON specifications to native representative PrimeVue templates, custom components, and page instances in Penpot.
---

# Penpot design synchronization

JSON under `design/` is authoritative. Read `design/README.md`,
`design/penpot.json`, tokens, the PrimeVue registry, requested custom
components, and pages. Run `python3 scripts/validate-design.py` and stop on any
error. Require explicit approval for material changes. Authenticate read-only
and discover live IDs before writes.

## Targets

- PrimeVue templates: configured library page and
  `libraryComponents.componentPrefix + component`.
- Custom components: configured custom page and
  `customComponents.componentPrefix + name`.
- Feature pages: `featurePagePrefix + feature.label`.
- Page frames: `pageFramePrefix + page`.

## Synchronization order

1. Locate/create only the configured generated file and exact target pages.
2. Synchronize tokens as concrete values where supported.
3. Synchronize every used/changed PrimeVue registry component as a native
   reusable component. Use registry appearances/states as representative
   templates. Semantic recognizability is required; pixel parity is not.
4. Synchronize custom components as native components/`State` variant sets.
   Preserve nested library component copies from their composition trees.
5. Synchronize page frames. Render every `library-component` and
   `custom-component` as a native copy instance from the correct family.
6. Re-read and verify names, variants, source families, nested instances,
   containment, and duplicates.

Penpot output is a reference-quality layout and implementation guide, not a
pixel-perfect browser specification. Preserve hierarchy, readable content,
sensible proportions, approximate token alignment, and recognizable controls.
Exact CSS metrics and minor cosmetic differences are not acceptance criteria.

## Write and visual-sanity checks

Before a write, capture the target page/frame IDs, bounds, component roots, and
the same summary for nearby generated sibling frames. Inspect the current
bounds of objects that will be changed instead of guessing from JSON alone.

After a write, re-read the changed scope and check for material defects:

- clipped, empty, overlapping, or implausibly narrow text;
- labels outside controls or obviously misaligned within them;
- controls with disproportionate dimensions or excessive unexplained space;
- obviously unusable mobile targets;
- descendants outside their component root or page frame;
- detached library/custom instances, duplicate generated roots, or changed
  sibling frame IDs, bounds, and component roots.

Use broad visual judgment rather than pixel-level tolerances. A tiny alignment
difference is acceptable; unreadable labels, broken hierarchy, clipping, and
grossly oversized controls are not.

When a visual reference is provided, inspect it before writing, identify the
important hierarchy and proportions, and use it as guidance rather than a
pixel-perfect target.

For visual verification, try one full-frame PNG export. If it fails, try one
smaller export of the changed section or control. Do not repeat failed exports
or run them concurrently with other Penpot operations. If both attempts fail,
complete structural and bounds inspection, report that visual export was
unavailable, and require manual visual review; do not claim visual verification.

Do not create documentation boards or detached substitutes. Library main
instances belong on the library page; custom main instances/variant containers
belong on the custom page; generated screen artwork belongs inside canonical
page frames. Update by exact stable name and never delete ambiguous/manual
content.

If native components, variants, nested instances, hierarchy, or verification
are unsupported, stop and report the precise block. A successful write call
alone does not prove visual correctness.

Report validated inputs, targets, objects changed, library/custom instance
verification, unsupported properties, visual-review availability, and manual
follow-up.