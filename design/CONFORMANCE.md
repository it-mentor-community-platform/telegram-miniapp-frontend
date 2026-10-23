# Recursive live structural conformance

## Known legacy Penpot records

The deletion-only cleanup removed the unused PrimeVue Select record and its
three-shape main subtree. The user could not delete the following orphan assets
through Penpot's UI and moved them to `Component / legacy`:

- `06e51fcf-8bc1-4f3a-9468-797e3619435c`: `Component/legacy/Input`.
- `045701d0-f4a3-4853-aded-d2b01af1e1f4`: `Component/legacy/Button`.

Both records have no main and no live shape dependencies. The documented plugin
API available during cleanup exposed no component-record deletion operation.
The user explicitly approved allowlisting these two undeletable orphans. Leave
them untouched; do not recreate mains or register their families. The comparator
accepts only these exact ID/family pairs in file
`6123a605-f677-80e2-8007-66eb7a88b390`, with a null main, empty variants and no
live shape dependencies (by component ID, reference ID or family). It reports
them separately under `acceptedOrphans`, rather than as errors. A changed
allowlisted record produces `LEGACY_ORPHAN_CHANGED`; other unknown/orphan
records remain errors. Missing records need no exception. This permission does
not exempt records from scoped outside-target preservation checks or permit
legacy artwork, instances, new records, or blanket family exclusions.

A fresh complete recursive capture after the manual cleanup checked all eight
page scopes and seven custom State scopes. Before this explicit approval, four
legacy diagnostics were the only findings. Comparison against the historical accepted Homepage snapshot
found only the three Select shapes removed, no added or changed remaining
shapes, unchanged pages, and unchanged non-target records. This historical
comparison is not a fresh pre-deletion preservation gate. No visual exports
were retried, and runtime accessibility remains unverified.

## Homepage representative evidence

Locked achievement Avatars retain their native copy and visible label, with root
opacity greater than zero and at most 0.6. A state stamp alone is insufficient.
Timeline values require ordered direct `TimelineItemN` boards, each with one
`Content` board containing exact `Title` (icon plus title) and `Time`
(description plus time, separated by a newline) texts, and one visible ellipse
`Marker`. Rows must follow value order without overlap. Unaccounted artwork and
native-reference checks remain unchanged. This verifies representative content,
not runtime accessibility. Homepage uses the existing scoped accessible-blue
treatment for its role Tag and four link Buttons, plus the accessible token for
profile initials and the achievements continuation text; shared mains are unchanged.

The strict gate is `scripts/audit-penpot-drift.py --recursive`. Original
count-based mode remains for legacy diagnosis only, not structural acceptance.
The new mode performs no live mutations and never repairs drift.

## Runbook

From the repository root:

```sh
python3 scripts/validate-design.py
python3 -B -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/audit-penpot-drift.py --recursive --manifest
python3 scripts/audit-penpot-drift.py --recursive --emit-penpot-js /tmp/penpot-collect.js
```

Authenticate read-only, confirm the configured generated file, and execute the
emitted function body in the Penpot plugin context. Save its returned JSON to
an untracked temporary file. Never commit private snapshots or credentials.

For the skill's network-free handoff, emit `--emit-transfer-js` instead of
`--emit-penpot-js`. Execute the exact emitted body once. It stores the immutable
captured facts in plugin-local storage and returns a small transfer header.
Fetch `storage.conformanceTransfer.chunks.slice(start, start + 2)` in ordered,
bounded tool calls; assemble a JSON envelope with `format`, `byteLength`,
`checksum`, `chunkCount`, and the complete ordered `chunks` array. The format
uses UTF-8, bounded 16-bit LZW, base64, and Adler-32 corruption detection. It
does not authenticate evidence. No browser compression API, local HTTP server,
network access, credentials, or artwork mutations are needed.

