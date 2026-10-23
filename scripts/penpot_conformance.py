"""Strict semantic conformance; stdlib only, no credentials or live writes.

Identity metadata locates artwork. All assertions use collected live facts.
Unknown representations and incomplete evidence are never a successful audit.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

VERSION = 2
ROOT = Path(__file__).resolve().parents[1]

# Explicitly approved, undeletable catalogue artifacts; never reusable families.
LEGACY_ORPHAN_FILE_ID = "6123a605-f677-80e2-8007-66eb7a88b390"
LEGACY_ORPHANS = {
    "06e51fcf-8bc1-4f3a-9468-797e3619435c": "Component/legacy/Input",
    "045701d0-f4a3-4853-aded-d2b01af1e1f4": "Component/legacy/Button",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def normalize_family(value):
    return "/".join(part.strip() for part in value.split("/"))


def bind(value, props):
    if isinstance(value, dict):
        if set(value) == {"bind"}:
            if value["bind"] not in props:
                raise ValueError(f"unresolved binding {value['bind']!r}")
            return props[value["bind"]]
        return {k: bind(v, props) for k, v in value.items()}
    if isinstance(value, list):
        return [bind(v, props) for v in value]
    return value


def build_manifest(root=ROOT):
    design = root / "design"
    paths = sorted(p for p in design.rglob("*.json")
                   if p.parts[len(design.parts)] in {"libraries", "components", "pages", "tokens", "schemas"}
                   or p == design / "penpot.json")
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0" + path.read_bytes() + b"\0")
    for name in ("penpot_conformance.py", "penpot_collect.js", "penpot_transfer.js", "penpot_snapshot.py", "audit-penpot-drift.py", "validate-design.py"):
        path = root / "scripts" / name
        digest.update(name.encode() + b"\0" + path.read_bytes() + b"\0")
    load = lambda p: json.loads(p.read_text())
    config = load(design / "penpot.json")
    libraries = {}
    for path in sorted((design / "libraries").glob("*.library.json")):
        lib = load(path)
        for name, definition in lib["components"].items():
            libraries[(lib["library"], name)] = definition
    custom = {v["name"]: (p, v) for p in sorted((design / "components").glob("*.component.json"))
              for v in [load(p)]}
    manifest = {"version": VERSION, "fingerprint": digest.hexdigest(),
                "fileName": config["generatedFileName"], "scopes": {}, "families": {}, "blocked": []}
    for (lib, name), definition in libraries.items():
        family = normalize_family(config["libraryComponents"]["componentPrefix"] + name)
        contract = definition.get("penpotAudit")
        manifest["families"][family] = {"contract": contract, "kind": "library"}
        if not contract:
            manifest["blocked"].append(f"No audit contract for {lib}.{name}")
    for name in custom:
        family = normalize_family(config["customComponents"]["componentPrefix"] + name)
        manifest["families"][family] = {"kind": "custom"}

    def resolve(node, source, pointer, scope, parent=None, slot=None, props=None, stack=(), owner=None):
        node = bind(node, props or {})
        key = f"{scope}|{source}#{pointer}"
        kind = node["type"]
        result = {"key": key, "source": f"{source}#{pointer}", "name": node.get("name"),
                  "kind": kind, "parent": parent, "slot": slot, "children": [],
                  "props": node.get("props", {}), "design": node.get("design", {}),
                  "representation": "structural"}
        if kind == "text":
            result["text"] = node["value"]
            if node.get("hideWhenEmpty") is True and node["value"] == "":
                result["expectedVisible"] = False
                result["hiddenReason"] = "empty-text"
                if node.get("penpotEmptyPlaceholder") == " ":
                    result["penpotEmptyPlaceholder"] = " "
        if kind == "custom-component":
            name, variant = node["component"], node["variant"]
            if name in stack:
                raise ValueError(f"custom composition cycle: {' -> '.join((*stack, name))}")
            path, definition = custom[name]
            state = definition["variants"][variant]
            result.update(family=normalize_family(config["customComponents"]["componentPrefix"] + name),
                          representation="native", variant=variant)
            # The composition root IS the custom head, not another page instance.
            bound_props = {k: "" for k, spec in definition["props"].items()
                           if not spec.get("required") and spec["type"] == "string"}
            bound_props.update(node.get("props", {}))
            composition = bind(state["composition"], bound_props)
            expanded = resolve(composition, str(path.relative_to(root)),
                               f"/variants/{variant}/composition", scope, parent, slot,
                               stack=(*stack, name), owner=name)
            if expanded["representation"] != "shell":
                manifest["blocked"].append(f"{key}: custom root needs an approved shell or explicit root adapter")
            result["children"] = expanded["children"]
            # A composition may be instantiated more than once on the same page.
            # Namespace its locators by the page instance, not just the definition.
            for child in flatten(result["children"]):
                child["key"] = key + ">" + child["key"]
                if child["parent"] != expanded["key"]:
                    child["parent"] = key + ">" + child["parent"]
            for child in result["children"]:
                child["parent"] = key
            return result
        if kind == "library-component":
            name, lib = node["component"], node["library"]
            definition = libraries[(lib, name)]
            family = normalize_family(config["libraryComponents"]["componentPrefix"] + name)
            shell = (owner in config["customComponents"].get("structuralCardShells", []) and name == "Card")
            shell |= (scope in config.get("pageStructuralCardShells", []) and name == "Card")
            shell |= any(e == {"page": scope, "library": lib, "component": name}
                         for e in config.get("pageStructuralShells", []))
            result.update(family=family, representation="shell" if shell else "native",
                          contract=definition.get("penpotAudit"))
            for slot_name, children in node.get("slots", {}).items():
                for i, child in enumerate(children):
                    result["children"].append(resolve(child, source, f"{pointer}/slots/{slot_name}/{i}",
                                                       scope, key, slot_name, stack=stack))
        else:
            for i, child in enumerate(node.get("children", [])):
                result["children"].append(resolve(child, source, f"{pointer}/children/{i}",
                                                   scope, key, stack=stack))
        if result.get("family") == "Library/PrimeVue/AccordionPanel" and result["design"].get("state") == "collapsed":
            for child in result["children"]:
                if child["slot"] == "content":
                    for descendant in flatten([child]):
                        descendant["expectedVisible"] = False
        return result

    for path in sorted((design / "pages").rglob("*.page.json")):
        page = load(path)
        scope = page["page"]
        manifest["scopes"][scope] = {
            "page": config["featurePagePrefix"] + page["feature"]["label"],
            "frame": config["pageFramePrefix"] + scope, "mode": "page", "nodes": [
                resolve(n, str(path.relative_to(root)), f"/children/{i}", scope)
                for i, n in enumerate(page["children"])]}
    for name, (path, definition) in custom.items():
        for variant, state in definition["variants"].items():
            scope = f"custom:{name}:{variant}"
            node = resolve({"type": "custom-component", "component": name, "variant": variant,
                            "props": state["previewProps"]}, str(path.relative_to(root)),
                           f"/variants/{variant}", scope)
            manifest["scopes"][scope] = {"page": config["customComponents"]["pageName"],
                                          "mode": "custom", "family": node["family"],
                                          "variant": variant, "nodes": [node]}
    return manifest


def flatten(nodes):
    output = []
    pending = list(reversed(nodes))
    while pending:
        node = pending.pop()
        output.append(node)
        pending.extend(reversed(node.get("children", [])))
    return output


def emit_collector(manifest, transfer=False):
    source = Path(__file__).with_name("penpot_collect.js").read_text()
    if transfer:
        source = "storage.conformanceSnapshot = (() => {\n" + source + "\n})();\n"
        source += Path(__file__).with_name("penpot_transfer.js").read_text()
    return "const auditRequest = " + canonical({"version": VERSION, "fingerprint": manifest["fingerprint"],
                                               "fileName": manifest["fileName"]}) + ";\n" + source


def compare(manifest, snapshot, scopes=None, baseline=None, max_age=3600, allow_families=None, inspect=False):
    issues = []
    accepted_orphans = []
    preservation_checked = False
    def issue(code, location, message, blocked=False):
        issues.append({"code": code, "location": location, "message": message,
                       "severity": "blocked" if blocked else "error"})
    def report():
        status = "BLOCKED" if any(i["severity"] == "blocked" for i in issues) else "FAIL" if issues else "PASS"
        return {"status": status, "scope": "target" if scopes else "full",
                "mode": "inspection" if inspect else "synchronization" if scopes else "full",
                "preservationChecked": preservation_checked,
                "requestedScopes": scopes or list(manifest["scopes"]),
                "allowedFamilies": sorted(allow_families or []),
                "acceptedOrphans": accepted_orphans, "issues": issues}
    if inspect and (not scopes or baseline is not None or allow_families):
        issue("INVALID_INSPECTION_SCOPE", "scope",
              "inspection requires explicit scopes and forbids baseline/family change permissions", True)
        return report()
    try:
        if not isinstance(snapshot, dict) or snapshot.get("version") != VERSION:
            raise ValueError("snapshot version 2 required")
        if snapshot.get("fingerprint") != manifest["fingerprint"]:
            raise ValueError("snapshot source fingerprint is stale")
        if snapshot.get("fileName") != manifest["fileName"] or not snapshot.get("fileId"):
            raise ValueError("wrong or missing generated file identity")
        if snapshot.get("complete") is not True or snapshot.get("collectionErrors"):
            raise ValueError("snapshot collection is incomplete")
        if snapshot.get("coverage") != "full-file":
            raise ValueError("full-file collection coverage required, including for target baselines")
        captured = datetime.fromisoformat(snapshot["capturedAt"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - captured).total_seconds()
        if age < -60 or age > max_age:
            raise ValueError("snapshot timestamp is stale or in the future")
        nodes = snapshot["nodes"]
        records = snapshot["records"]
        pages = snapshot["pages"]
        if not all(isinstance(v, list) for v in (nodes, records, pages)):
            raise ValueError("nodes, records, pages must be arrays")
        for collection, required in ((pages, {"id", "name"}), (records, {"id", "family", "mainId", "variant"})):
            seen = set()
            for item in collection:
                if not isinstance(item, dict) or not required.issubset(item) or not isinstance(item["id"], str) or item["id"] in seen:
                    raise ValueError("malformed or duplicate page/component record")
                seen.add(item["id"])
        if any(not isinstance(r["family"], str) or not isinstance(r["variant"], dict) for r in records):
            raise ValueError("invalid component family/variant")
        ids = {}
        for n in nodes:
            if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in ids:
                raise ValueError("malformed or duplicate shape ID")
            if not all(k in n for k in ("parent", "pageId", "type", "name", "hidden", "opacity", "bounds", "copy", "head", "family", "componentId", "refId", "auditKey", "slot", "text")):
                raise ValueError("incomplete shape evidence")
            if not isinstance(n["hidden"], bool) or not isinstance(n["copy"], bool) or not isinstance(n["head"], bool):
                raise ValueError("visibility and native flags must be boolean")
            if not isinstance(n["opacity"], (int, float)) or isinstance(n["opacity"], bool) or not math.isfinite(n["opacity"]) or not 0 <= n["opacity"] <= 1:
                raise ValueError("invalid opacity")
            if "opacitySource" in n or "rawOpacity" in n:
                if "rawOpacity" not in n or "opacitySource" not in n:
                    raise ValueError("incomplete opacity provenance")
                raw = n["rawOpacity"]
                if n["opacitySource"] == "penpot-null-default-v1":
                    if raw is not None or n["opacity"] != 1:
                        raise ValueError("invalid null-default opacity evidence")
                elif n["opacitySource"] == "explicit":
                    if type(raw) not in (int, float) or raw != n["opacity"]:
                        raise ValueError("invalid explicit opacity evidence")
                else:
                    raise ValueError("unsupported opacity provenance")
            if not isinstance(n["name"], str) or not isinstance(n.get("variant"), dict):
                raise ValueError("invalid shape name/variant")
            if any(n[k] is not None and not isinstance(n[k], str) for k in ("parent", "family", "componentId", "refId", "slot", "text")):
                raise ValueError("invalid shape references/text")
            if n["auditKey"] is not None and not isinstance(n["auditKey"], str):
                raise ValueError("invalid semantic identity")
            if not isinstance(n["bounds"], list) or len(n["bounds"]) != 4 or not all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v) for v in n["bounds"]):
                raise ValueError("invalid shape bounds")
            ids[n["id"]] = n
        page_ids = {p["id"] for p in pages}
        for n in nodes:
            if n["pageId"] not in page_ids or (n["parent"] is not None and n["parent"] not in ids):
                raise ValueError("missing parent or page evidence")
            if n["parent"] is not None and ids[n["parent"]]["pageId"] != n["pageId"]:
                raise ValueError("cross-page parent reference")
            chain = set()
            a = n
            while a:
                if a["id"] in chain:
                    raise ValueError("cyclic shape hierarchy")
                chain.add(a["id"])
                a = ids.get(a["parent"])
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        issue("INVALID_SNAPSHOT", "snapshot", str(error), True)
        return report()
    for block in manifest["blocked"]:
        issue("UNSUPPORTED_CONTRACT", "manifest", block, True)
    selected = scopes or list(manifest["scopes"])
    if set(selected) - set(manifest["scopes"]):
        issue("UNKNOWN_SCOPE", "scope", "unknown requested scope", True)
        return report()
    allowed = {normalize_family(f) for f in (allow_families or [])}
    if allowed and (not scopes or baseline is None):
        issue("INVALID_CHANGE_SCOPE", "scope", "family permissions require explicit scopes and baseline", True)
        return report()
    if allowed - set(manifest["families"]):
        issue("UNKNOWN_FAMILY_SCOPE", "scope", "only registered families may be changed", True)
        return report()
    for scope_name, scope in manifest["scopes"].items():
        affected = any(e.get("family") in allowed for e in flatten(scope["nodes"]))
        if affected and scope_name not in selected:
            issue("DEPENDENT_SCOPE_REQUIRED", scope_name, "family permission requires validation of every dependent scope", True)
    if any(i["code"] == "DEPENDENT_SCOPE_REQUIRED" for i in issues):
        return report()
    children = {}
    record_map = {r["id"]: r for r in records}
    for n in nodes:
        children.setdefault(n["parent"], []).append(n)
    def descendants(root):
        found = []
        pending = [root]
        while pending:
            n = pending.pop()
            found.append(n)
            pending.extend(reversed(children.get(n["id"], [])))
        return found
    def visible(n):
        while n:
            if n["hidden"] or n["opacity"] <= 0:
                return False
            n = ids.get(n["parent"])
        return True
    def paired_nested_reference(n):
        """Verify a direct nested copy, optionally through one paired board.

        Nested copies can reference the corresponding nested copy in the
        enclosing main, rather than a shape in their standalone family main.
        Structural wrappers must pair by actual native references, not names
        or audit metadata. Arbitrary ancestry and extra depth are unsupported.
        """
        parent = ids.get(n["parent"])
        reference = ids.get(n["refId"])
        if not parent or not reference or not n["head"] or not n["copy"]:
            return False
        wrapper = None
        source_wrapper = None
        if not parent["head"]:
            wrapper = parent
            source_wrapper = ids.get(wrapper["refId"])
            parent = ids.get(wrapper["parent"])
            if (not parent or not source_wrapper
                    or wrapper["type"] != "board" or not wrapper["copy"]
                    or source_wrapper["type"] != "board"
                    or source_wrapper["head"] or source_wrapper["copy"]
                    or source_wrapper["componentId"] is not None
                    or source_wrapper["family"] is not None
                    or source_wrapper["variant"] != {}):
                return False
        parent_record = record_map.get(parent["componentId"])
        main = ids.get((parent_record or {}).get("mainId"))
        if not main or not parent["head"] or not parent["copy"]:
            return False
        if (parent["refId"] != main["id"] or not main["head"] or main["copy"]
                or main["componentId"] != parent_record["id"]
                or parent["family"] != parent_record["family"]
                or main["family"] != parent_record["family"]
                or parent["variant"] != parent_record["variant"]
                or main["variant"] != parent_record["variant"]
                or parent["family"] not in manifest["families"]):
            return False
        if wrapper is not None:
            if (source_wrapper["parent"] != main["id"]
                    or source_wrapper["refId"] is not None
                    or wrapper["pageId"] != parent["pageId"]
                    or source_wrapper["pageId"] != main["pageId"]
                    or any(wrapper[field] != parent[field]
                           for field in ("componentId", "family", "variant"))):
                return False
        source_parent = source_wrapper if wrapper is not None else main
        return (reference["parent"] == source_parent["id"]
                and reference["head"] and reference["copy"]
                and reference["componentId"] == n["componentId"]
                and reference["family"] == n["family"]
                and reference["variant"] == n["variant"]
                and reference["refId"] is None)
    def inside(n, parent):
        x, y, w, h = n["bounds"]
        px, py, pw, ph = parent["bounds"]
        return w >= 0 and h >= 0 and x >= px-2 and y >= py-2 and x+w <= px+pw+2 and y+h <= py+ph+2
    keys = {}
    for n in nodes:
        if n["auditKey"]:
            keys.setdefault(n["auditKey"], []).append(n)
    for key, matches in keys.items():
        if len(matches) != 1:
            issue("DUPLICATE_IDENTITY", key, f"found {len(matches)} shapes")
    protected = set()
    target_roots = {}
    for scope_name in selected:
        scope = manifest["scopes"][scope_name]
        pp = [p for p in pages if p["name"] == scope["page"]]
        if len(pp) != 1:
            issue("MISSING_PAGE", scope_name, "expected exactly one feature/template page")
            continue
        candidates = [n for n in nodes if n["pageId"] == pp[0]["id"]]
        if scope["mode"] == "page":
            roots = [n for n in candidates if n["parent"] is None and
                     normalize_family(n["name"]) == normalize_family(scope["frame"])]
        else:
            roots = [n for n in candidates if n["head"] and not n["copy"] and
                     n["family"] == scope["family"] and n.get("variant", {}).get("State") == scope["variant"]]
        if len(roots) != 1:
            issue("MISSING_ROOT", scope_name, f"expected one frame/variant root, found {len(roots)}")
            continue
        root = roots[0]
        root_record = record_map.get(root["componentId"])
        verified_custom_main = (
            scope["mode"] == "custom" and root["head"] and not root["copy"]
            and root["family"] == scope["family"]
            and manifest["families"].get(root["family"], {}).get("kind") == "custom"
            and root.get("variant", {}).get("State") == scope["variant"]
            and root_record is not None and root_record["mainId"] == root["id"]
            and root_record["family"] == root["family"]
            and root_record["variant"].get("State") == scope["variant"]
        )
        target_roots[scope_name] = root["id"]
        live = descendants(root)
        protected.update(n["id"] for n in live)
        used = {root["id"]} if scope["mode"] == "page" else set()
        matches = {}
        expected_nodes = flatten(scope["nodes"])
        for expected in expected_nodes:
            key = expected["key"]
            parent = matches.get(expected["parent"], root)
            pool = [n for n in live if n["id"] not in used]
            exact = keys.get(key, [])
            if exact:
                found = [n for n in exact if n in pool]
            elif expected.get("name"):
                found = [n for n in pool if n["name"] == expected["name"]]
            elif expected.get("family"):
                found = [n for n in pool if n["head"] and n["family"] == expected["family"]]
                if expected["representation"] == "shell":
                    found = []  # unnamed shells need stamped identity
            else:
                found = []
            if len(found) != 1:
                issue("MISSING_NODE" if not found else "AMBIGUOUS_NODE", key,
                      f"{expected['source']}: expected one semantic node, found {len(found)}", bool(found))
                continue
            n = found[0]
            matches[key] = n
            used.add(n["id"])
            if n["auditKey"] is not None and n["auditKey"] != key:
                issue("WRONG_IDENTITY", key, f"shape {n['id']} is stamped for {n['auditKey']}")
            # Slot wrappers may occur between a node and its semantic parent.
            ancestor = ids.get(n["parent"])
            while ancestor and ancestor["id"] != parent["id"] and ancestor.get("slot") == expected["slot"] and expected["slot"]:
                used.add(ancestor["id"])
                ancestor = ids.get(ancestor["parent"])
            is_custom_root = scope["mode"] == "custom" and expected["parent"] is None and n["id"] == root["id"]
            if not is_custom_root and (not ancestor or ancestor["id"] != parent["id"]):
                issue("WRONG_PARENT", key, f"must belong to {expected['parent'] or scope_name}")
            if expected["slot"] and n["slot"] != expected["slot"] and not any(
                    a.get("slot") == expected["slot"] for a in live if a["id"] == n["parent"]):
                issue("SLOT_UNVERIFIED", key, "slot metadata missing or incorrect", True)
            expected_visible = expected.get("expectedVisible", True)
            if expected_visible and not visible(n):
                issue("HIDDEN_CONTENT", key, "required node is hidden by itself or an ancestor")
            if not expected_visible and visible(n):
                if expected.get("hiddenReason") == "empty-text":
                    issue("EMPTY_TEXT_VISIBLE", key, "hideWhenEmpty text must be hidden when its bound value is empty")
                else:
                    issue("COLLAPSED_CONTENT_VISIBLE", key, "collapsed panel content must be hidden")
            if expected_visible and not inside(n, parent):
                issue("CONTAINMENT", key, "required content lies outside its semantic parent")
            if n["bounds"][2] <= 0 or n["bounds"][3] <= 0:
                issue("EMPTY_BOUNDS", key, "required artwork needs positive dimensions")
            rep = expected["representation"]
            if rep == "native":
                # componentRefShape() documents null inside main instances.
                # Only a library copy under this verified custom State main may
                # use its native component record/main instead. Preserve raw
                # null evidence; never infer or replace a reference shape ID.
                source_ancestor = ids.get(n["parent"])
                while source_ancestor and source_ancestor["id"] != root["id"]:
                    source_ancestor = ids.get(source_ancestor["parent"])
                nested_main_null_ref = (
                    n["refId"] is None and verified_custom_main
                    and source_ancestor is not None and source_ancestor["id"] == root["id"]
                    and n["head"] and n["copy"]
                    and manifest["families"].get(expected["family"], {}).get("kind") == "library"
                )
                if not n["copy"] and not is_custom_root:
                    issue("DETACHED_INSTANCE", key, "native copy required")
                if not n["head"] or n["family"] != expected["family"] or not n["componentId"] or (not is_custom_root and not n["refId"] and not nested_main_null_ref):
                    issue("WRONG_FAMILY", key, "native head, family and source reference required")
                record = record_map.get(n["componentId"])
                if not record or record["family"] != expected["family"] or record.get("mainId") not in ids:
                    issue("BROKEN_SOURCE", key, "source component record/main missing")
                else:
                    main = ids[record["mainId"]]
                    if not main["head"] or main["copy"] or main["family"] != expected["family"] or main["componentId"] != record["id"]:
                        issue("BROKEN_SOURCE", key, f"source {main['id']} must be its record's native main head")
                    if (not is_custom_root and not nested_main_null_ref
                            and n["refId"] not in {d["id"] for d in descendants(main)}
                            and not paired_nested_reference(n)):
                        issue("BROKEN_SOURCE", key, "reference is not part of its native main subtree")
                    if "variant" in expected and (record["variant"].get("State") != expected["variant"] or main["variant"].get("State") != expected["variant"]):
                        issue("WRONG_VARIANT", key, "source record and main must match the requested State")
                if "variant" in expected and n.get("variant", {}).get("State") != expected["variant"]:
                    issue("WRONG_VARIANT", key, f"expected State={expected['variant']}")
            elif n["type"] != ("text" if expected["kind"] == "text" else "board") or n["head"]:
                issue("WRONG_REPRESENTATION", key, "expected structural board/text, not native component head")
            placeholder = False
            if (expected["kind"] == "text" and expected.get("text") == ""
                    and expected.get("hiddenReason") == "empty-text"
                    and expected.get("expectedVisible") is False
                    and expected.get("penpotEmptyPlaceholder") == " " and n["text"] == " "
                    and n["hidden"] and n["copy"] and not n["head"]):
                record = record_map.get(n["componentId"])
                main = ids.get((record or {}).get("mainId"))
                source = ids.get(n["refId"])
                owner = ids.get(n["parent"])
                while owner and not owner["head"]:
                    owner = ids.get(owner["parent"])
                placeholder = bool(main and source and owner
                    and main["head"] and not main["copy"]
                    and main["componentId"] == record["id"]
                    and n["family"] == main["family"] == record["family"]
                    and n["variant"] == main["variant"] == record["variant"]
                    and source in descendants(main) and source["type"] == "text"
                    and not source["head"] and source["name"] == n["name"]
                    and owner["copy"] and owner["componentId"] == record["id"]
                    and owner["refId"] == main["id"]
                    and owner["family"] == main["family"] and owner["variant"] == main["variant"])
            if expected["kind"] == "text" and n["text"] != expected["text"] and not placeholder:
                issue("TEXT_MISMATCH", key, f"expected {expected['text']!r}, found {n['text']!r}")
            contract = expected.get("contract")
            if contract:
                verify_control(expected, n, descendants(n), visible, used, issue)
        # Omitted native branches require exact paired source topology, not names
        # or inherited invisibility. Invalid remnants remain unexpected artwork.
        for expected in expected_nodes:
            owner = matches.get(expected["key"])
            if not owner:
                continue
            for branch in expected.get("contract", {}).get("inactiveNativeBranches", []):
                if any(c["slot"] == branch["slot"] for c in expected["children"]):
                    continue
                record = record_map.get(owner["componentId"])
                main = ids.get((record or {}).get("mainId"))
                if not (main and owner["copy"] and owner["head"] and owner["refId"] == main["id"]
                        and owner["family"] == main["family"] == record["family"] == "Library/PrimeVue/Toolbar"
                        and main["head"] and not main["copy"] and main["componentId"] == record["id"]
                        and owner["variant"] == main["variant"] == record["variant"]):
                    continue
                sources = [c for c in children.get(main["id"], []) if c["name"] == branch["sourceName"]]
                if len(sources) != 1:
                    continue
                source = sources[0]
                copies = [c for c in children.get(owner["id"], []) if c["refId"] == source["id"]]
                if len(copies) != 1:
                    continue
                candidate = copies[0]
                source_children = children.get(source["id"], [])
                copy_children = children.get(candidate["id"], [])
                native_record = record_map.get(source["componentId"])
                native_main = ids.get((native_record or {}).get("mainId"))
                if not (candidate["hidden"] and source["hidden"] and candidate["copy"] and candidate["head"]
                        and source["copy"] and source["head"] and source["refId"] is None
                        and candidate["family"] == source["family"] == branch["family"]
                        and candidate["componentId"] == source["componentId"]
                        and candidate["variant"] == source["variant"]
                        and native_main and native_main["head"] and not native_main["copy"]
                        and native_main["componentId"] == native_record["id"]
                        and native_main["family"] == native_record["family"] == source["family"]
                        and native_main["variant"] == native_record["variant"] == source["variant"]
                        and candidate["auditKey"] is None and candidate["slot"] is None
                        and len(source_children) == len(copy_children) == len(branch["children"])
                        and sorted(c["name"] for c in source_children) == sorted(branch["children"])):
                    continue
                paired = set()
                for child in copy_children:
                    ref = ids.get(child["refId"])
                    if not (ref in source_children and ref["id"] not in paired
                            and not children.get(child["id"]) and not children.get(ref["id"])
                            and child["copy"] and not child["head"] and ref["copy"] and not ref["head"]
                            and ref["refId"] is None and child["type"] == ref["type"] == "text"
                            and child["name"] == ref["name"]
                            and child["family"] == ref["family"] == source["family"]
                            and child["componentId"] == ref["componentId"] == source["componentId"]
                            and child["variant"] == ref["variant"] == source["variant"]
                            and child["auditKey"] is None and child["slot"] is None):
                        break
                    paired.add(ref["id"])
                else:
                    used.update(c["id"] for c in [candidate, *copy_children])
        # Other internal artwork is allowed only through a family's explicit name list.
        for n in live:
            if n["id"] in used:
                continue
            ancestor = ids.get(n["parent"])
            while ancestor and ancestor["id"] not in used:
                ancestor = ids.get(ancestor["parent"])
            expected_parent = next((e for e in expected_nodes if matches.get(e["key"], {}).get("id") == (ancestor or {}).get("id")), None)
            allowed_internals = (expected_parent or {}).get("contract", {}).get("internals", [])
            if n["name"] in allowed_internals and not n["head"]:
                used.add(n["id"])
                if n["type"] == "text" and visible(n) and n["text"]:
                    issue("UNEXPECTED_TEXT", scope_name, f"unaccounted visible template text {n['name']}: {n['text']!r}")
            else:
                issue("UNEXPECTED_NODE", scope_name, f"unaccounted artwork {n['id']} {n['name']}")
    if scopes and not inspect:
        if baseline is None:
            issue("BASELINE_REQUIRED", "scope", "target verification needs a before snapshot", True)
        else:
            before_report = compare(manifest, baseline, max_age=max_age)
            if any(i["code"] == "INVALID_SNAPSHOT" for i in before_report["issues"]) or baseline.get("fileId") != snapshot["fileId"]:
                issue("INVALID_BASELINE", "scope", "baseline must be complete, fresh and from the same file", True)
            else:
                preservation_checked = True
                def template_ids(s):
                    by_parent = {}
                    by_id = {n["id"]: n for n in s["nodes"]}
                    for n in s["nodes"]:
                        by_parent.setdefault(n["parent"], []).append(n["id"])
                    pending = [r["mainId"] for r in s["records"] if r["family"] in allowed]
                    found = set()
                    while pending:
                        id_ = pending.pop()
                        if id_ not in by_id or id_ in found:
                            continue
                        found.add(id_)
                        pending.extend(by_parent.get(id_, []))
                    return found
                # Classify both snapshots independently: deleted target children
                # are permitted; moving protected artwork into a target fails.
                old_template = template_ids(baseline)
                new_template = template_ids(snapshot)
                old_target = set()
                baseline_children = {}
                for n in baseline["nodes"]:
                    baseline_children.setdefault(n["parent"], []).append(n)
                for scope_name in selected:
                    spec = manifest["scopes"][scope_name]
                    page_ids = {p["id"] for p in baseline["pages"] if p["name"] == spec["page"]}
                    roots = [n for n in baseline["nodes"] if n["pageId"] in page_ids and (
                        spec["mode"] == "page" and n["parent"] is None and normalize_family(n["name"]) == normalize_family(spec["frame"])
                        or spec["mode"] == "custom" and n["head"] and not n["copy"] and n["family"] == spec["family"] and n["variant"].get("State") == spec["variant"])]
                    if len(roots) > 1:
                        issue("AMBIGUOUS_BASELINE_ROOT", scope_name, "baseline target root is ambiguous", True)
                    if len(roots) == 1 and scope_name in target_roots and roots[0]["id"] != target_roots[scope_name]:
                        issue("TARGET_ROOT_REPLACED", scope_name, "update existing target by stable identity, not root replacement")
                    pending = list(roots)
                    while pending:
                        n = pending.pop()
                        old_target.add(n["id"])
                        pending.extend(baseline_children.get(n["id"], []))
                old = {n["id"]: n for n in baseline["nodes"] if n["id"] not in old_target | old_template}
                new = {n["id"]: n for n in nodes if n["id"] not in protected | new_template}
                # Root IDs must be preserved; removing a target root cannot evade protection.
                for id_ in sorted(set(old) | set(new)):
                    if old.get(id_) != new.get(id_):
                        issue("PROTECTED_CHANGE", id_, "outside-target shape added, removed or changed")
                old_records = {r["id"]: r for r in baseline["records"] if r["family"] not in allowed}
                new_records = {r["id"]: r for r in records if r["family"] not in allowed}
                if old_records != new_records or {p["id"]: p for p in baseline["pages"]} != {p["id"]: p for p in pages}:
                    issue("PROTECTED_CHANGE", "templates", "component records or page identities changed")
                for family in allowed:
                    matching = [r for r in records if r["family"] == family]
                    if not matching or any(r["mainId"] not in ids or ids[r["mainId"]]["copy"] or not ids[r["mainId"]]["head"] or ids[r["mainId"]]["family"] != family for r in matching):
                        issue("INVALID_TEMPLATE", family, "allowed template must retain observed native mains")
                    wanted_states = [s["variant"] for s in manifest["scopes"].values() if s["mode"] == "custom" and s["family"] == family]
                    if wanted_states:
                        if sorted(str(r["variant"].get("State")) for r in matching) != sorted(wanted_states):
                            issue("TEMPLATE_STATES", family, "changed custom records must match all declared State variants")
                    elif len(matching) != 1:
                        issue("TEMPLATE_COUNT", family, "changed library must have exactly one main record")
    elif not scopes:
        for record in records:
            if (snapshot["fileId"] == LEGACY_ORPHAN_FILE_ID
                    and record["id"] in LEGACY_ORPHANS):
                expected_family = LEGACY_ORPHANS[record["id"]]
                dependencies = [n["id"] for n in nodes
                                if n["componentId"] == record["id"]
                                or n["refId"] == record["id"]
                                or n["family"] == expected_family]
                if (record["family"] == expected_family
                        and record["mainId"] is None
                        and record["variant"] == {} and not dependencies):
                    accepted_orphans.append({"id": record["id"], "family": expected_family,
                                             "reason": "Approved undeletable orphan; no main or live dependencies"})
                    continue
                issue("LEGACY_ORPHAN_CHANGED", record["id"],
                      "approved orphan must retain its exact family, null main, empty variants and no live dependencies")
            if record["family"] not in manifest["families"]:
                issue("UNKNOWN_FAMILY", record["id"], record["family"])
            if not record.get("mainId"):
                issue("ORPHAN_RECORD", record["id"], "component has no main")
        # Strays outside known frames on feature pages are not silently ignored.
        feature_pages = {s["page"] for s in manifest["scopes"].values() if s["mode"] == "page"}
        for n in nodes:
            if n["parent"] is None and n["id"] not in protected and any(p["id"] == n["pageId"] and p["name"] in feature_pages for p in pages):
                issue("STRAY_ARTWORK", n["id"], n["name"])
        for family, definition in manifest["families"].items():
            matching = [r for r in records if r["family"] == family and r.get("mainId")]
            wanted_states = [s["variant"] for s in manifest["scopes"].values()
                             if s["mode"] == "custom" and s["family"] == family]
            if wanted_states:
                actual_states = [r["variant"].get("State") for r in matching]
                if sorted(str(s) for s in actual_states) != sorted(wanted_states):
                    issue("TEMPLATE_STATES", family, f"expected State variants {wanted_states}, found {actual_states}")
            elif len(matching) != 1:
                issue("TEMPLATE_COUNT", family, f"expected one component record with main, found {len(matching)}")
            for record in matching:
                main = ids.get(record["mainId"])
                if not main or main["family"] != family or not main["head"] or main["copy"]:
                    issue("INVALID_TEMPLATE", family, "main must be an observed native main head")
    return report()


def verify_control(expected, head, subtree, visible, used, issue):
    """Assert observable control content; never trust an asserted state stamp."""
    key, contract, props = expected["key"], expected["contract"], expected["props"]
    def role(name):
        return [n for n in subtree if n["id"] != head["id"] and n["name"] == name]
    for prop, name in contract.get("textProps", {}).items():
        if prop not in props:
            continue
        found = role(name)
        if len(found) != 1 or found[0]["type"] != "text" or found[0]["head"] or not visible(found[0]) or found[0]["text"] != str(props[prop]):
            issue("CONTROL_TEXT", key, f"{name} must visibly represent {prop}={props[prop]!r}")
        used.update(n["id"] for n in found)
    adapter = contract["adapter"]
    family = expected.get("family")
    state = expected.get("design", {}).get("state")
    if family == "Library/PrimeVue/Avatar" and state == "locked":
        if not 0 < head["opacity"] <= 0.6:
            issue("LOCKED_APPEARANCE", key, "locked Avatar requires visible muted opacity at most 0.6")
    if family == "Library/PrimeVue/Timeline":
        items = props.get("value", [])
        expected_ids = set()
        previous_bottom = None
        for index, item in enumerate(items):
            rows = role(f"TimelineItem{index}")
            row = rows[0] if len(rows) == 1 else None
            content = [n for n in subtree if row and n["parent"] == row["id"] and n["name"] == "Content"]
            texts = {name: [n for n in subtree if content and n["parent"] == content[0]["id"] and n["name"] == name]
                     for name in ("Title", "Time")}
            markers = [n for n in subtree if row and n["parent"] == row["id"] and n["name"] == "Marker"]
            values = {"Title": f"{item.get('icon', '')} {item.get('title', '')}".strip(),
                      "Time": f"{item.get('description', '')}\n{item.get('time', '')}"}
            valid = (row and row["parent"] == head["id"] and row["type"] == "board" and not row["head"]
                     and len(content) == 1 and content[0]["type"] == "board" and not content[0]["head"]
                     and len(markers) == 1 and markers[0]["type"] == "ellipse" and not markers[0]["head"]
                     and all(visible(n) for n in [row, *content, *markers])
                     and all(len(texts[name]) == 1 and texts[name][0]["type"] == "text"
                             and not texts[name][0]["head"] and visible(texts[name][0])
                             and texts[name][0]["text"] == value for name, value in values.items()))
            if not valid:
                issue("TIMELINE_ITEM", key, f"TimelineItem{index} must visibly represent its ordered value")
            if row:
                if previous_bottom is not None and row["bounds"][1] < previous_bottom - 2:
                    issue("TIMELINE_ORDER", key, "Timeline rows must follow value order without overlap")
                previous_bottom = row["bounds"][1] + row["bounds"][3]
            expected_ids.update(n["id"] for n in [*rows, *content, *markers, *texts["Title"], *texts["Time"]])
        used.update(expected_ids)
    if family == "Library/PrimeVue/Accordion":
        selected = props.get("value", [])
        panels = expected.get("children", [])
        if not isinstance(selected, list) or not panels or any(
                p.get("family") != "Library/PrimeVue/AccordionPanel" or
                p.get("design", {}).get("state") != ("expanded" if p.get("props", {}).get("value") in selected else "collapsed")
                for p in panels) or (state == "expanded") != bool(selected):
            issue("ACCORDION_STATE", key, "selected values and panel expanded/collapsed states must agree")
    if family == "Library/PrimeVue/AccordionPanel":
        slots = {c.get("slot") for c in expected.get("children", [])}
        if not {"header", "content"}.issubset(slots):
            issue("PANEL_EVIDENCE", key, "panel adapter requires semantic header and content evidence", True)
        if "Secondary" in contract.get("internals", []) and state in ("collapsed", "expanded"):
            indicators = role("Secondary")
            glyph = "⌃" if state == "expanded" else "⌄"
            x, y, w, h = head["bounds"]
            if len(indicators) != 1 or not all(
                    n["parent"] == head["id"] and n["type"] == "text"
                    and not n["head"] and visible(n) and n["text"] == glyph
                    and n["bounds"][2] > 0 and n["bounds"][3] > 0
                    and n["bounds"][0] >= x - 2 and n["bounds"][1] >= y - 2
                    and n["bounds"][0] + n["bounds"][2] <= x + w + 2
                    and n["bounds"][1] + n["bounds"][3] <= y + h + 2
                    for n in indicators):
                issue("PANEL_INDICATOR", key, "one visible contained Secondary chevron must match panel state")
            else:
                used.add(indicators[0]["id"])
    if adapter == "progress":
        values, indicators = role("Value"), role("Indicator")
        if props.get("showValue") is False and any(visible(n) for n in values):
            issue("VISIBLE_PERCENTAGE", key, "showValue=false requires hidden Value")
        if not indicators or not any(visible(n) and n["bounds"][2] > 0 for n in indicators):
            issue("MISSING_INDICATOR", key, "visible progress indicator required")
        if props.get("mode") == "indeterminate" and indicators:
            x, _, w, _ = head["bounds"]
            if not any(x < n["bounds"][0] and n["bounds"][0]+n["bounds"][2] < x+w for n in indicators):
                issue("PROGRESS_MODE", key, "indeterminate segment must float within track")
        elif "value" in props and indicators:
            track_width = head["bounds"][2] - 8
            expected_width = track_width * props["value"] / 100
            if not any(abs(n["bounds"][2] - expected_width) <= 3 for n in indicators):
                issue("PROGRESS_VALUE", key, "indicator must represent determinate value within representative tolerance")
        used.update(n["id"] for n in values + indicators)
    if adapter == "options":
        options = props.get("options", [])
        for i, text in enumerate(options):
            option = role(f"Option{i}")
            labels = [n for n in subtree if option and n["parent"] == option[0]["id"] and n["name"] == "Label"]
            norm = lambda s: " ".join(str(s).replace("·", " ").split())
            if len(option) != 1 or option[0]["head"] or len(labels) != 1 or labels[0]["type"] != "text" or not visible(labels[0]) or norm(labels[0]["text"]) != norm(text):
                issue("OPTION_MISMATCH", key, f"Option{i} must visibly represent {text!r}")
            used.update(n["id"] for n in option + labels)
    if adapter == "button" and props.get("icon"):
        glyph = contract.get("icons", {}).get(props["icon"])
        if glyph is None:
            issue("UNSUPPORTED_ICON", key, f"no icon evidence adapter for {props['icon']}", True)
        elif not any(visible(n) and n["text"] == glyph for n in subtree):
            issue("MISSING_ICON", key, f"visible {glyph!r} required")
        else:
            used.update(n["id"] for n in subtree if n["text"] == glyph)
    if adapter == "button" and props.get("variant") in {"text", "link"} and head.get("fills"):
        if any(f.get("fillOpacity", 1) > 0 and f.get("fillColor", "").upper() not in {"#FFFFFF", "#F9FAFB"} for f in head["fills"]):
            issue("BUTTON_VARIANT", key, "text/link Button must not have a filled primary surface")
    state = expected.get("design", {}).get("state")
    if adapter == "button":
        if state == "disabled" and props.get("disabled") is not True:
            issue("BUTTON_STATE", key, "disabled design state requires disabled=true")
        if props.get("disabled") is True or state == "disabled":
            if not 0 < head["opacity"] <= 0.6:
                issue("DISABLED_APPEARANCE", key, "disabled Button needs a visible muted surface (opacity at most 0.6)")
        if state == "loading" and props.get("loading") is not True:
            issue("BUTTON_STATE", key, "loading design state requires loading=true")
    if adapter == "button" and props.get("loading"):
        loaders = role("LoadingIndicator")
        if not any(visible(n) for n in loaders):
            issue("MISSING_LOADER", key, "loading Button needs visible LoadingIndicator")
        used.update(n["id"] for n in loaders)
    if state not in contract.get("observableStates", []):
        issue("STATE_UNVERIFIED", key, f"no observable adapter for state {state!r}", True)