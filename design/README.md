# UI design source

This directory contains the version-controlled source specifications for the
Telegram Mini App UI. See [USAGE.md](USAGE.md) for the team workflow.

## Source of truth

- `tokens/` defines reusable visual values.
- `components/` defines reusable UI components.
- `pages/` defines approved page layouts and states. Every page must use exactly
  one feature directory: `pages/<feature>/<screen>.page.json`, for example
  `pages/home/homepage.page.json`.
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
- Product pages are grouped by feature on Penpot pages named
  `featurePagePrefix + feature.label`, for example `Pages / Home`.
- Page frames are named `Page/<PageName>`, for example `Page/Login`.
- Native reusable component families are named `Component/<Name>`, for example
  `Component/Button`.
- Named sections and layout nodes in page JSON must be represented as nested
  generated layers inside their `Page/<PageName>` frame.
- Every component specification must become a native Penpot library component.
  Specifications with multiple variants become native variant sets using the
  `State` property and exact JSON variant names.
- Page component nodes must be native copy instances. Detached drawings and
  flattened or redrawn substitutes are invalid.
- The components page contains native main instances and variant containers,
  not documentation boards that list component names, states, or layers.
- Generated page artwork must be contained by its canonical page frame. It must
  not remain loose at a Penpot page root.
- Generated objects must be updated by stable name and never duplicated.

## Page organization

Each page specification must declare its feature:

```json
{
  "feature": {
    "key": "home",
    "label": "Home"
  },
  "page": "Homepage"
}
```

The contract is:

```text
Local file:          design/pages/<feature.key>/<screen>.page.json
Penpot feature page: featurePagePrefix + feature.label
Penpot page frame:   pageFramePrefix + page
```

Feature directories and screen filenames use kebab-case. `feature.key` must
match the directory exactly. Pages with the same feature key must use the same
feature label, and one feature label may not represent multiple feature keys.
Structural `section`, `row`, `column`, and `grid` nodes must have stable
PascalCase names so synchronization and review can map their Penpot containers.

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
- Never replace a native component, variant, or page instance with a
  documentation board or detached artwork.
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