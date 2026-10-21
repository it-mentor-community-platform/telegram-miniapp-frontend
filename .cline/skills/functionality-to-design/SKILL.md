---
name: functionality-to-design
description: Turn business requirements and visual references into an approval-first UI design proposal, then approved JSON design specifications for this Telegram Mini App. Use when designing or revising pages, components, states, navigation, or information architecture from files in the meta workspace.
---

# Functionality to design

Convert product requirements into the version-controlled design format under
`design/`. Follow `design/README.md` and `design/USAGE.md`.

## Source hierarchy

1. Business behavior comes from referenced documents, normally under
   `../meta/business-analytics/functionality/`.
2. Approved UI decisions are recorded in `design/tokens/`,
   `design/components/`, and `design/pages/`.
3. Penpot is generated output, not the source of truth.
4. Screenshots provide visual direction only unless the user explicitly says
   otherwise.

## Phase 1: inspect and propose

Before proposing a design:

1. Read every requirement and reference named by the user.
2. Read `design/tokens/tokens.json`, relevant component specifications, related
   page specifications, and `design/penpot.json`.
3. Inspect related Penpot objects read-only when authentication and tooling are
   available.
4. Separate user-facing requirements from backend-only behavior.
5. Identify missing product decisions instead of silently inventing them.

Present a concrete proposal covering:

- target users and goals;
- pages, entry points, and navigation;
- each page's feature key, feature label, local path, Penpot feature page, and
  stable page-frame name;
- information hierarchy;
- actions, permissions, and validation;
- reusable components and variants;
- loading, empty, error, success, and permission-denied states;
- mobile behavior and any requested responsive behavior;
- assumptions and unresolved questions;
- tokens and existing components to reuse.

Do not edit JSON, frontend code, or Penpot during this phase. Wait for explicit
approval such as "Approved" or a direct instruction to implement the proposal.
Comments such as "looks good" or "probably fine" are not sufficient when
material assumptions remain unresolved.

If feedback materially changes structure or behavior, present the revised
proposal and obtain approval again.

## Phase 2: implement an approved proposal

After explicit approval:

1. Update reusable tokens first. Reuse an existing token whenever it represents
   the intended value.
2. Update or add reusable component specifications next.
3. Update or add page specifications last.
4. Add requirement traceability to new or materially revised pages:

   ```json
   "requirements": {
     "sources": ["meta/business-analytics/functionality/example.md"],
     "approvedAssumptions": ["An explicitly approved design decision"]
   }
   ```

5. Store each page at `design/pages/<feature>/<screen>.page.json`, with exactly
   one kebab-case feature directory. Related screens share that directory.
6. Add feature metadata to every page and keep it consistent with the path:

   ```json
   "feature": {
     "key": "user-profile",
     "label": "User Profile"
   }
   ```

   The Penpot feature page is `featurePagePrefix + feature.label`; the screen
   frame is `pageFramePrefix + page`.
7. Use stable PascalCase component and page names. File names use kebab-case
   with `.components.json` or `.page.json` suffixes.
8. Give semantic names to structural page nodes so their hierarchy can be
   represented inside the generated page frame.
9. Reference reusable values with dotted token paths such as `color.primary`,
   `spacing.md`, `radius.lg`, and `font.size.md`.
10. Reference components by their declared `name` and a declared variant.
11. Preserve existing approved behavior unless the new approval changes it.

Run:

```bash
python3 scripts/validate-design.py
```

Fix every validation error before synchronization. Then use the
`penpot-design` workflow if synchronization was requested.

## Completion report

Report:

- requirements and references used;
- approved assumptions;
- JSON files created or changed;
- tokens and components reused or introduced;
- validation result;
- Penpot result, if synchronization was requested;
- unsupported operations and manual review still required.
