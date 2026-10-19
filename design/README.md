# UI design source

This directory contains the version-controlled source specifications for the
Telegram Mini App UI. See [USAGE.md](USAGE.md) for the team workflow.

## Source of truth

- `tokens/` defines reusable visual values.
- `components/` defines reusable UI components.
- `pages/` defines approved page layouts and states.
- `penpot.json` identifies the generated Penpot target.
- `references/` contains input screenshots and other visual references.
- `exports/` contains generated artifacts and is not a source of truth.
- `schemas/` documents the supported JSON structures.

Business behavior remains defined in the workspace's
`meta/business-analytics/functionality/` documents. Business requirements are
inputs to design discussions; approved JSON in this directory is the UI design
source of truth.

Penpot is a generated visual representation of these files, not an independent
source of truth.

## Penpot conventions

- The target file is named by `generatedFileName` in `penpot.json`.
- The components page is named by `componentsPageName`.
- Page frames are named `Page/<PageName>`, for example `Page/Login`.
- Components are named `Component/<Name>`, for example `Component/Button`.
- Generated objects must be updated by stable name and never duplicated.

## Approval rule

When a page is derived from business requirements, the workflow must first
present a design proposal and wait for explicit user approval. It must not
change JSON or Penpot before approval.

## Idempotency rule

- Find an existing page frame or component before creating it.
- Update generated objects in place where possible.
- Delete and recreate generated objects only when incremental updates are not
  supported and doing so is safe.
- Never append duplicate page frames or components.
- Never delete manually maintained Penpot content.

## Token rule

- JSON references tokens by dotted paths such as `color.primary` or
  `spacing.md`.
- Reuse an existing token whenever it represents the intended value.
- Do not invent an arbitrary reusable color or dimension. Add it to
  `tokens/tokens.json` first.
- Validate token and component references before synchronizing Penpot.

## Requirement traceability

New page specifications should record their source documents and assumptions:

```json
{
  "requirements": {
    "sources": [
      "meta/business-analytics/functionality/user-profiles.md"
    ],
    "approvedAssumptions": [
      "Projects and reviews are shown in separate sections"
    ]
  }
}
```

Existing pages that predate this workflow may omit `requirements` until they
are next discussed and approved.

## Validation

From the repository root, run:

```bash
python3 scripts/validate-design.py
```