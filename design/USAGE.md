# UI design workflow

## Workflow

```text
Business requirements
        ↓
Proposal: library components, inline compositions, custom components
        ↓
Explicit approval
        ↓
JSON source specifications
        ↓
Validation
        ↓
Penpot synchronization
        ↓
Structural and visual review
```

Do not modify JSON or Penpot while a material proposal is still under review.

## Component selection

For every UI concept ask:

```text
Does the PrimeVue registry provide the semantic control?
  Yes → use library-component.

Is it a small one-off arrangement of library controls and text?
  Yes → compose it directly on the page.

Is it a recurring product/domain concept?
  Yes → propose a custom-component with a rationale and library composition.

Otherwise → do not create a custom component.
```

Design proposals must make the source explicit:

| UI concept | Source |
|---|---|
| Primary action | PrimeVue Button |
| Specialization label | PrimeVue Tag |
| Category review card | Custom, composed from Card, Tag, and Button |

## PrimeVue registry

The allowlist is `design/libraries/primevue.library.json`. Add a component only
when a design requires it. Record its frontend import, design-relevant props and
slots, and representative Penpot appearances/states. Do not copy the entire
upstream API.

Use `library-component` nodes for registered controls. Keep navigation,
submission, commands, and external links under `action` rather than fake
PrimeVue props.

## Custom component workflow

A new custom component requires explicit approval and must explain why inline
composition or a registered library control is insufficient. Update in order:

1. library registry, when a new PrimeVue building block is needed;
2. tokens;
3. `design/components/<name>.component.json`;
4. pages.

Custom compositions should retain nested PrimeVue instances in Penpot and must
not redraw generic controls as rectangles/text.

## Pages

Store every page at `design/pages/<feature>/<screen>.page.json`. Its
`feature.key` must match the directory. Pages sharing a feature key use the same
feature label. Structural nodes have stable PascalCase names.

Example:

```json
{
  "$schema": "../../schemas/page.schema.json",
  "feature": { "key": "interval-repetition", "label": "Interval Repetition" },
  "page": "ReviewSession",
  "children": [
    {
      "type": "library-component",
      "library": "primevue",
      "component": "SelectButton",
      "props": { "options": ["0", "1", "2", "3", "4", "5"] },
      "action": { "type": "submit", "name": "saveRecallRating" },
      "design": { "appearance": "rating-scale", "state": "default" }
    }
  ]
}
```

## Approval

Explicit approval is required for new pages, material behavior changes, new
custom components, and changes to the library/schema contract. “Looks
interesting” and “probably fine” are not approvals.

## Validation

Run:

```bash
python3 scripts/validate-design.py
```

Validation rejects unknown library controls/props/slots, legacy
`type: component`, legacy `*.components.json`, missing custom variants,
composition cycles, invalid bindings, broken tokens, and invalid paths.

## Penpot synchronization

Synchronization order:

1. read `design/penpot.json` and discover current IDs;
2. authenticate with a read-only request;
3. synchronize representative native PrimeVue templates on
   `Library / PrimeVue`;
4. synchronize native custom components on `Components`, preserving nested
   PrimeVue instances;
5. synchronize pages using native library/custom instances;
6. re-read and verify stable names, variants, sources, containment, and
   duplicates.

PrimeVue templates need semantic recognizability, not pixel parity. Review
Button as a button, Toolbar as a header, ProgressBar as progress, and so on.
Exact CSS metrics, transitions, and browser rendering are not acceptance
criteria.

Generated Penpot pages are reference-quality layout and implementation guides.
They should communicate hierarchy, grouping, reading order, responsive/mobile
composition, readable content, and sensible relative proportions. Clipped or
unreadable text, labels outside controls, broken containment, obvious
misalignment, disproportionate controls, and excessive unexplained empty space
are defects. Small pixel differences and cosmetic runtime variance are not.

When a task supplies a visual reference, inspect it before synchronization and
use its important hierarchy and proportions as guidance. Exact pixel matching
is required only when a requirement explicitly says so.

For controls whose registry declares representative variants or sizes, every
JSON node must state them explicitly under `design`. Runtime choices remain in
`props`; for example, a filled normal Button uses `design.variant: filled` and
`design.size: normal` while omitting PrimeVue's runtime `variant` and `size`
props because those are the library defaults.

## Review and completion report

Review library-first selection, custom rationales, accessibility, states,
requirements, native Penpot instance sources, duplicate names, and page
containment. Before a write, record the target bounds/component roots and nearby
generated sibling frame summaries. Afterward, re-read them and check text
readability, approximate label alignment, relative proportions, containment,
instance ancestry, duplicates, and unintended sibling changes.

For visual verification, try one full-frame PNG export. If it fails, try one
smaller export of the changed section or control. Do not repeatedly retry or
run exports concurrently with other Penpot operations. If both fail, complete
the structural and bounds checks, report visual export as unavailable, and
request manual visual review. Do not claim visual verification.

Report changed JSON, registry entries, retained custom components, Penpot
operations, validation, unsupported tooling, and manual review needs.

Never commit credentials, tokens, or private screenshots. Never overwrite
manual Penpot content or claim synchronization/visual parity after a failed or
unverifiable operation.

## Repeatable drift audit

The drift audit derives its expectations from the approved JSON and checks the
live generated pages without modifying Penpot. Generate the self-contained
plugin-context JavaScript with:

```bash
python3 scripts/audit-penpot-drift.py --emit-penpot-js /tmp/audit-penpot-drift.js
```

Run that JavaScript through the authenticated Penpot plugin context. Its result
contains `ok`, `errors`, `warnings`, a portable `snapshot`, and `snapshotJson`
for direct file persistence. The comparison command accepts either the raw
`snapshot` object or the complete plugin result containing `snapshot`:

```bash
python3 scripts/audit-penpot-drift.py --snapshot /tmp/penpot-live-snapshot.json
```

The audit verifies canonical feature pages and frames, the JSON-derived
PrimeVue/custom family allowlist, exact custom-family placement and counts, and
exactly one component-record main plus visible native state roots for each
approved custom family. Generic PrimeVue template
counts are reported in the snapshot but are not compared one-to-one because
the representative rendering strategy may preserve a semantically equivalent
historical template. Main-less, unreferenced component records are reported as
warnings because the plugin API does not expose safe record deletion.
Legacy generated frame names in the form `Page / Name` are accepted only as an
unambiguous alias and reported as warnings when the plugin API does not persist
the configured `Page/Name` normalization.