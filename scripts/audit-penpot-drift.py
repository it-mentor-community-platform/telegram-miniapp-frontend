#!/usr/bin/env python3
"""Build and verify a read-only JSON-to-live Penpot drift audit.

The repository JSON is authoritative. This script derives the expected native
component families and page-level representative instances from it. It can
emit a self-contained JavaScript audit for the Penpot plugin context and can
compare a snapshot returned by that audit without requiring Penpot credentials.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import penpot_conformance as conformance
from penpot_snapshot import decode_transfer

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
PENPOT = DESIGN / "penpot.json"
LIBRARIES = DESIGN / "libraries"
COMPONENTS = DESIGN / "components"
PAGES = DESIGN / "pages"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_snapshot(path: Path) -> dict[str, Any]:
    """Load either a raw snapshot or a complete Penpot audit result."""

    try:
        value = load(path)
    except FileNotFoundError as error:
        raise ValueError(f"snapshot file not found: {path}") from error
    except OSError as error:
        raise ValueError(f"could not read snapshot file {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"snapshot file {path} is not valid JSON: line {error.lineno}, column {error.colno}"
        ) from error

    if not isinstance(value, dict):
        raise ValueError("snapshot input must be a JSON object")
    if "snapshot" in value:
        value = value["snapshot"]
        if not isinstance(value, dict):
            raise ValueError("plugin result snapshot must be a JSON object")
    return value


def stable_family(prefix: str, name: str) -> str:
    return f"{prefix}{name}"


def representative_instances(nodes: list[dict[str, Any]]) -> Counter[str]:
    """Count page roots represented by native component instances.

    A library/custom node is one native page instance. Its slots are content of
    the representative template and are intentionally not counted as separate
    page roots. Structural nodes continue traversal through ``children``.
    """

    result: Counter[str] = Counter()

    def visit(node: dict[str, Any]) -> None:
        node_type = node.get("type")
        if node_type == "library-component":
            result[f"library:{node['library']}:{node['component']}"] += 1
            return
        if node_type == "custom-component":
            result[f"custom:{node['component']}"] += 1
            return
        for child in node.get("children", []):
            visit(child)

    for node in nodes:
        visit(node)
    return result


def build_manifest() -> dict[str, Any]:
    config = load(PENPOT)
    library_prefix = config["libraryComponents"]["componentPrefix"]
    custom_prefix = config["customComponents"]["componentPrefix"]

    library_names: dict[str, set[str]] = {}
    for path in sorted(LIBRARIES.glob("*.library.json")):
        value = load(path)
        library_names[value["library"]] = set(value["components"])

    custom_names = sorted(load(path)["name"] for path in COMPONENTS.glob("*.component.json"))
    frames: dict[str, dict[str, Any]] = {}
    custom_totals: Counter[str] = Counter()
    json_representative_instances = 0

    for path in sorted(PAGES.rglob("*.page.json")):
        value = load(path)
        page_name = f"{config['featurePagePrefix']}{value['feature']['label']}"
        frame_name = f"{config['pageFramePrefix']}{value['page']}"
        raw_counts = representative_instances(value.get("children", []))
        families: Counter[str] = Counter()
        for key, count in raw_counts.items():
            kind, owner, *rest = key.split(":")
            if kind == "library":
                component = rest[0]
                if owner not in library_names or component not in library_names[owner]:
                    raise ValueError(f"Unknown library family in {path.relative_to(ROOT)}: {owner}/{component}")
                family = stable_family(library_prefix, component)
            else:
                component = owner
                if component not in custom_names:
                    raise ValueError(f"Unknown custom family in {path.relative_to(ROOT)}: {component}")
                family = stable_family(custom_prefix, component)
            families[family] += count
        custom_families = Counter(
            {family: count for family, count in families.items() if family.startswith(custom_prefix)}
        )
        custom_totals.update(custom_families)
        json_representative_instances += sum(families.values())
        key = f"{page_name}\n{frame_name}"
        frames[key] = {
            "page": page_name,
            "frame": frame_name,
            "customFamilies": dict(sorted(custom_families.items())),
        }

    custom_families = [stable_family(custom_prefix, name) for name in custom_names]
    return {
        "version": 1,
        "generatedFileName": config["generatedFileName"],
        "libraryPage": config["libraryComponents"]["pageName"],
        "customPage": config["customComponents"]["pageName"],
        "libraryPrefix": library_prefix,
        "customPrefix": custom_prefix,
        "libraryFamilies": sorted(
            stable_family(library_prefix, name)
            for names in library_names.values()
            for name in names
        ),
        "customFamilies": custom_families,
        "frames": frames,
        "customTotals": dict(sorted(custom_totals.items())),
        "jsonRepresentativeInstances": json_representative_instances,
    }


def emit_penpot_javascript(manifest: dict[str, Any]) -> str:
    expected = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    return f"""// Generated by scripts/audit-penpot-drift.py; read-only.
