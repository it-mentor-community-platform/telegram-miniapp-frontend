---
name: penpot-design
description: Synchronize approved JSON design specifications in this repository to the configured Penpot generated file, or inspect Penpot synchronization status. Use for Penpot sync, generated components/pages, authentication checks, and structural comparison with design/penpot.json.
---

# Penpot design synchronization

Synchronize the JSON source of truth under `design/` to the target configured in
`design/penpot.json`. Never treat Penpot as the authoritative design source.

## Preconditions

1. Read `design/README.md`, `design/penpot.json`,
   `design/tokens/tokens.json`, and all requested component/page JSON files.
2. Run `python3 scripts/validate-design.py` and stop on any error.
3. Confirm that the requested design is already approved. If synchronization
   would implement a new or materially changed design without explicit
   approval, switch to a proposal and do not write JSON or Penpot.
4. Check Penpot authentication with read-only profile/team/project operations.
   If authentication fails, report the exact error and do not attempt writes.

## Target discovery

Resolve targets by stable names from `design/penpot.json`:

- project: `projectName`;
- generated file: `generatedFileName`;
- component page: `componentsPageName`;
- feature page: `featurePagePrefix + feature.label` from the page JSON;
- page frames: `pageFramePrefix + page`;
- native component families: `componentPrefix + name`.

For a page at `design/pages/<feature>/<screen>.page.json`, require
`feature.key == <feature>`. If the canonical page frame exists on another
Penpot page, stop and report the mismatch instead of creating a duplicate.

List existing projects, files, pages, components, and shapes before writing.
Never assume IDs from an earlier session.

## Safe synchronization order

1. Locate or create only the configured generated file.
2. Locate or create the configured components page.
3. Synchronize tokens as concrete Penpot properties; do not invent values.
4. Synchronize components before pages. Create native library components with
   `penpot.library.local.createComponent(...)`. For multiple JSON states, create
   one complete main component per state and combine them into a native variant
   set with property `componentVariantProperty` and exact JSON variant values.
5. Locate or create the exact feature page after every referenced component
   exists.
6. Synchronize the page frame on that feature page. Keep all generated page
   artwork inside the canonical page frame and mirror named JSON structural
   nodes as nested generated containers where supported.
7. Render every page node with `type: component` as a copy instance from the
   native library component and select its requested variant. Apply supported
   property overrides without detaching the instance.
8. Feature-page roots should contain canonical `Page/...` frames. The
   components page should contain native main instances and native variant
   containers only; do not create enclosing documentation boards or component
   specification cards.
9. Re-read generated objects and check names, counts, dimensions, colors,
   typography, duplicate stable names, native main-instance status, variant
   coverage, and page copy-instance status.

## Native component requirements

- A component JSON file with one variant maps to one normal native component.
- A component JSON file with multiple variants maps to one native variant set.
- Variant values must exactly equal the JSON keys and use the configured
  `componentVariantProperty` (normally `State`).
- Composite components should use nested component instances where the JSON
  design system defines reusable primitives.
- Component references on pages must remain usable instances. A detached clone,
  group, board, or manually redrawn substitute is a synchronization failure.
- A board is acceptable only when Penpot uses it as an actual component main
  instance or variant container. A board that merely lists variants, layers, or
  component documentation is prohibited.

## Active-page writes

Penpot may reject hierarchy changes on pages other than `penpot.currentPage`.
Before modifying a page:

1. call `penpot.openPage(page)`;
2. confirm in a separate read that `penpot.currentPage.id == page.id`;
3. write only that page in the current operation;
4. re-read the page before switching to another page.

Do not combine writes to multiple Penpot pages in one call. A failed multi-step
call may have applied earlier operations; always re-read state after any error
before retrying.

Follow `renderStrategy` from `design/penpot.json`. For `replace-by-name`:

- find an existing generated object by exact stable name;
- update it in place where supported;
- recreate it only when incremental update is unsupported and the object is
  clearly generated;
- never append a duplicate object with the same stable name;
- never delete or overwrite manually maintained content.

## Tooling limitations

Do not claim success for an operation the available MCP tools cannot perform.
In particular:

- if parent/child hierarchy, auto-layout, component variants, exports, or
  screenshots cannot be represented, preserve the JSON and report the gap;
- never replace a required native component or component instance with flat
  artwork; stop the synchronization instead;
- a successful MCP call proves only that the call completed, not that the
  visual result is correct;
- request manual visual review when screenshot/export comparison is
  unavailable.

## Failure handling

- Authentication or Cloudflare failure: stop before writes and report it.
- Missing target: create it only when the configured scope is unambiguous.
- Duplicate stable name: stop, identify the canonical generated object, and do
  not delete anything ambiguous.
- Partial failure: keep JSON unchanged, enumerate successful and failed Penpot
  operations, and never report full synchronization.

## Completion report

Report:

- validated JSON inputs;
- target project, file, and pages;
- objects created, updated, recreated, or left unchanged;
- duplicate-name and structural verification;
- native component families, variants, main instances, and page copy instances;
- unsupported properties or operations;
- whether automated visual comparison was available;
- manual review required.
