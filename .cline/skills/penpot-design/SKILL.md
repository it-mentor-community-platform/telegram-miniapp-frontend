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
- page frames: `pageFramePrefix + page`;
- generated components: `componentPrefix + name`.

List existing projects, files, pages, components, and shapes before writing.
Never assume IDs from an earlier session.

## Safe synchronization order

1. Locate or create only the configured generated file.
2. Locate or create the configured components page.
3. Synchronize tokens as concrete Penpot properties; do not invent values.
4. Synchronize components before pages.
5. Synchronize page frames after every referenced component exists.
6. Re-read generated objects and check names, counts, dimensions, colors,
   typography, and duplicate stable names.

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
- do not replace real components with misleading flat artwork without saying
  so;
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
- unsupported properties or operations;
- whether automated visual comparison was available;
- manual review required.