const expected = {expected};

function flatten(shape, output = []) {{
  output.push(shape);
  if ("children" in shape) for (const child of shape.children) flatten(child, output);
  return output;
}}

function familyName(component) {{
  if (!component) return null;
  if (component.name.includes("/")) return component.name;
  return component.path ? `${{component.path}}/${{component.name}}` : component.name;
}}

function countFamilies(frame) {{
  const counts = {{}};
  for (const shape of flatten(frame)) {{
    if (!shape.isComponentRoot?.()) continue;
    const family = familyName(shape.component?.());
    if (family) counts[family] = (counts[family] || 0) + 1;
  }}
  return Object.fromEntries(Object.entries(counts).sort(([a], [b]) => a.localeCompare(b)));
}}

function compareCounts(scope, wanted, actual, errors) {{
  const names = new Set([...Object.keys(wanted), ...Object.keys(actual)]);
  for (const name of [...names].sort()) {{
    const expectedCount = wanted[name] || 0;
    const actualCount = actual[name] || 0;
    if (expectedCount !== actualCount) errors.push(`${{scope}}: ${{name}} expected ${{expectedCount}}, found ${{actualCount}}`);
  }}
}}

const errors = [];
const warnings = [];
const frameSnapshots = {{}};
const allPageInstances = [];
const allowedFamilies = new Set([...expected.libraryFamilies, ...expected.customFamilies]);

for (const item of Object.values(expected.frames)) {{
  const pages = penpot.currentFile.pages.filter(page => page.name === item.page);
  if (pages.length !== 1) {{
    errors.push(`page ${{item.page}} expected once, found ${{pages.length}}`);
    continue;
  }}
  const legacyFrame = item.frame.replace("Page/", "Page / ");
  const frames = flatten(pages[0].root).filter(shape => shape.name === item.frame || shape.name === legacyFrame);
  if (frames.length !== 1) {{
    errors.push(`${{item.page}} / ${{item.frame}} (or legacy ${{legacyFrame}}) expected once, found ${{frames.length}}`);
    continue;
  }}
  if (frames[0].name === legacyFrame) warnings.push(`${{item.page}}: legacy frame name ${{legacyFrame}} could not be normalized through the plugin API`);
  const families = countFamilies(frames[0]);
  const key = `${{item.page}}\n${{item.frame}}`;
  frameSnapshots[key] = {{page: item.page, frame: item.frame, families, total: Object.values(families).reduce((a, b) => a + b, 0)}};
  const customFamilies = Object.fromEntries(Object.entries(families).filter(([family]) => family.startsWith(expected.customPrefix)));
  compareCounts(`${{item.page}} / ${{item.frame}} custom instances`, item.customFamilies, customFamilies, errors);
  for (const family of Object.keys(families)) if (!allowedFamilies.has(family)) errors.push(`unapproved page component family: ${{family}}`);
  for (const [family, count] of Object.entries(families)) for (let i = 0; i < count; i++) allPageInstances.push(family);
}}

const totals = allPageInstances.reduce((result, family) => {{
  result[family] = (result[family] || 0) + 1;
  return result;
}}, {{}});
const customTotals = Object.fromEntries(Object.entries(totals).filter(([family]) => family.startsWith(expected.customPrefix)));
compareCounts("all generated page frames custom instances", expected.customTotals, customTotals, errors);

const records = penpot.library.local.components.map(component => ({{
  id: component.id,
  family: familyName(component),
  hasMain: !!component.mainInstance?.(),
}})).sort((a, b) => a.family.localeCompare(b.family));

for (const family of expected.customFamilies) {{
  const matching = records.filter(record => record.family === family && record.hasMain);
  if (matching.length !== 1) errors.push(`custom family ${{family}} expected one main, found ${{matching.length}}`);
}}
for (const record of records) {{
  if (record.family.startsWith(expected.customPrefix) && !expected.customFamilies.includes(record.family)) {{
    if (record.hasMain) errors.push(`unapproved custom family has a main: ${{record.family}}`);
    else warnings.push(`orphan component record has no main or page references: ${{record.family}} (${{record.id}})`);
  }}
}}

const customPages = penpot.currentFile.pages.filter(page => page.name === expected.customPage);
if (customPages.length !== 1) errors.push(`custom component page ${{expected.customPage}} expected once, found ${{customPages.length}}`);
else {{
  const visibleCustomRoots = flatten(customPages[0].root)
    .filter(shape => shape.isComponentRoot?.())
    .map(shape => familyName(shape.component?.()))
    .filter(family => family?.startsWith(expected.customPrefix));
  for (const family of visibleCustomRoots) if (!expected.customFamilies.includes(family)) errors.push(`${{expected.customPage}}: unapproved custom family root ${{family}}`);
  for (const family of expected.customFamilies) {{
    const count = visibleCustomRoots.filter(value => value === family).length;
    if (count < 1) errors.push(`${{expected.customPage}}: ${{family}} has no visible native root`);
  }}
}}

