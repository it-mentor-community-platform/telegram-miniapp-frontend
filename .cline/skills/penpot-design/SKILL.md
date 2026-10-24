---
name: penpot-design
description: Synchronize approved library-first JSON specifications to native representative PrimeVue templates, custom components, and page instances in Penpot.
---

# Penpot design synchronization

JSON under `design/` is authoritative. Read `design/README.md`,
`design/penpot.json`, tokens, the PrimeVue registry, requested custom
components, and pages. Run `python3 scripts/validate-design.py` and stop on any
error. Require explicit approval for material changes. Authenticate read-only
and discover live IDs before writes.

## Mandatory structural preflight and postflight

Read `design/CONFORMANCE.md`. The recursive gate is required on every sync;
the legacy count audit, offline tests, visual inspection, and successful write
calls are not substitutes. All commands below run from the repository root;
use absolute paths when invoking tools and a private temporary directory for
artifacts. Never commit snapshots or credentials.

1. Validate source, build the recursive manifest, and identify the approved
   page/custom scopes and any library/custom template families to change.
   Generate the collector with:
   `python3 scripts/audit-penpot-drift.py --recursive --emit-transfer-js /tmp/penpot-collect-transfer.js`.
   Read and execute the exact emitted function body through the Penpot tool.
   This captures a full snapshot in plugin-local `storage.conformanceSnapshot`
   and prepares `storage.conformanceTransfer`, without changing artwork.
2. Transfer all chunks through bounded tool results. Read the returned header,
   then retrieve chunks by index, at most two per call:
   `return {start: 0, chunks: storage.conformanceTransfer.chunks.slice(0, 2)};`.
   Assemble the exact header fields (`format`, `byteLength`, `checksum`,
   `chunkCount`) and ordered `chunks` into a local JSON envelope. Do not
   summarize/retype artwork, truncate chunks, use localhost networking, or
   recollect between chunks. Decode with
   `python3 scripts/audit-penpot-drift.py --recursive --decode-transfer /tmp/before-transfer.json --snapshot-output /tmp/before.json`.
   A checksum/size failure is BLOCKED; decoding success is not conformance.
3. Run full recursive preflight against `/tmp/before.json`; retain its complete
   report. Existing FAIL can define a separately approved repair inventory.
   Invalid/incomplete/stale collection, transfer failure, ambiguous target
   identity, or unsupported checks affecting the target stop writes. Unrelated
   known drift must be reported, not silently repaired or exempted. First-time
   generation still requires a complete baseline of the configured file.
4. Before writes, complete the native composition capability gate below and
   `design/CONFORMANCE.md`'s operation checklist. Capture actual
   target/sibling bounds. Stamp each semantic shape with the exact manifest
   `auditKey` and slot children/wrappers with `auditSlot`. Never stamp a claim
   of correctness in place of collecting actual live facts.
5. After synchronization (also after a partially failed write), run a fresh
   collection and transfer to `/tmp/after.json`. Do not reuse the baseline as
   the after snapshot. Do not edit JSON/contracts between the paired snapshots;
   if approved sources change, recapture the baseline before further writes.
6. Compare with `--recursive --snapshot /tmp/after.json --baseline /tmp/before.json`
   and repeated `--scope <name>` for every approved page/custom State scope.
   For explicitly approved template changes, add repeated
   `--allow-family '<canonical family>'` and include **all** dependent page and
   custom State scopes. Family permission is not a bypass: changed mains and
   dependents remain checked. Never broaden scope merely to suppress failures.
   Unsupported template representation/state checks remain BLOCKED.
7. Run the full recursive audit separately to report remaining whole-file
   drift. Only a target PASS plus outside-target preservation permits scoped
   acceptance; it never implies a whole-file PASS. FAIL/BLOCKED postflight
   means not accepted. No automatic repair loop; return concrete diagnostics
   and obtain approval for material follow-up changes.

Report structural status, exact checked scopes/families, snapshot file ID,
freshness/completeness, preservation status, remaining full-file drift, and
visual-review status separately. If tool transport prevents comparison, report
BLOCKED and stop; never downgrade to count-only or agent-only verification.
This skill is an agent workflow, not a hook for arbitrary manual Penpot edits.

## Targets

- PrimeVue templates: configured library page and
  `libraryComponents.componentPrefix + component`.
- Custom components: configured custom page and
  `customComponents.componentPrefix + name`.
- Feature pages: `featurePagePrefix + feature.label`.
- Page frames: `pageFramePrefix + page`.

## Synchronization order

