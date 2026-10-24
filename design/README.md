# UI design source

Recursive live acceptance, identity stamping and supported contract coverage
are specified in [CONFORMANCE.md](CONFORMANCE.md). Count-only audits are not
structural conformance gates.

This directory contains the version-controlled source specifications for the
Telegram Mini App UI. Business behavior remains defined under the sibling
`meta/business-analytics/functionality/` workspace. Penpot is generated output,
not an independent source of truth.

## Directory contract

- `tokens/` defines reusable visual values.
- `libraries/` defines curated external UI-library contracts. The current
  runtime library is PrimeVue 4.
- `components/` contains project-owned custom components only.
- `pages/<feature>/<screen>.page.json` defines approved screens.
- `schemas/` contains JSON Schema documentation for these structures.
- `penpot.json` configures generated Penpot targets and stable names.
- `references/` contains approved visual inputs.
- `exports/` is generated output and is not editable source.

## Library-first rule

Choose UI building blocks in this order:

1. Use a registered PrimeVue component with `type: library-component`.
2. Compose registered PrimeVue components and structural nodes directly on the
   page for a one-off arrangement.
3. Add `type: custom-component` only for a recurring product/domain concept
   without a suitable direct library equivalent.

Minor visual differences from PrimeVue do not justify a custom replacement.
Do not add custom wrappers that merely rename Button, Card, InputText, Tag,
Toolbar, ProgressBar, or another registered generic control.

## Node examples

PrimeVue control:

```json
{
  "type": "library-component",
  "library": "primevue",
  "component": "Button",
  "props": {
    "label": "Продолжить",
    "icon": "pi pi-arrow-right",
    "iconPos": "right",
    "severity": "primary"
  },
  "action": {
    "type": "navigate",
    "target": "RepetitionDashboard"
  },
  "design": {
    "appearance": "primary",
    "variant": "filled",
    "size": "normal",
    "state": "default"
  }
}
```

Project-owned domain component:

```json
{
  "type": "custom-component",
  "component": "CategoryReviewCard",
  "variant": "active",
  "props": {
    "title": "Core",
    "specialization": "Java",
    "due": "6 к повторению",
    "new": "24 новых",
    "total": "38 всего",
    "primaryAction": "Повторить"
  }
}
```

`props` contains runtime-library or custom-component values. Product behavior
belongs in `action`, not in invented library props. `design.appearance`,
`design.variant`, `design.size`, and `design.state` select a representative
Penpot template and must be declared in the library registry. Representative
values such as a normal size or a filled default variant remain design metadata
when the runtime library expresses them by omitting a prop.

## Custom components

### RoadmapProjectCard

`RoadmapProjectCard` has native `State=submitted` / `State=notSubmitted`
variants. Its root Card uses the explicitly configured custom structural shell;
the reusable outer identity is RoadmapProjectCard, not PrimeVue Card. Status Tag
and OpenProject Button remain native PrimeVue copies. Both complete trees must
be assembled before registration, then combined using the documented native
`combineAsVariants` operation. No shared library main changes are authorized.

Inputs are required `title` and optional `languagesText` (full displayed text).
Submitted shows the success status and language text; notSubmitted has a secondary
status and no language node. Empty optional language text is hidden, never populated
from preview data. All project types remain actionable; reviews do not gate status.
Requirement source: sibling `meta/business-analytics/functionality/student-roadmap-completion.md`.

The nested Button uses `action: {"type": "owner-action"}`. This sentinel is allowed
only on Buttons inside custom compositions, has no other fields, and delegates
to the owning custom instance's required concrete action. The manifest forwards
that exact action; display labels and previewProps never select commands or route
identity. Standalone custom mains retain the sentinel as an unbound event contract,
not a working prototype destination. Runtime event wiring and browser accessibility
are not verified by Penpot. The five My Projects JSON previews now use this
family for all 30 project summaries, retaining each concrete command and its
project-type route mapping. Submitted page instances supply a nonempty complete
distinct-language list; notSubmitted instances omit it. Navigation retains the
explicit Open Project button, not a new whole-card interaction. Page ordering,
track progress, access and submission-choice messaging remain page concerns.
Page Penpot synchronization is pending a complete fresh structural preflight;
JSON migration alone does not mean live page artwork was generated.

### Scoped accessible color treatment