```sh
python3 scripts/audit-penpot-drift.py --recursive \
  --emit-transfer-js /tmp/penpot-collect-transfer.js
python3 scripts/audit-penpot-drift.py --recursive \
  --decode-transfer /tmp/before-transfer.json --snapshot-output /tmp/before.json
```

Missing, reordered, truncated or corrupted chunks fail decoding. Decoding is
only transport validation: run the comparator separately. Never recollect
mid-transfer or use a reconstructed summary instead of exact snapshot facts.

```sh
python3 scripts/audit-penpot-drift.py --recursive --snapshot /tmp/after.json
python3 scripts/audit-penpot-drift.py --recursive --snapshot /tmp/after.json \
  --scope ReviewSessionSaved --baseline /tmp/before.json
```

Exit codes: **0 PASS**, **1 FAIL** (observed nonconformance), **2 BLOCKED**
(insufficient/unsupported evidence). BLOCKED takes precedence over FAIL;
all diagnostics remain available. Generating a collector/manifest is not a
passing gate. Snapshot version 2, exact source fingerprint, configured file
name plus live ID, complete traversal, and capture age at most one hour are
mandatory. Target before/after snapshots must share file ID and fingerprint.

Require preflight before synchronization and postflight before acceptance.
Existing failures are a repair inventory, not permission to weaken contracts.
A target PASS is not whole-file conformance. CI runs offline tests; fresh live
evidence must be obtained separately.

## Read-only design review

### Explicit empty-text visibility

Text nodes may opt in to `hideWhenEmpty: true`. After binding, an exactly empty
string requires effective hidden visibility (`EMPTY_TEXT_VISIBLE` otherwise).
Nonempty strings, including whitespace-only strings, still require visibility;
unflagged empty strings receive no exemption. The node remains mandatory and
retains identity, representation, parent, slot, exact text, and positive-bounds
checks. This does not omit optional nodes or allow arbitrary hidden content.
By explicit approval, text specifications may declare
`penpotEmptyPlaceholder: " "` together with `hideWhenEmpty: true`. Only when
the resolved semantic value is exactly empty may a native copy retain exactly
one ASCII space. It must be explicitly hidden (not just hidden by an ancestor),
retain its verified native source text within its component main, and belong to
the corresponding native owner copy with matching family, record and State.
The snapshot records the actual space; the manifest/runtime value remains empty.
Missing opt-in, detached text, wrong sources, tabs, NBSP and multiple spaces are
not exempted. Nonempty semantic values keep ordinary exact-text/visibility checks.
CategorySelectionRow ProgressText opts in for all four existing States, retaining
the native State records and existing text-node structure. No runtime prop or
generic-control wrapper is introduced.

`design-review` requires fresh collection and recursive comparison for any
live structural verification claim. It never repairs or stamps live artwork.
Whole-file review uses `--recursive --snapshot` as above. Scoped review uses:

```sh
python3 scripts/audit-penpot-drift.py --recursive --snapshot /tmp/review.json \
  --inspect --scope ReviewSessionSaved
```

Repeat `--scope` for additional exact manifest scope names. `--inspect` requires
explicit scopes and a snapshot, forbids `--baseline` and `--allow-family`, and
does **not** establish outside-scope preservation or synchronization acceptance.
Do not fake a baseline or compare a snapshot with itself for review. The same
freshness, fingerprint, full-file evidence, ambiguity, recursive content, native
source-linkage, and fail-closed checks apply. Global evidence validity and
identity ambiguity can block/fail even a scoped inspection. Unselected scope
content, whole-file stray/orphan inventory, and full template inventory are not
certified by scoped inspection; selected native source linkage is still checked.
Reports expose `mode`, `requestedScopes`, and `preservationChecked` (false for
inspection; true only when a valid synchronization baseline was compared).
Existing `--scope` without `--inspect` still requires a preservation baseline.