const snapshot = {{version: 1, frames: frameSnapshots, totals: Object.fromEntries(Object.entries(totals).sort(([a], [b]) => a.localeCompare(b))), records}};
return {{
  ok: errors.length === 0,
  errors,
  warnings,
  snapshot,
  snapshotJson: JSON.stringify(snapshot),
}};
"""


def compare_snapshot(manifest: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if snapshot.get("version") != 1:
        errors.append(f"snapshot version must be 1, found {snapshot.get('version')!r}")

    actual_frames = snapshot.get("frames")
    if not isinstance(actual_frames, dict):
        return errors + ["snapshot.frames must be an object"]

    actual_totals_value = snapshot.get("totals")
    if not isinstance(actual_totals_value, dict):
        return errors + ["snapshot.totals must be an object"]

    records = snapshot.get("records")
    if not isinstance(records, list):
        return errors + ["snapshot.records must be an array"]

    expected_frames = manifest["frames"]
    for key in sorted(set(expected_frames) | set(actual_frames)):
        if key not in expected_frames:
            errors.append(f"unexpected generated frame: {key.replace(chr(10), ' / ')}")
            continue
        if key not in actual_frames:
            errors.append(f"missing generated frame: {key.replace(chr(10), ' / ')}")
            continue
        actual_frame = actual_frames[key]
        if not isinstance(actual_frame, dict):
            errors.append(f"{key.replace(chr(10), ' / ')}: frame snapshot must be an object")
            continue
        actual_families = actual_frame.get("families", {})
        if not isinstance(actual_families, dict):
            errors.append(f"{key.replace(chr(10), ' / ')}: families must be an object")
            continue
        unknown = sorted(set(actual_families) - set(manifest["libraryFamilies"]) - set(manifest["customFamilies"]))
        for family in unknown:
            errors.append(f"{key.replace(chr(10), ' / ')}: unapproved page component family {family}")
        wanted = expected_frames[key]["customFamilies"]
        actual = {
            family: count
            for family, count in actual_families.items()
            if family.startswith(manifest["customPrefix"])
        }
        for family in sorted(set(wanted) | set(actual)):
            if wanted.get(family, 0) != actual.get(family, 0):
                errors.append(
                    f"{key.replace(chr(10), ' / ')}: {family} expected {wanted.get(family, 0)}, "
                    f"found {actual.get(family, 0)}"
                )

    actual_totals = {
        family: count
        for family, count in actual_totals_value.items()
        if family.startswith(manifest["customPrefix"])
    }
    for family in sorted(set(manifest["customTotals"]) | set(actual_totals)):
        wanted = manifest["customTotals"].get(family, 0)
        actual = actual_totals.get(family, 0)
        if wanted != actual:
            errors.append(f"all generated page frames: {family} expected {wanted}, found {actual}")

    for family in manifest["customFamilies"]:
        mains = sum(
            isinstance(record, dict)
            and record.get("family") == family
            and record.get("hasMain") is True
            for record in records
        )
        if mains != 1:
            errors.append(f"custom family {family} expected one main, found {mains}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", action="store_true", help="print the JSON-derived expected manifest")
    parser.add_argument("--emit-penpot-js", metavar="PATH", help="write a read-only Penpot audit; use - for stdout")
    parser.add_argument("--snapshot", type=Path, help="compare a snapshot returned by the Penpot audit")
    parser.add_argument("--recursive", action="store_true", help="use strict version-2 semantic conformance")
    parser.add_argument("--scope", action="append", help="target scope (repeatable); requires --baseline unless --inspect")
    parser.add_argument("--inspect", action="store_true", help="read-only scoped review; forbids baseline/family permissions; no preservation check")
    parser.add_argument("--baseline", type=Path, help="fresh before snapshot for protected-scope comparison")
    parser.add_argument("--partial-recovery", type=Path, help="explicit approved file/scope/root/node inventory for unregistered baseline recovery")
    parser.add_argument("--emit-transfer-js", type=Path, help="emit collector plus network-free chunk preparation")
    parser.add_argument("--emit-resumable-js", type=Path, help="emit bounded read-only collector; resume via storage.conformanceCollectStep()")
    parser.add_argument("--decode-transfer", type=Path, help="decode a chunk envelope into --snapshot-output")
    parser.add_argument("--snapshot-output", type=Path, help="output path for decoded snapshot")
    parser.add_argument("--allow-family", action="append", help="explicitly permitted template family; requires dependent --scope entries")
    parser.add_argument("--new-library-only", help="add one absent unused library family; requires full baseline and preserves all existing artwork")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.recursive:
        try:
            if args.partial_recovery and (not args.snapshot or not args.baseline or not args.scope or not args.allow_family
                                         or args.inspect or args.new_library_only or args.decode_transfer):
                raise ValueError('--partial-recovery requires snapshot, baseline, scopes and family permission; forbids inspection, new-library-only and decoding')
            if args.new_library_only and (not args.snapshot or not args.baseline or args.scope or args.inspect or args.allow_family or args.decode_transfer):
                raise ValueError("--new-library-only requires --snapshot and --baseline; forbids scopes, inspection, family permissions and decoding")
            if args.inspect and (not args.scope or args.baseline or args.allow_family or not args.snapshot or args.decode_transfer):
                raise ValueError("--inspect requires --scope and --snapshot; forbids --baseline, --allow-family and --decode-transfer")
            if args.decode_transfer:
                if not args.snapshot_output:
                    raise ValueError("--decode-transfer requires --snapshot-output")
                decoded = decode_transfer(json.loads(args.decode_transfer.read_text()))
                args.snapshot_output.write_text(json.dumps(decoded, ensure_ascii=False), encoding="utf-8")
                print(f"Decoded integrity-checked snapshot to {args.snapshot_output}; not a conformance PASS")
                return 0
            expected = conformance.build_manifest()
            if args.manifest:
                print(json.dumps(expected, ensure_ascii=False, indent=2))
            if args.emit_penpot_js:
                javascript = conformance.emit_collector(expected)
                if args.emit_penpot_js == "-": print(javascript)
                else: Path(args.emit_penpot_js).write_text(javascript, encoding="utf-8")
            if args.emit_transfer_js:
                args.emit_transfer_js.write_text(conformance.emit_collector(expected, transfer=True), encoding="utf-8")
            if args.emit_resumable_js:
                args.emit_resumable_js.write_text(conformance.emit_collector(expected, resumable=True), encoding="utf-8")
            if args.snapshot:
                if args.new_library_only:
                    result = conformance.compare_new_library(expected, load_snapshot(args.snapshot),
                                                            load_snapshot(args.baseline), args.new_library_only)
                else:
                    result = conformance.compare(expected, load_snapshot(args.snapshot), args.scope,
                                             load_snapshot(args.baseline) if args.baseline else None,
                                             allow_families=args.allow_family, inspect=args.inspect,
                                             partial_recovery=json.loads(args.partial_recovery.read_text()) if args.partial_recovery else None)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[result["status"]]
            if not args.manifest and not args.emit_penpot_js and not args.emit_transfer_js and not args.emit_resumable_js:
                print("BLOCKED: provide --snapshot; building expectations alone is not conformance")
                return 2
            return 0
        except (ValueError, KeyError, TypeError, OSError) as error:
            print(f"BLOCKED: {error}", file=sys.stderr)
            return 2
    if args.emit_resumable_js or args.partial_recovery or args.new_library_only or args.inspect or args.scope or args.baseline or args.allow_family or args.emit_transfer_js or args.decode_transfer or args.snapshot_output:
        print("structural gate options require --recursive", file=sys.stderr)
        return 2
    manifest = build_manifest()
    performed = False

    if args.manifest:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        performed = True

    if args.emit_penpot_js:
        javascript = emit_penpot_javascript(manifest)
        if args.emit_penpot_js == "-":
            print(javascript, end="")
        else:
            path = Path(args.emit_penpot_js)
            path.write_text(javascript, encoding="utf-8")
            print(f"Wrote read-only Penpot audit to {path}")
        performed = True

    if args.snapshot:
        try:
            snapshot = load_snapshot(args.snapshot)
        except ValueError as error:
            print(f"Penpot drift audit input error: {error}", file=sys.stderr)
            return 2
        errors = compare_snapshot(manifest, snapshot)
        if errors:
            print(f"Penpot drift audit failed with {len(errors)} error(s):")
            for error in errors:
                print(f"- {error}")
            return 1
        print(
            "Penpot drift audit passed: "
            f"{len(manifest['frames'])} frames, {sum(manifest['customTotals'].values())} custom page instances, "
            f"and {len(manifest['customFamilies'])} approved custom families match the JSON source."
        )
        performed = True

    if not performed:
        print(
            f"Expected {len(manifest['frames'])} frames, {sum(manifest['customTotals'].values())} custom page instances, "
            f"and {len(manifest['customFamilies'])} custom families. "
            "Use --emit-penpot-js to generate the live read-only audit."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())