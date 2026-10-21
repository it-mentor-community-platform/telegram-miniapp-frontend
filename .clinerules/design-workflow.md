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
- Every component specification must synchronize to a native reusable Penpot
  library component. A multi-state specification must use a native variant set
  whose `State` values exactly match the JSON variant names.
- Never substitute a documentation board, specification card, group, or
  detached drawing for a native component. If native component or variant
  creation is unsupported, stop and report the synchronization as blocked.
- Every page node with `type: component` must synchronize to a component copy
  instance of the requested family and variant. Detached visual reproductions
  are invalid.
- Keep generated screen layers inside their canonical page frame. Native
  component main instances and variant containers belong on the configured
  components page without documentation-board wrappers.
- Update generated objects by exact stable name and never create duplicates.
- Never delete or overwrite manually maintained Penpot content.
- Do not claim synchronization or visual parity when a call failed or tooling
  cannot verify it.
- Report unsupported MCP operations and require manual visual review when
  screenshots or exports are unavailable.
- Verify native main instances, variant coverage, page copy instances, and the
  absence of generated component documentation boards before reporting success.

## Verification and reporting

- Design review is read-only unless fixes are explicitly requested.
- Report requirement inputs, approved assumptions, changed JSON, reused or new
  tokens/components, Penpot operations, validation results, and remaining
  limitations.
- Never commit credentials, API tokens, private screenshots, or other secrets.
