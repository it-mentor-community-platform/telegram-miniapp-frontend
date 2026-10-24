#!/usr/bin/env python3
"""Validate library-first JSON UI design specifications."""

from __future__ import annotations
import json, re, sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design"
TOKENS = DESIGN / "tokens" / "tokens.json"
LIBRARIES = DESIGN / "libraries"
COMPONENTS = DESIGN / "components"
PAGES = DESIGN / "pages"
SCHEMAS = DESIGN / "schemas"
PENPOT = DESIGN / "penpot.json"
WORKSPACE = ROOT.parent
SCHEMA_FILES = {SCHEMAS / name for name in ("library.schema.json", "node.schema.json", "page.schema.json", "custom-component.schema.json")}
TOKEN_REF = re.compile(r"^(color|spacing|radius|font)\.[A-Za-z0-9_.-]+$")
NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NODE_TYPES = {"library-component", "custom-component", "column", "grid", "row", "section", "text"}
STRUCTURAL = {"column", "grid", "row", "section"}
GENERIC_CUSTOM = {"Accordion", "Avatar", "Badge", "Button", "Card", "IconField", "Input", "InputText", "Message", "ProgressBar", "ProgressSpinner", "SelectButton", "Skeleton", "Tag", "Textarea", "Timeline", "Toolbar"}

@dataclass(frozen=True)
class Document:
    path: Path
    value: Any