Report exact coverage and PASS/FAIL/BLOCKED. Observed errors become findings;
BLOCKED indicates incomplete verification, not a proven artwork defect. Keep
independent observed errors when BLOCKED takes precedence. Other review work
may continue, but no unqualified all-clear is allowed. Requirements,
accessibility, and visual checks remain separate from structural conformance.
JSON-only review is supported: report live structural/visual verification as
not performed, rather than claiming PASS. The skill is instruction-based,
not an automatic interception of manual edits. Full live snapshot transfer and
comparison remain unverified as recorded above; offline tests are not live proof.

## Identity and representations

The manifest exposes each expected `key`, `source`, `parent`, and `slot`.
Generation must stamp the exact key with `shape.setPluginData('auditKey', key)`.
Keys include repository-relative JSON Pointers; custom composition locators are
namespaced by the owning instance to disambiguate repeated families. Stamp slot
children or intermediary slot boards with `setPluginData('auditSlot', slot)`.
These stamps locate artwork, not assert correctness.

The native custom head represents its composition root: do not add a second
detached Card beneath it. Nested library controls remain native copy heads.
Explicit page/custom Card exceptions and exact configured Message exceptions
remain structural boards. Other library heads require native copy linkage to
the registered family and a reference in its observed main subtree. Each custom
State is expanded with page props, or preview props for template expectations.
Omitted optional string bindings represent empty text; missing required bindings
block resolution. Prose page `states` do not create additional screens.

Legacy matching requires unique semantic names/families. Ambiguity fails.
Unnamed structural shells need identity stamps. Legacy artwork can therefore
fail until regenerated by a separately approved synchronization.

## Contracts and limitations

Approved Toolbar `inactiveNativeBranches` describes only the BackButton/start
and EndButton/end template branches, each a Button with exactly Label and
TrailingIcon text leaves. An omitted slot may retain its explicitly hidden
native subtree because native removal hides copy descendants. Acceptance
requires a verified Toolbar copy/main pair, exactly one corresponding source
branch and copy by native reference, verified Button record/main, matching
family/State, and a bijection of the two leaf source references. Source and copy
branch roots must both be explicitly hidden. No semantic stamps or slot claims
may be placed on inactive remnants. Duplicates, extra depth, detached copies,
unrelated references and present/required slots receive no exemption. This is
not a hidden-node exemption or an addition to the generic internal-name list.

Registry `penpotAudit` metadata declares an adapter, explicit internal names,
prop-to-text roles and supported observable states. It is not runtime props or
product behavior. Unexplained visible template text fails even if its shape name
is allowlisted. Semantic slot content is recursively required; unexplained
shapes/component heads fail.

Adapters check text props; Button icons/loading; ProgressBar indicator, value,
indeterminate segment and hidden percentage; and every SelectButton option.
Stable roles include `Label`, `Value`, `Indicator`, and `Option0`.
Determinate progress allows 3px representative variance with 4px track insets;
containment allows 2px variance. Unknown icons/states block. Empty
`observableStates` intentionally blocks until its adapter is implemented.

The initial contracts do not prove full appearance parity, disabled interaction,
focus, runtime accessibility, browser behavior or subjective visual quality.
Several specialized states remain unsupported. Library mains are checked for
native identity/linkage, not every representative visual appearance/state.
No automatic repairs are included.

Implementation verification on October 23, 2026: read-only collection from the
configured generated file completed with 611 shapes and 23 component records.
The plugin could not transfer that snapshot to the local Python comparator, so
no end-to-end live PASS/FAIL is claimed. A fresh exported snapshot is still
required for acceptance. Read-only sampling confirmed native main heads have
null copy references (valid for mains), and the previously recorded Select and
orphan Input/Button records remain present. No artwork was modified.

Skill integration verification later on October 23, 2026: the network-free
encoder ran in the real plugin sandbox over all 611 shapes; its tabular payload
was 181,040 UTF-8 bytes, encoded into eight chunks. An intentionally incomplete
live sample was transferred through tool output and successfully decoded by the
local CLI with size/checksum verification. The comparator rejected the sample
as BLOCKED (stale source fingerprint); it was never used as acceptance evidence.
Full-file chunk assembly and fresh full live comparison remain unverified.
Offline tests cover complete Unicode roundtrips, malformed/truncated/corrupted
transfers, emitted JavaScript syntax, CLI decoding, and preservation permissions.

