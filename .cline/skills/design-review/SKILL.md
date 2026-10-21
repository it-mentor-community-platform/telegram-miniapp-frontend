---
name: design-review
description: Review business requirements, JSON design specifications, and generated Penpot objects without changing them. Use for requirement coverage, token/component integrity, structural consistency, duplicate detection, accessibility concerns, and pre-merge design review.
---

# Design review

Perform a read-only review unless the user explicitly asks to fix findings.
Distinguish confirmed defects from recommendations and from checks blocked by
tooling.

## Inputs

Read, as applicable:

- referenced business requirements under `../meta/`;
- `design/README.md` and `design/USAGE.md`;
- `design/tokens/tokens.json`;
- relevant `design/components/*.components.json`;
- relevant `design/pages/**/*.page.json`;
- `design/penpot.json`;
- relevant Penpot projects, files, pages, components, and shapes read-only.

Run:

```bash
python3 scripts/validate-design.py
```

Do not modify JSON or Penpot merely to make the review pass.

## Review checklist

### Requirement coverage

- Each user-facing requirement has a corresponding page, action, state, or an
  explicit reason for exclusion.
- Backend-only requirements are not exposed as arbitrary UI.
- Roles, permissions, validation, and error behavior are represented.
- `requirements.sources` and `approvedAssumptions` are accurate when present.
- Unapproved assumptions are called out.

### Information architecture and interaction

- Primary tasks and calls to action are clear.
- Navigation and back behavior are understandable in a Telegram Mini App.
- Loading, empty, error, success, disabled, and permission states are covered.
- Content order and progressive disclosure fit a mobile-first viewport.

### Design-system integrity

- Reusable values use existing tokens or introduce intentional new tokens.
- Repeated patterns use components rather than page-specific copies.
- Component references and variants exist.
- Names are stable and unique.
- Text contrast, target size, focus/disabled states, labels, and content clarity
  receive an accessibility review.

### Penpot consistency

- The configured project and generated file are used.
- Each page file is under `design/pages/<feature>/<screen>.page.json`, its
  `feature.key` matches the directory, and pages sharing a feature key use one
  consistent feature label.
- Each feature maps to the Penpot page
  `featurePagePrefix + feature.label`.
- Components and page frames match configured stable-name prefixes.
- There are no duplicate generated names.
- Each `Page/<PageName>` frame is on the correct feature page, and generated
  page artwork is contained inside that frame rather than left loose at the
  feature-page root.
- Named JSON sections and layout nodes have corresponding nested generated
  containers where the MCP supports them.
- Generated component layers are contained inside their canonical
  `Component/<Name>` frame rather than left loose at the components-page root.
- Dimensions, colors, typography, spacing, and visible content agree with JSON.
- Manual content has not been overwritten.
- Unsupported MCP properties and visual checks are explicitly identified.

## Findings format

List findings first, ordered by severity:

1. **Blocking** — unsafe synchronization, invalid references, missing approval,
   duplicate generated objects, or major requirement omissions.
2. **Major** — incorrect behavior, hierarchy, permissions, or important states.
3. **Minor** — consistency, accessibility, maintainability, or polish issues.

For each finding include:

- severity and concise title;
- exact file/path, JSON location, or Penpot object;
- evidence;
- user or workflow impact;
- recommended correction.

Then include:

- assumptions and questions;
- validation and Penpot checks completed;
- checks not performed and why;
- a short overall assessment.

If no findings exist, say so explicitly and still state residual risks such as
unavailable pixel-level comparison.