1. Discover the configured file/pages read-only. Missing pages require explicit
   creation permission supported by preservation tooling; never create a page
   before the baseline to evade preservation.
2. Resolve tokens to concrete values; write shared assets only when explicitly
   approved. Reuse existing library/custom mains unchanged in page-only scope.
3. For approved template changes only, synchronize native PrimeVue mains, then
   custom mains/`State` variant sets. Include all affected dependent scopes.
4. For a new main, assemble its complete supported composition before registering
   it as a native component, then create variants/copies. A nested library copy
   remains structurally immutable even inside an unregistered outer board.
5. Synchronize page frames. Render every `library-component` and
   `custom-component` as a native copy instance from the correct family.
6. Re-read and verify names, variants, source families, nested instances,
   containment, and duplicates.

## Native composition capability gate (before any artwork writes)

- Compare the required JSON/manifest tree with each live source main's actual
  descendants. Record source main/record IDs, nested copy ancestry, required
  existing roles, planned operations and destinations, supporting API evidence,
  and authorized scopes. Method existence is not permission to use it on a copy.
- Never call `appendChild` or `insertChild` on a component copy or an inherited
  container inside one. Never reparent inherited descendants out of their copy.
  Treat other structural mutations (removal, reordering, grouping, swapping)
  as unsupported unless their exact context is documented and verified; do not
  probe them by trial writes on generated artwork. Inspect copy ancestry, not
  just `isComponentHead()` on the immediate destination.
- Existing copies may override existing text, visibility and supported visual
  properties; a missing semantic child cannot be supplied by a label override.
  Approve compatible mains before creating copies. If the tree is incompatible,
  stop before writes and request an approved template change, justified domain
  component or explicit structural-shell exception. Do not detach, redraw, or
  use sibling overlays as an implicit fallback.
- Validate the destination before creating an instance, not after `instance()`:
  a failed insertion can leave an orphan at the page root. If required native
  operations or their verification are unavailable, report BLOCKED.
- Use small dependency-ordered write batches, record new IDs immediately, and
  re-read native links/parentage after each batch. Re-read geometry after layout
  settles; requested coordinates are not observed bounds.
- On a partial failure, stop writes and capture a fresh complete snapshot before
  further decisions. Inventory partial objects by ID. Do not automatically
  delete or roll back without an authorized, supported cleanup plan; cleanup
  writes also require fresh post-write evidence and preservation comparison.

These are mandatory agent instructions, not an API interceptor. Documentation
regression tests do not prove live capability or prevent arbitrary/manual edits.

Penpot output is a reference-quality layout and implementation guide, not a
pixel-perfect browser specification. Preserve hierarchy, readable content,
sensible proportions, approximate token alignment, and recognizable controls.
Exact CSS metrics and minor cosmetic differences are not acceptance criteria.

## Write and visual-sanity checks

Before a write, capture the target page/frame IDs, bounds, component roots, and
the same summary for nearby generated sibling frames. Inspect the current
bounds of objects that will be changed instead of guessing from JSON alone.

After a write, re-read the changed scope and check for material defects:

- clipped, empty, overlapping, or implausibly narrow text;
- labels outside controls or obviously misaligned within them;
- controls with disproportionate dimensions or excessive unexplained space;
- obviously unusable mobile targets;
- descendants outside their component root or page frame;
- detached library/custom instances, duplicate generated roots, or changed
  sibling frame IDs, bounds, and component roots.

Use broad visual judgment rather than pixel-level tolerances. A tiny alignment
difference is acceptable; unreadable labels, broken hierarchy, clipping, and
grossly oversized controls are not.

When a visual reference is provided, inspect it before writing, identify the
important hierarchy and proportions, and use it as guidance rather than a
pixel-perfect target.

For visual verification, try one full-frame PNG export. If it fails, try one
smaller export of the changed section or control. Do not repeat failed exports
or run them concurrently with other Penpot operations. If both attempts fail,
complete structural and bounds inspection, report that visual export was
unavailable, and require manual visual review; do not claim visual verification.

Do not create documentation boards or detached substitutes. Library main
instances belong on the library page; custom main instances/variant containers
belong on the custom page; generated screen artwork belongs inside canonical
page frames. Update by exact stable name and never delete ambiguous/manual
content.

If native components, variants, nested instances, hierarchy, or verification
are unsupported, stop and report the precise block. A successful write call
alone does not prove visual correctness.

Report validated inputs, targets, objects changed, library/custom instance
verification, unsupported properties, visual-review availability, and manual
follow-up.