`penpot-design` now explicitly requires these steps, not just a documentation
reference. It remains an instruction-based agent workflow: it cannot intercept
manual Penpot edits or guarantee an agent invokes tools correctly. A transfer
or verification failure must stop acceptance and be reported as BLOCKED.

## Evidence and scope

### Explicit unset-opacity adapter

The plugin's `ShapeBase.opacity` getter returns stored `:opacity` directly;
unset values are returned as JavaScript `null`. Penpot's WASM renderer
`set-shape-opacity` uses `(or opacity 1)`. Primary-source implementation checked
on October 23, 2026 at Penpot commit
`74add0522668dffe9bb35cd18bc8a0e812372b5e`:
`frontend/src/app/plugins/shape.cljs` and
`frontend/src/app/render_wasm/api.cljs`. The connected deployment's exact build
was not identified; this adapter is based on these source semantics and the
observed live null values, not on an API type declaration promising a number.

The collector retains `rawOpacity` and emits `opacitySource` as `explicit` or
`penpot-null-default-v1`; only explicit null receives effective opacity 1.
Undefined/getter exceptions are not defaulted. Python rejects inconsistent or
partial provenance, null effective values, non-finite values, booleans, and
values outside [0, 1]. Explicit zero and hidden/transparent ancestors still
fail visibility. Legacy finite numeric evidence remains accepted.

Fresh read-only end-to-end verification on October 23, 2026 captured file
`6123a605-f677-80e2-8007-66eb7a88b390` at `2026-10-23T18:02:44.943Z`:
611 shapes, 23 records, full-file coverage, complete, no collection errors;
571 raw null opacities were explicitly adapted. All eight ordered transfer
chunks were retrieved from the same capture through tool output, and decoded
locally with size/checksum verification (187,284 bytes, Adler-32 `1b618d08`).
The recursive Python comparator ran successfully; the evidence/transport block
is resolved, but conformance is **BLOCKED**, not PASS. Whole-file comparison
produced 626 diagnostics (168 blocked, 458 errors). Inspection of
`CategorySetup`, `CategoryDetails`, `RepetitionDashboard`, and `ReviewSession`
produced 274 diagnostics (78 blocked, 196 errors), including ambiguous legacy
identity, missing slot evidence, and an unsupported expanded Panel state.
These diagnostics can cascade from ambiguous matching; they are not a count
of independent proven artwork defects. Scoped inspection did not check
outside-scope preservation or certify the whole-file inventory. The full run
also reported the unapproved Select/Input/Button families and orphan records.
No artwork, plugin identity metadata, or UI specification was modified.
Temporary snapshots/reports remain untracked under `/tmp/review*`.

The read-only collector captures flat facts for all pages, shapes and native
records: parentage, source references, variants, bounds, text and visibility.
The local component catalogue exposes a representative of each native variant
family rather than all of its State records. For variant representatives the
collector enumerates `variants.variantComponents()` and deduplicates records
by ID. Missing/incomplete variant sets, API errors, and conflicting records
make collection incomplete; they are not silently treated as absent artwork.
The October 23 capture described above used the older catalogue-only collector:
its 23 records omitted five existing custom State records. Consequently its
missing-source and template-State diagnostics require fresh comparison, not
artwork recreation. A later read-only capture at `2026-10-23T18:32:54.856Z`
using variant enumeration observed all seven custom State records (28 total
records, 611 shapes, complete/full-file, no collection errors). That capture's
header or agent inspection alone is not a recursive comparator result and does
not establish conformance or a verified preservation baseline.
Approved interval-repetition state adapters additionally check:
- Accordion selected values must agree with panel expanded/collapsed metadata.
  AccordionPanel's registered Secondary text internal is interpreted as a state
  indicator: exactly one direct, visible, positive-size, contained non-head text
  child must show `⌄` when collapsed and `⌃` when expanded. Only a validated
  indicator is consumed; arbitrary visible internal text remains an error.
  Collapsed panel content must exist with correct identity, text, parent and
  slot evidence but be effectively hidden. Hidden content is not required to
  fit within the collapsed panel's visible bounds; visible content still is.
  Expanded content and all headers remain subject to normal visibility checks.