class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.tokens: dict[str, Any] = {}
        self.libraries: dict[str, Document] = {}
        self.library_components: dict[tuple[str, str], dict[str, Any]] = {}
        self.custom_components: dict[str, Document] = {}
        self.custom_dependencies: dict[str, set[str]] = {}
        self.pages: dict[str, Document] = {}
        self.features: dict[str, str] = {}
        self.feature_labels: dict[str, str] = {}
        self.library_refs = 0
        self.custom_refs = 0

    def error(self, path: Path, location: str, message: str) -> None:
        suffix = f" at {location}" if location else ""
        self.errors.append(f"{path.relative_to(ROOT)}{suffix}: {message}")

    def load(self, path: Path) -> Document | None:
        if not path.is_file():
            self.error(path, "", "required file does not exist")
            return None
        try:
            return Document(path, json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as exc:
            self.error(path, f"line {exc.lineno}, column {exc.colno}", exc.msg)
            return None

    def object(self, document: Document, kind: str) -> dict[str, Any] | None:
        if not isinstance(document.value, dict):
            self.error(document.path, "$", f"{kind} must be an object")
            return None
        return document.value

    def schema_ref(self, value: dict[str, Any], path: Path, expected: str) -> None:
        if value.get("$schema") != expected:
            self.error(path, "$.$schema", f"must be {expected!r}")

    def token_exists(self, reference: str) -> bool:
        current: Any = self.tokens
        for segment in reference.split("."):
            if not isinstance(current, dict) or segment not in current:
                return False
            current = current[segment]
        return not isinstance(current, (dict, list))

    def token_refs(self, value: Any, path: Path, location: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items(): self.token_refs(child, path, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value): self.token_refs(child, path, f"{location}[{index}]")
        elif isinstance(value, str) and TOKEN_REF.fullmatch(value) and not self.token_exists(value):
            self.error(path, location, f"unknown token reference {value!r}")

    def validate_tokens(self) -> None:
        doc = self.load(TOKENS)
        if not doc: return
        value = self.object(doc, "token document")
        if value is None: return
        self.tokens = value
        for namespace in ("color", "spacing", "radius", "font"):
            if not isinstance(value.get(namespace), dict): self.error(doc.path, f"$.{namespace}", "must be an object")
        self._token_leaves(value, doc.path)

    def _token_leaves(self, value: Any, path: Path, location: str = "$") -> None:
        if isinstance(value, dict):
            if not value: self.error(path, location, "token group must not be empty")
            for key, child in value.items(): self._token_leaves(child, path, f"{location}.{key}")
        elif not (isinstance(value, (str, int, float)) and not isinstance(value, bool)):
            self.error(path, location, "token value must be a string or number")

    def validate_schemas(self) -> None:
        for path in sorted(SCHEMA_FILES):
            doc = self.load(path)
            if doc and isinstance(doc.value, dict) and doc.value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                self.error(path, "$.$schema", "must use JSON Schema draft 2020-12")

    def validate_libraries(self) -> None:
        paths = sorted(LIBRARIES.glob("*.library.json"))
        if not paths: self.error(LIBRARIES, "", "no component library registry found")
        for path in paths:
            doc = self.load(path)
            if not doc: continue
            value = self.object(doc, "library registry")
            if value is None: continue
            self.schema_ref(value, path, "../schemas/library.schema.json")
            library = value.get("library")
            if not isinstance(library, str) or not KEBAB.fullmatch(library):
                self.error(path, "$.library", "must be kebab-case"); continue
            if library in self.libraries: self.error(path, "$.library", f"duplicate library {library!r}")
            self.libraries[library] = doc
            implementation = value.get("implementation")
            if not isinstance(implementation, dict) or not isinstance(implementation.get("majorVersion"), int):
                self.error(path, "$.implementation", "must declare package and integer majorVersion")
            penpot = value.get("penpot")
            if not isinstance(penpot, dict) or penpot.get("fidelity") != "representative":
                self.error(path, "$.penpot", "must declare representative fidelity")
            definitions = value.get("components")
            if not isinstance(definitions, dict) or not definitions:
                self.error(path, "$.components", "must be a non-empty object"); continue
            for component, definition in definitions.items():
                loc = f"$.components.{component}"
                if not NAME.fullmatch(component): self.error(path, loc, "key must use PascalCase"); continue
                if not isinstance(definition, dict): self.error(path, loc, "must be an object"); continue
                self.library_components[(library, component)] = definition
                if not isinstance(definition.get("import"), str): self.error(path, f"{loc}.import", "must be a string")
                props = definition.get("props")
                if not isinstance(props, dict): self.error(path, f"{loc}.props", "must be an object")
                else:
                    for prop, spec in props.items():
                        if not isinstance(spec, dict) or spec.get("type") not in {"string", "number", "boolean", "array", "object"}:
                            self.error(path, f"{loc}.props.{prop}", "must declare a supported type")
                if not isinstance(definition.get("slots"), list): self.error(path, f"{loc}.slots", "must be an array")
                audit = definition.get("penpotAudit")
                if not isinstance(audit, dict) or set(audit) - {"adapter", "internals", "textProps", "observableStates", "icons", "inactiveNativeBranches"}:
                    self.error(path, f"{loc}.penpotAudit", "must declare a supported audit contract")
                else:
                    branches = audit.get("inactiveNativeBranches", [])
                    approved = [dict(sourceName=name, slot=slot, family="Library/PrimeVue/Button",
                                     children=["Label", "TrailingIcon"])
                                for name, slot in (("BackButton", "start"), ("EndButton", "end"))]
                    if "inactiveNativeBranches" in audit and (
                            library != "primevue" or component != "Toolbar" or branches != approved):
                        self.error(path, f"{loc}.penpotAudit.inactiveNativeBranches", "must match the approved Toolbar native-branch contract")
                    if audit.get("adapter") not in {"container", "text", "button", "progress", "options", "shape"}:
                        self.error(path, f"{loc}.penpotAudit.adapter", "unsupported audit adapter")
                    for key in ("internals", "observableStates"):
                        items = audit.get(key)
                        if not isinstance(items, list) or not all(isinstance(x, str) and x for x in items) or len(items) != len(set(items)):
                            self.error(path, f"{loc}.penpotAudit.{key}", "must be unique non-empty strings")
                    for key in ("textProps", "icons"):
                        items = audit.get(key, {} if key == "icons" else None)
                        if not isinstance(items, dict) or not all(isinstance(k, str) and isinstance(v, str) and v for k, v in items.items()):
                            self.error(path, f"{loc}.penpotAudit.{key}", "must map strings to non-empty strings")
                    if isinstance(audit.get("textProps"), dict) and isinstance(props, dict):
                        for prop in set(audit["textProps"]) - set(props):
                            self.error(path, f"{loc}.penpotAudit.textProps", f"unknown prop {prop!r}")
                template = definition.get("penpotTemplate")
                if isinstance(template, dict) and "colorTreatments" in template and (
                        library != "primevue" or component not in {"Button", "Tag", "SelectButton"}
                        or template["colorTreatments"] != ["accessible-blue"]):
                    self.error(path, f"{loc}.penpotTemplate.colorTreatments", "must match the approved accessible-blue control contract")
                if not isinstance(template, dict): self.error(path, f"{loc}.penpotTemplate", "must be an object")
                else:
                    for key in ("appearances", "states"):
                        items = template.get(key)
                        if not isinstance(items, list) or not items: self.error(path, f"{loc}.penpotTemplate.{key}", "must be non-empty")

    def validate_custom_components(self) -> None:
        for path in sorted(COMPONENTS.glob("*.components.json")):
            self.error(path, "", "legacy *.components.json is unsupported; use *.component.json")
        for path in sorted(COMPONENTS.glob("*.component.json")):
            doc = self.load(path)
            if not doc: continue
            value = self.object(doc, "custom component")
            if value is None: continue
            self.schema_ref(value, path, "../schemas/custom-component.schema.json")
            if value.get("kind") != "custom-component": self.error(path, "$.kind", "must be 'custom-component'")
            name = value.get("name")
            if not isinstance(name, str) or not NAME.fullmatch(name): self.error(path, "$.name", "must use PascalCase"); continue
            filename = re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower() + ".component.json"
            if path.name != filename: self.error(path, "$.name", f"filename must be {filename!r}")
            if name in GENERIC_CUSTOM or any(component == name for _, component in self.library_components):
                self.error(path, "$.name", f"generic control {name!r} must use the library")
            if name in self.custom_components: self.error(path, "$.name", f"duplicate custom component {name!r}")
            self.custom_components[name] = doc
            if not isinstance(value.get("rationale"), str) or not value["rationale"].strip(): self.error(path, "$.rationale", "is required")
            props = value.get("props")
            if not isinstance(props, dict): self.error(path, "$.props", "must be an object")
            variants = value.get("variants")
            if not isinstance(variants, dict) or not variants: self.error(path, "$.variants", "must be non-empty")
            self.token_refs(value, path)
        # Register all families before validating any state's dependencies.
        for name, doc in self.custom_components.items():
            self.validate_custom_states(doc, name)
        self.validate_cycles()

    def validate_custom_states(self, doc: Document, name: str) -> None:
        value, path = doc.value, doc.path
        allowed = {"$schema", "kind", "name", "rationale", "props", "variants"}
        for key in set(value) - allowed:
            self.error(path, f"$.{key}", "unsupported custom field; use complete per-state compositions")
        declared = value.get("props", {})
        if not isinstance(declared, dict): return
        for prop, spec in declared.items():
            if not isinstance(spec, dict) or spec.get("type") not in {"string", "number", "boolean", "array", "object"}:
                self.error(path, f"$.props.{prop}", "must declare a supported type")
                return
        variants = value.get("variants")
        if not isinstance(variants, dict): return
        deps: set[str] = set()
        for state, variant in variants.items():
            loc = f"$.variants.{state}"
            if not re.fullmatch(r"[a-z][A-Za-z0-9]*", state): self.error(path, loc, "state must use lowerCamelCase")
            if not isinstance(variant, dict) or set(variant) != {"previewProps", "composition"}:
                self.error(path, loc, "must contain exactly previewProps and composition"); continue
            preview, tree = variant["previewProps"], variant["composition"]
            if not isinstance(preview, dict): self.error(path, f"{loc}.previewProps", "must be an object"); continue
            for prop, item in preview.items():
                if prop not in declared: self.error(path, f"{loc}.previewProps.{prop}", "unknown preview prop")
                else: self.validate_value(item, declared[prop]["type"], path, f"{loc}.previewProps.{prop}", None)
            for prop, spec in declared.items():
                if spec.get("required") and prop not in preview: self.error(path, f"{loc}.previewProps", f"missing required prop {prop!r}")
            self.validate_node(tree, path, f"{loc}.composition", name, deps)
            seen: set[str] = set()
            def inspect(node: Any, location: str) -> None:
                if not isinstance(node, dict): return
                node_name = node.get("name")
                if not isinstance(node_name, str) or not NAME.fullmatch(node_name): self.error(path, f"{location}.name", "every state node requires a PascalCase name")
                elif node_name in seen: self.error(path, f"{location}.name", f"duplicate node name {node_name!r}")
                else: seen.add(node_name)
                def bindings(item: Any) -> None:
                    if isinstance(item, dict):
                        if set(item) == {"bind"}:
                            bound = item["bind"]
                            if isinstance(bound, str) and bound in declared and bound not in preview: self.error(path, f"{loc}.previewProps", f"missing bound preview prop {bound!r}")
                        else:
                            for child in item.values(): bindings(child)
                    elif isinstance(item, list):
                        for child in item: bindings(child)
                bindings(node.get("props", {})); bindings(node.get("value"))
                if node.get("type") == "library-component":
                    definition = self.library_components.get((node.get("library"), node.get("component")), {})
                    node_props = node.get("props", {})
                    if isinstance(node_props, dict):
                        for prop, item in node_props.items():
                            if isinstance(item, dict) and set(item) == {"bind"} and isinstance(item["bind"], str) and item["bind"] in preview:
                                spec = definition.get("props", {}).get(prop, {})
                                sample = preview[item["bind"]]
                                if spec.get("enum") and sample not in spec["enum"]: self.error(path, f"{location}.props.{prop}", f"bound preview must be one of {spec['enum']}")
                children = node.get("children", [])
                if isinstance(children, list):
                    for i, child in enumerate(children): inspect(child, f"{location}.children[{i}]")
                slots = node.get("slots", {})
                if isinstance(slots, dict):
                    for slot, children in slots.items():
                        if isinstance(children, list):
                            for i, child in enumerate(children): inspect(child, f"{location}.slots.{slot}[{i}]")
            inspect(tree, f"{loc}.composition")
        self.custom_dependencies[name] = deps

    def validate_cycles(self) -> None:
        visiting: set[str] = set(); visited: set[str] = set()
        def visit(name: str, trail: list[str]) -> None:
            if name in visiting:
                self.error(self.custom_components[name].path, "$.variants", f"cycle: {' -> '.join(trail + [name])}"); return
            if name in visited: return
            visiting.add(name)
            for dep in self.custom_dependencies.get(name, set()):
                if dep in self.custom_components: visit(dep, trail + [name])
            visiting.remove(name); visited.add(name)
        for name in self.custom_components: visit(name, [])

    def validate_pages(self) -> None:
        paths = sorted(PAGES.rglob("*.page.json"))
        if not paths: self.error(PAGES, "", "no pages found")
        for path in paths:
            relative = path.relative_to(PAGES)
            if len(relative.parts) != 2: self.error(path, "", "must use pages/<feature>/<screen>.page.json"); continue
            directory, filename = relative.parts[0], path.name.removesuffix(".page.json")
            if not KEBAB.fullmatch(directory): self.error(path, "", "feature directory must be kebab-case")
            if not KEBAB.fullmatch(filename): self.error(path, "", "screen filename must be kebab-case")
            doc = self.load(path)
            if not doc: continue
            value = self.object(doc, "page")
            if value is None: continue
            self.schema_ref(value, path, "../../schemas/page.schema.json")
            feature = value.get("feature")
            if not isinstance(feature, dict): self.error(path, "$.feature", "must be an object")
            else:
                key, label = feature.get("key"), feature.get("label")
                if key != directory: self.error(path, "$.feature.key", f"must match {directory!r}")
                if not isinstance(label, str) or not label.strip(): self.error(path, "$.feature.label", "must be non-empty")
                elif isinstance(key, str):
                    if key in self.features and self.features[key] != label: self.error(path, "$.feature.label", "inconsistent label")
                    if label in self.feature_labels and self.feature_labels[label] != key: self.error(path, "$.feature.label", "label belongs to another feature")
                    self.features[key] = label; self.feature_labels[label] = key
            page = value.get("page")
            if not isinstance(page, str) or not NAME.fullmatch(page): self.error(path, "$.page", "must use PascalCase")
            elif page in self.pages: self.error(path, "$.page", f"duplicate page {page!r}")
            else: self.pages[page] = doc
            if not isinstance(value.get("frame"), dict): self.error(path, "$.frame", "must be an object")
            if not isinstance(value.get("layout"), dict): self.error(path, "$.layout", "must be an object")
            children = value.get("children")
            if not isinstance(children, list): self.error(path, "$.children", "must be an array")
            else:
                for index, child in enumerate(children): self.validate_node(child, path, f"$.children[{index}]")
            self.validate_requirements(value.get("requirements"), path)
            self.token_refs(value, path)

    def validate_value(self, value: Any, expected: str, path: Path, location: str, owner: str | None) -> None:
        if isinstance(value, dict) and set(value) == {"bind"}:
            binding = value.get("bind")
            if not owner: self.error(path, location, "bindings are only allowed in custom composition")
            elif not isinstance(binding, str) or binding not in self.custom_components[owner].value.get("props", {}): self.error(path, location, f"unknown binding {binding!r}")
            elif self.custom_components[owner].value["props"][binding].get("type") != expected: self.error(path, location, f"binding {binding!r} must have type {expected}")
            return
        checks = {"string": lambda x: isinstance(x, str), "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool), "boolean": lambda x: isinstance(x, bool), "array": lambda x: isinstance(x, list), "object": lambda x: isinstance(x, dict)}
        if expected in checks and not checks[expected](value): self.error(path, location, f"must be {expected}")

    def validate_node(self, node: Any, path: Path, location: str, owner: str | None = None, deps: set[str] | None = None) -> None:
        if not isinstance(node, dict): self.error(path, location, "node must be an object"); return
        kind = node.get("type")
        if isinstance(node.get("design"), dict) and "colorTreatment" in node["design"] and kind != "library-component":
            self.error(path, f"{location}.design.colorTreatment", "is only allowed on registered library controls")
        if kind == "component": self.error(path, f"{location}.type", "legacy type is ambiguous; use library-component or custom-component"); return
        if kind not in NODE_TYPES: self.error(path, f"{location}.type", f"unsupported node type {kind!r}"); return
        if "hideWhenEmpty" in node:
            if kind != "text": self.error(path, f"{location}.hideWhenEmpty", "is only allowed on text nodes")
            if not isinstance(node["hideWhenEmpty"], bool): self.error(path, f"{location}.hideWhenEmpty", "must be boolean")
        if "penpotEmptyPlaceholder" in node:
            if kind != "text" or node.get("hideWhenEmpty") is not True or node["penpotEmptyPlaceholder"] != " ":
                self.error(path, f"{location}.penpotEmptyPlaceholder", "requires text, hideWhenEmpty true, and exactly one ASCII space")
        if kind in STRUCTURAL or kind == "text":
            if not isinstance(node.get("name"), str) or not NAME.fullmatch(node["name"]): self.error(path, f"{location}.name", "must use PascalCase")
        if kind == "text": self.validate_value(node.get("value"), "string", path, f"{location}.value", owner)
        if kind == "library-component":
            self.library_refs += 1
            library, component = node.get("library"), node.get("component")
            definition = self.library_components.get((library, component))
            if definition is None: self.error(path, f"{location}.component", f"unknown library component {library}.{component}")
            else:
                declared, props = definition.get("props", {}), node.get("props", {})
                if not isinstance(props, dict): self.error(path, f"{location}.props", "must be an object"); props = {}
                for prop, prop_value in props.items():
                    if prop not in declared: self.error(path, f"{location}.props.{prop}", f"{library}.{component} does not declare this prop"); continue
                    spec = declared[prop]; self.validate_value(prop_value, spec.get("type"), path, f"{location}.props.{prop}", owner)
                    if spec.get("enum") and not isinstance(prop_value, dict) and prop_value not in spec["enum"]: self.error(path, f"{location}.props.{prop}", f"must be one of {spec['enum']}")
                for prop, spec in declared.items():
                    if spec.get("required") and prop not in props: self.error(path, f"{location}.props", f"missing required prop {prop!r}")
                slots = node.get("slots", {})
                if not isinstance(slots, dict): self.error(path, f"{location}.slots", "must be an object"); slots = {}
                allowed = set(definition.get("slots", []))
                for slot, children in slots.items():
                    if slot not in allowed: self.error(path, f"{location}.slots.{slot}", f"unknown slot for {library}.{component}")
                    if not isinstance(children, list): self.error(path, f"{location}.slots.{slot}", "must be an array")
                    else:
                        for index, child in enumerate(children): self.validate_node(child, path, f"{location}.slots.{slot}[{index}]", owner, deps)
                design = node.get("design", {})
                if isinstance(design, dict):
                    template = definition.get("penpotTemplate", {})
                    if design.get("appearance") not in (None, *template.get("appearances", [])): self.error(path, f"{location}.design.appearance", "unsupported representative appearance")
                    if design.get("state") not in (None, *template.get("states", [])): self.error(path, f"{location}.design.state", "unsupported representative state")
                    for key in ("variant", "size"):
                        allowed_values = template.get(f"{key}s", [])
                        if allowed_values and design.get(key) is None: self.error(path, f"{location}.design.{key}", f"is required for {library}.{component}")
                        elif design.get(key) not in (None, *allowed_values): self.error(path, f"{location}.design.{key}", f"unsupported representative {key}")
                    if "colorTreatment" in design and design["colorTreatment"] not in template.get("colorTreatments", []):
                        self.error(path, f"{location}.design.colorTreatment", "unsupported representative color treatment")
                    if component == "Button":
                        visual_variant = design.get("variant")
                        runtime_variant = props.get("variant")
                        if visual_variant == "filled" and runtime_variant is not None: self.error(path, f"{location}.props.variant", "filled Button must omit the runtime variant prop")
                        elif visual_variant in {"outlined", "text", "link"} and runtime_variant != visual_variant: self.error(path, f"{location}.props.variant", f"must match design.variant {visual_variant!r}")
                        if "severity" not in props: self.error(path, f"{location}.props.severity", "Button severity must be explicit")
                        if "icon" in props and "iconPos" not in props: self.error(path, f"{location}.props.iconPos", "Button icon position must be explicit")
                    if component in {"InputText", "Textarea"}:
                        if props.get("variant") != design.get("variant"): self.error(path, f"{location}.props.variant", "must match design.variant")
                        if "fluid" not in props: self.error(path, f"{location}.props.fluid", f"{component} fluid width behavior must be explicit")
                    state = design.get("state")
                    if state == "disabled" and props.get("disabled") is not True: self.error(path, f"{location}.props.disabled", "must be true for disabled design state")
                    if state == "loading" and component == "Button" and props.get("loading") is not True: self.error(path, f"{location}.props.loading", "must be true for loading design state")
                    if component == "Button":
                        if props.get("loading") is True and state != "loading": self.error(path, f"{location}.design.state", "must be loading when loading is true")
                        elif props.get("disabled") is True and props.get("loading") is not True and state != "disabled": self.error(path, f"{location}.design.state", "must be disabled when disabled is true without loading")
                        if owner and (not isinstance(props.get("disabled"), bool) or not isinstance(props.get("loading"), bool)): self.error(path, f"{location}.props", "custom state Buttons require literal disabled and loading booleans")
                else: self.error(path, f"{location}.design", "must be an object")
        elif kind == "custom-component":
            self.custom_refs += 1
            component, variant = node.get("component"), node.get("variant")
            doc = self.custom_components.get(component)
            if doc is None: self.error(path, f"{location}.component", f"unknown custom component {component!r}")
            else:
                definition = doc.value
                if variant not in definition.get("variants", {}): self.error(path, f"{location}.variant", f"unknown variant {component}.{variant}")
                declared, props = definition.get("props", {}), node.get("props", {})
                if not isinstance(props, dict): self.error(path, f"{location}.props", "must be an object"); props = {}
                for prop, prop_value in props.items():
                    if prop not in declared: self.error(path, f"{location}.props.{prop}", f"{component} does not declare this prop")
                    else: self.validate_value(prop_value, declared[prop].get("type"), path, f"{location}.props.{prop}", owner)
                for prop, spec in declared.items():
                    if spec.get("required") and prop not in props: self.error(path, f"{location}.props", f"missing required prop {prop!r}")
                if deps is not None and isinstance(component, str): deps.add(component)
        if "action" in node:
            if isinstance(node["action"], dict) and node["action"].get("type") == "owner-action":
                if not owner or kind != "library-component" or node.get("component") != "Button" or set(node["action"]) != {"type"}:
                    self.error(path, f"{location}.action", "owner-action requires a nested custom composition Button and no other fields")
            else:
                self.validate_action(node["action"], path, f"{location}.action")
        if kind == "custom-component" and doc is not None and variant in doc.value.get("variants", {}):
            def delegates(item):
                if isinstance(item, dict):
                    return item.get("action") == {"type": "owner-action"} or any(delegates(v) for v in item.values())
                return isinstance(item, list) and any(delegates(v) for v in item)
            if delegates(doc.value["variants"][variant]["composition"]) and "action" not in node:
                self.error(path, f"{location}.action", "custom instance with owner-action Button requires a concrete action")
        children = node.get("children")
        if children is not None:
            if not isinstance(children, list): self.error(path, f"{location}.children", "must be an array")
            else:
                for index, child in enumerate(children): self.validate_node(child, path, f"{location}.children[{index}]", owner, deps)

    def validate_action(self, action: Any, path: Path, location: str) -> None:
        if not isinstance(action, dict): self.error(path, location, "must be an object"); return
        required = {"navigate": "target", "submit": "name", "command": "name", "external-link": "url"}
        kind = action.get("type")
        if kind not in required: self.error(path, f"{location}.type", "unsupported action type"); return
        key = required[kind]
        if not isinstance(action.get(key), str) or not action[key]: self.error(path, f"{location}.{key}", "must be non-empty")

    def validate_requirements(self, requirements: Any, path: Path) -> None:
        if requirements is None: return
        if not isinstance(requirements, dict): self.error(path, "$.requirements", "must be an object"); return
        sources = requirements.get("sources")
        if not isinstance(sources, list) or not sources: self.error(path, "$.requirements.sources", "must be non-empty")
        else:
            for index, source in enumerate(sources):
                loc = f"$.requirements.sources[{index}]"
                if not isinstance(source, str) or not any(candidate.is_file() for candidate in (ROOT / source, WORKSPACE / source)): self.error(path, loc, f"requirement source does not exist: {source}")
        assumptions = requirements.get("approvedAssumptions")
        if not isinstance(assumptions, list) or not all(isinstance(item, str) and item.strip() for item in assumptions): self.error(path, "$.requirements.approvedAssumptions", "must be a string array")

    def validate_penpot(self) -> None:
        doc = self.load(PENPOT)
        if not doc: return
        value = self.object(doc, "Penpot config")
        if value is None: return
        for key in ("server", "projectName", "generatedFileName", "featurePagePrefix", "pageFramePrefix", "pageComponentRepresentation", "renderStrategy"):
            if not isinstance(value.get(key), str) or not value[key]: self.error(doc.path, f"$.{key}", "must be non-empty")
        library, custom = value.get("libraryComponents"), value.get("customComponents")
        if not isinstance(library, dict) or library.get("representation") != "native" or library.get("fidelity") != "representative": self.error(doc.path, "$.libraryComponents", "must be native with representative fidelity")
        if not isinstance(custom, dict) or custom.get("representation") != "native" or custom.get("variantProperty") != "State": self.error(doc.path, "$.customComponents", "must be native with State variants")
        if isinstance(custom, dict): self.validate_structural_card_shells(custom.get("structuralCardShells", []), doc.path)
        if isinstance(library, dict) and isinstance(custom, dict):
            if library.get("pageName") == custom.get("pageName"): self.error(doc.path, "$", "library and custom pages must differ")
            if library.get("componentPrefix") == custom.get("componentPrefix"): self.error(doc.path, "$", "library and custom prefixes must differ")
        self.validate_page_structural_card_shells(value.get("pageStructuralCardShells", []), doc.path)
        self.validate_page_structural_shells(value.get("pageStructuralShells", []), doc.path)
        if value.get("pageComponentRepresentation") != "instance": self.error(doc.path, "$.pageComponentRepresentation", "must be 'instance'")
        if value.get("renderStrategy") != "replace-by-name": self.error(doc.path, "$.renderStrategy", "must be 'replace-by-name'")

    def validate_page_structural_shells(self, entries: Any, path: Path) -> None:
        location = "$.pageStructuralShells"
        if not isinstance(entries, list):
            self.error(path, location, "must be an array of scoped shell policies"); return
        seen = set()
        for index, entry in enumerate(entries):
            loc = f"{location}[{index}]"
            if not isinstance(entry, dict) or set(entry) != {"page", "library", "component"} or not all(isinstance(v, str) and v for v in entry.values()):
                self.error(path, loc, "requires exactly non-empty page, library, and component strings"); continue
            key = (entry["page"], entry["library"], entry["component"])
            if key in seen: self.error(path, loc, "duplicate scoped shell policy")
            seen.add(key)
            page = self.pages.get(entry["page"])
            if not page: self.error(path, loc, f"unknown page {entry['page']!r}")
            contract = self.library_components.get(key[1:])
            if not contract:
                self.error(path, loc, "unknown library component"); continue
            if not contract.get("slots"):
                self.error(path, loc, "structural shells require a slot-bearing component")
            def contains(nodes):
                for node in nodes:
                    if node.get("type") == "library-component" and (node.get("library"), node.get("component")) == key[1:]: return True
                    if contains(node.get("children", [])): return True
                    if any(contains(children) for children in node.get("slots", {}).values()): return True
                return False
            if page and not contains(page.value.get("children", [])):
                self.error(path, loc, "page does not reference the scoped library component")

    def validate_page_structural_card_shells(self, names: Any, path: Path) -> None:
        location = "$.pageStructuralCardShells"
        if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
            self.error(path, location, "must be an array of page names"); return
        if len(names) != len(set(names)): self.error(path, location, "must contain unique page names")
        for name in names:
            if name not in self.pages: self.error(path, location, f"unknown page {name!r}")

    def validate_structural_card_shells(self, names: Any, path: Path) -> None:
        location = "$.customComponents.structuralCardShells"
        if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
            self.error(path, location, "must be an array of custom family names"); return
        if len(names) != len(set(names)): self.error(path, location, "must contain unique family names")
        for name in names:
            doc = self.custom_components.get(name)
            if not doc: self.error(path, location, f"unknown custom family {name!r}"); continue
            for state, variant in doc.value.get("variants", {}).items():
                tree = variant.get("composition", {}) if isinstance(variant, dict) else {}
                if tree.get("type") != "library-component" or tree.get("library") != "primevue" or tree.get("component") != "Card":
                    self.error(path, location, f"{name}.{state} must have a PrimeVue Card root")

    def unrecognized_json(self) -> None:
        recognized = {TOKENS, PENPOT, *SCHEMA_FILES}
        recognized.update(LIBRARIES.glob("*.library.json")); recognized.update(COMPONENTS.glob("*.component.json")); recognized.update(PAGES.rglob("*.page.json"))
        for path in sorted(DESIGN.rglob("*.json")):
            if path not in recognized: self.error(path, "", "JSON file is outside a supported design location")

    def run(self) -> int:
        self.validate_tokens(); self.validate_schemas(); self.validate_libraries(); self.validate_custom_components(); self.validate_pages(); self.validate_penpot(); self.unrecognized_json()
        if self.errors:
            print(f"Design validation failed with {len(self.errors)} error(s):")
            for error in self.errors: print(f"- {error}")
            return 1
        print(f"Design validation passed: {len(self.libraries)} component library, {len(self.library_components)} registered library components, {len(self.custom_components)} custom components, {len(self.pages)} pages, {self.library_refs} library references and {self.custom_refs} custom references; props, slots, actions, bindings, variants, tokens, requirements, schemas, and Penpot config are valid.")
        return 0

if __name__ == "__main__": sys.exit(Validator().run())