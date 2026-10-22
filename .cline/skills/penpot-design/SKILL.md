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

Do not create documentation boards or detached substitutes. Library main
instances belong on the library page; custom main instances/variant containers
belong on the custom page; generated screen artwork belongs inside canonical
page frames. Update by exact stable name and never delete ambiguous/manual
content.

If native components, variants, nested instances, hierarchy, or verification
are unsupported, stop and report the precise block. A successful call does not
prove visual correctness; request manual review when exports are unavailable.

Report validated inputs, targets, objects changed, library/custom instance
verification, unsupported properties, visual-review availability, and manual
follow-up.