`design.colorTreatment: "accessible-blue"` is optional and allowlisted only
for Button, Tag, and SelectButton. It uses `color.accessiblePrimary` (#2563EB)
without changing the global primary token or shared PrimeVue mains. Active
filled primary controls and selected rating surfaces use this blue with white
labels; text/outlined primary labels and specialization tags use this blue on
their existing pale surfaces. Disabled states retain their existing treatment;
loading controls retain their indicator and disabled distinction. Secondary
severity remains secondary. Plain text uses `style.color` as before.

This approved interval-repetition treatment changes colors only, not native
families, layout, target sizes, actions, or runtime props. Runtime implementation
must map it to scoped theme/CSS values and separately verify accessibility.
Color calculations do not constitute rendered visual or runtime acceptance.

Custom component files use:

```text
design/components/<kebab-name>.component.json
```

Each specification must provide:

- `kind: custom-component`;
- stable PascalCase `name`;
- a non-empty `rationale`;
- explicit props and variants;
- a complete `variants.<state>.composition` tree using registered library
  components, structural nodes, text, or other non-cyclic custom components;
- literal `variants.<state>.previewProps` for every required prop and every
  optional prop bound in that state's composition.

There is no top-level composition, state inheritance, override mechanism, or
implicit state flag. Each state declares its nested control props and design
states directly. Every node has a stable PascalCase name, unique within that
state; reuse the same names across states for equivalent roles. Bindings refer
only to declared custom props with matching types. Preview props are design
examples, not runtime defaults. Page instances select the complete tree using
their existing `variant` and supply their own props.

Card slot children must remain inside their Card container, and structural
rows/columns must remain containers. By explicit approval, custom families listed
in `penpot.json` under `customComponents.structuralCardShells` render their
root PrimeVue Card as a structural Penpot board, not a native Card copy. Their
JSON/runtime semantics remain PrimeVue Card. Preserve named Content and Footer
slot containers, native nested Button/Tag copies, and native custom State
variants. This exception applies only to the root Card of the listed families;
it does not permit detached controls, sibling overlays, or structural substitutes
for other library nodes. Loading Buttons require a visible loading indicator, not opacity
alone. Text-variant Buttons must not use a filled primary surface. Unsupported
native composition must be reported as a blocker, not flattened or detached.

## Page organization

Every page declares feature metadata and lives at exactly one feature level:

```json
{
  "$schema": "../../schemas/page.schema.json",
  "feature": { "key": "home", "label": "Home" },
  "page": "Homepage"
}
```

```text
Local file:          design/pages/<feature.key>/<screen>.page.json
Penpot feature page: featurePagePrefix + feature.label
Penpot page frame:   pageFramePrefix + page
```

Feature directories and filenames use kebab-case. Page, structural-node, and
custom-component names use PascalCase.

## Penpot contract

- Registered PrimeVue templates live on `Library / PrimeVue` and use the
  Penpot-native stable path `Library / PrimeVue/<Name>`.
- Project custom components live on `Components` and use stable names
  `Component/<Name>`.
- Both kinds are native reusable Penpot components.
- Page nodes are native copy instances from the matching family, except PrimeVue
  Cards on pages explicitly listed in `penpot.json.pageStructuralCardShells`.
  These Cards use structural boards with named slot containers; JSON/runtime
  semantics remain PrimeVue Card. The approved Homepage-only exception covers
  its eight Cards, not other controls or pages. All nested Avatar, Tag, Timeline,
  and Button controls remain native copies. Detached controls and sibling
  overlays remain prohibited.
- Custom components use nested library component instances where applicable.
- `penpot.json.pageStructuralShells` records explicit page/library/component
  exceptions for slot-bearing containers. The approved ReviewSessionSaved
  Message uses a structural success-message board containing SavedMessageContent
  and its native ProgressBar copy. ReviewComplete uses the same scoped approach
  for CompletionMessageContent and its CompletionTitle/CompletionDescription texts.
  JSON/runtime semantics remain PrimeVue Message. Replace only the page-local
  generated Message subtree; do not detach copies or change the shared main.
  This does not authorize other pages, detached child controls, or
  implicit fallback. Existing Card exceptions remain unchanged.
- Library templates must be semantically recognizable and approximately follow
  approved tokens. Pixel-for-pixel PrimeVue reproduction is not required.
- Detached drawings, documentation boards, and manually redrawn substitutes
  for required instances are invalid.
- Generated page artwork stays inside its canonical `Page/<Name>` frame.
- Generated objects are updated by stable name and never duplicated.

## Tokens and requirements

Reference reusable values with dotted paths such as `color.primary` and
`spacing.md`. Add reusable values to `tokens/tokens.json` before using them.

New or materially revised pages record requirement sources and explicitly
approved assumptions. Business-derived design changes require a proposal and
explicit approval before JSON or Penpot writes.

## Validation

Run from the repository root:

```bash
python3 scripts/validate-design.py
```

The validator checks schemas, library allowlists, props, slots, actions,
bindings, custom variants, composition cycles, tokens, page organization,
requirements, and Penpot configuration.