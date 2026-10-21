# Repository design workflow

These rules apply to UI design work in this repository.

## Sources of truth

- Business behavior is defined by referenced documents in the sibling `meta`
  workspace.
- Approved UI specifications under `design/` are the design source of truth.
- Penpot is generated output and must not be the only place a design change is
  made.
- `design/exports/` is generated output, not an editable source.

## Approval boundary

- For a new design or a material change derived from requirements, inspect the
  requirements and existing design system, present a proposal, and wait for
  explicit approval before changing design JSON or Penpot.
- Do not interpret tentative feedback as approval.
- If review feedback materially changes the proposal, request approval for the
  revised proposal.

## JSON-first implementation

- Update tokens, then components, then pages.
- Reuse existing tokens and components when they match the intent.
- Store every page at `design/pages/<feature>/<screen>.page.json`, with exactly
  one kebab-case feature directory level. The page's `feature.key` must match
  that directory and `feature.label` provides its Penpot display name.
- Record requirement sources and approved assumptions on new or materially
  revised pages.
- Run `python3 scripts/validate-design.py` after changing design JSON and before
  Penpot synchronization.

## Penpot safety

- Read `design/penpot.json` and discover current IDs before every sync.
- Check authentication with a read-only request before writes.
- Synchronize each feature to
  `featurePagePrefix + feature.label` and each screen to
  `pageFramePrefix + page`.
- Keep generated screen layers inside their canonical page frame and generated
  component layers inside their canonical component frame. Do not leave loose
  generated artwork at a Penpot page root.
- Update generated objects by exact stable name and never create duplicates.
- Never delete or overwrite manually maintained Penpot content.
- Do not claim synchronization or visual parity when a call failed or tooling
  cannot verify it.
- Report unsupported MCP operations and require manual visual review when
  screenshots or exports are unavailable.

## Verification and reporting

- Design review is read-only unless fixes are explicitly requested.
- Report requirement inputs, approved assumptions, changed JSON, reused or new
  tokens/components, Penpot operations, validation results, and remaining
  limitations.
- Never commit credentials, API tokens, private screenshots, or other secrets.