- Disabled Buttons must have `disabled=true` and a visible muted head with
  opacity at most 0.6, based on the observed 0.5 representative controls. This
  establishes static appearance only, not keyboard or runtime disabled behavior.
  Loading metadata must agree with `loading=true` and a visible loader is still
  required independently of opacity. The play icon maps to the observed `▶`.
Limits are 20,000 shapes and 15 seconds. API exceptions, cycles, duplicate IDs
or time limits yield incomplete evidence and BLOCKED. An external timeout
without a snapshot cannot pass. Python owns comparison, not emitted JavaScript.

### Native references inside custom mains

Penpot's `ShapeBase.componentRefShape()` documents a null result for shapes
inside a main instance. Preserve that null in collection. A nested library
copy may use native component-record/main evidence only inside the actual
ancestry of the selected, verified custom State main: the custom root must be
a registered native main, its record must point back to it, and family/State
must agree. The nested control still requires native copy/head flags, correct
family/record, and an existing matching native source main. This is not an
exception for detached artwork, page copies, or custom copies. Non-null wrong
references remain errors even inside custom mains. Ordinary page copies retain
the reference-shape membership requirement. Plugin identities never substitute
for native source evidence.

A non-null reference on a nested page copy can instead identify the matching
nested copy in its enclosing native main. The comparator supports only the
verified direct-parent topology: the page parent must be a native copy/head
whose reference is exactly its valid registered native main; the referenced
child must be a direct native copy/head child of that main with the same
family, component record and variant as the page child. Parent record, family
and variants must agree with its main. The nested source's null reference is
retained as documented main-instance evidence. The child's standalone native
main is still independently validated. Missing references, unrelated enclosing
mains, detached shapes, mismatched records and arbitrary ancestry are not
accepted.

One intervening structural board is also supported when both sides are paired
by native source evidence. The page board must be a non-head native copy,
directly under the verified enclosing copy/head, and reference a plain non-head
structural board directly inside that enclosing record's main. The page board
must retain the enclosing component record, family and State. The source board
is not a native copy and has null family, component and reference fields and an
empty variant map. The nested control must reference a direct child of
that exact source board, with the same copy/head, family, record, variant and
null-reference checks as the direct case. Names and audit stamps do not prove
pairing. Sibling boards, other States, detached boards, missing source links,
extra wrapper depth and arbitrary ancestry remain rejected. The nested control's
standalone native main is still independently validated. No artwork flattening,
source-reference rewriting or State-record recreation is required.

The full gate checks all specified page frames/custom State mains, unapproved
or orphan records, and stray feature-page artwork. The target gate requires a
full before snapshot and compares all outside-target shape facts, page IDs and
component records. This rejects template edits in a page-only sync by default.
Explicit `--allow-family 'Library/PrimeVue/ProgressBar'` (repeatable) permits
only registered template families, requires a baseline and explicit scopes,
and requires every affected page/custom State scope to be selected. It allows
that family's main subtrees/records to change, not unrelated template artwork
or arbitrary dependency exemptions. Native mains and their dependents remain
checked; generic library appearance/state coverage remains limited as above.
Target scope may remove existing target children, but cannot absorb protected
objects by moving them into the target. Object/record ordering is irrelevant.
No page creation/renaming permission is implied; that requires a separate scope
extension rather than silently relaxing preservation. Neither checks arbitrary
manual artwork for product correctness. Both
require effective ancestor visibility and containment. Continue the existing
bounded PNG/manual visual-review workflow separately.