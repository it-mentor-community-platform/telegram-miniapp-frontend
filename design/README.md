# UI design source

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

Custom component files use:

```text
design/components/<kebab-name>.component.json
```

Each specification must provide:

- `kind: custom-component`;
- stable PascalCase `name`;
- a non-empty `rationale`;
- explicit props and variants;
- a `composition` tree using registered library components, structural nodes,
  text, or other non-cyclic custom components.

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
- Page nodes are native copy instances from the matching family.
- Custom components use nested library component instances where applicable.
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