#!/usr/bin/env python3
"""Validate the repository's JSON-first UI design specifications."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "design"
TOKENS_FILE = DESIGN_DIR / "tokens" / "tokens.json"
COMPONENTS_DIR = DESIGN_DIR / "components"
PAGES_DIR = DESIGN_DIR / "pages"
PENPOT_FILE = DESIGN_DIR / "penpot.json"
WORKSPACE_ROOT = ROOT.parent

TOKEN_REFERENCE = re.compile(r"^(color|spacing|radius|font)\.[A-Za-z0-9_.-]+$")
NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")
SUPPORTED_NODE_TYPES = {
    "component",
    "column",
    "grid",
    "row",
    "section",
    "text",
}


@dataclass(frozen=True)
class LoadedJson:
    path: Path
    value: Any


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.tokens: dict[str, Any] = {}
        self.components: dict[str, LoadedJson] = {}
        self.pages: dict[str, LoadedJson] = {}

    def error(self, path: Path, location: str, message: str) -> None:
        relative = path.relative_to(ROOT)
        suffix = f" at {location}" if location else ""
        self.errors.append(f"{relative}{suffix}: {message}")

    def load_json(self, path: Path) -> LoadedJson | None:
        if not path.is_file():
            self.error(path, "", "required file does not exist")
            return None
        try:
            with path.open(encoding="utf-8") as source:
                return LoadedJson(path, json.load(source))
        except json.JSONDecodeError as exc:
            self.error(path, f"line {exc.lineno}, column {exc.colno}", exc.msg)
        except OSError as exc:
            self.error(path, "", str(exc))
        return None

    def require_object(self, document: LoadedJson, kind: str) -> dict[str, Any] | None:
        if not isinstance(document.value, dict):
            self.error(document.path, "$", f"{kind} must be a JSON object")
            return None
        return document.value

    def token_exists(self, reference: str) -> bool:
        current: Any = self.tokens
        for segment in reference.split("."):
            if not isinstance(current, dict) or segment not in current:
                return False
            current = current[segment]
        return not isinstance(current, (dict, list))

    def validate_token_references(self, value: Any, path: Path, location: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                self.validate_token_references(child, path, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self.validate_token_references(child, path, f"{location}[{index}]")
        elif isinstance(value, str) and TOKEN_REFERENCE.fullmatch(value):
            if not self.token_exists(value):
                self.error(path, location, f"unknown token reference {value!r}")

    def validate_tokens(self) -> None:
        document = self.load_json(TOKENS_FILE)
        if document is None:
            return
        value = self.require_object(document, "token document")
        if value is None:
            return
        self.tokens = value
        for namespace in ("color", "spacing", "radius", "font"):
            if namespace not in value:
                self.error(document.path, "$", f"missing token namespace {namespace!r}")
            elif not isinstance(value[namespace], dict):
                self.error(document.path, f"$.{namespace}", "token namespace must be an object")
        self.validate_token_leaves(value, document.path)

    def validate_token_leaves(self, value: Any, path: Path, location: str = "$") -> None:
        if isinstance(value, dict):
            if not value:
                self.error(path, location, "token group must not be empty")
            for key, child in value.items():
                if not isinstance(key, str) or not key:
                    self.error(path, location, "token names must be non-empty strings")
                self.validate_token_leaves(child, path, f"{location}.{key}")
        elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
            return
        else:
            self.error(path, location, "token value must be a string or number")

    def validate_components(self) -> None:
        paths = sorted(COMPONENTS_DIR.glob("*.components.json"))
        if not paths:
            self.error(COMPONENTS_DIR, "", "no component specifications found")
        for path in paths:
            document = self.load_json(path)
            if document is None:
                continue
            value = self.require_object(document, "component specification")
            if value is None:
                continue
            name = value.get("name")
            if not isinstance(name, str) or not NAME.fullmatch(name):
                self.error(path, "$.name", "must be a non-empty PascalCase name")
                continue
            if name in self.components:
                original = self.components[name].path.relative_to(ROOT)
                self.error(path, "$.name", f"duplicate component {name!r}; first declared in {original}")
                continue
            self.components[name] = document
            variants = value.get("variants")
            if not isinstance(variants, dict) or not variants:
                self.error(path, "$.variants", "must be a non-empty object")
            else:
                for variant, definition in variants.items():
                    if not isinstance(variant, str) or not variant:
                        self.error(path, "$.variants", "variant names must be non-empty strings")
                    if not isinstance(definition, dict):
                        self.error(path, f"$.variants.{variant}", "variant must be an object")
            layers = value.get("layers")
            if not isinstance(layers, list) or not layers or not all(
                isinstance(layer, str) and layer for layer in layers
            ):
                self.error(path, "$.layers", "must be a non-empty array of layer names")
            elif len(layers) != len(set(layers)):
                self.error(path, "$.layers", "contains duplicate layer names")
            self.validate_token_references(value, path)

    def validate_pages(self) -> None:
        paths = sorted(PAGES_DIR.glob("*.page.json"))
        if not paths:
            self.error(PAGES_DIR, "", "no page specifications found")
        for path in paths:
            document = self.load_json(path)
            if document is None:
                continue
            value = self.require_object(document, "page specification")
            if value is None:
                continue
            name = value.get("page")
            if not isinstance(name, str) or not NAME.fullmatch(name):
                self.error(path, "$.page", "must be a non-empty PascalCase name")
                continue
            if name in self.pages:
                original = self.pages[name].path.relative_to(ROOT)
                self.error(path, "$.page", f"duplicate page {name!r}; first declared in {original}")
                continue
            self.pages[name] = document
            frame = value.get("frame")
            if not isinstance(frame, dict):
                self.error(path, "$.frame", "must be an object")
            elif not isinstance(frame.get("width"), (int, float)) or isinstance(frame.get("width"), bool) or frame["width"] <= 0:
                self.error(path, "$.frame.width", "must be a positive number")
            layout = value.get("layout")
            if not isinstance(layout, dict):
                self.error(path, "$.layout", "must be an object")
            children = value.get("children")
            if not isinstance(children, list):
                self.error(path, "$.children", "must be an array")
            else:
                for index, child in enumerate(children):
                    self.validate_node(child, path, f"$.children[{index}]")
            self.validate_requirements(value.get("requirements"), path)
            self.validate_token_references(value, path)

    def validate_node(self, node: Any, path: Path, location: str) -> None:
        if not isinstance(node, dict):
            self.error(path, location, "node must be an object")
            return
        node_type = node.get("type")
        if node_type not in SUPPORTED_NODE_TYPES:
            self.error(path, f"{location}.type", f"unsupported node type {node_type!r}")
            return
        if node_type == "component":
            component = node.get("component")
            variant = node.get("variant")
            if component not in self.components:
                self.error(path, f"{location}.component", f"unknown component {component!r}")
            else:
                component_value = self.components[component].value
                variants = component_value.get("variants", {})
                if variant not in variants:
                    self.error(
                        path,
                        f"{location}.variant",
                        f"unknown variant {component}.{variant}",
                    )
        children = node.get("children")
        if children is not None:
            if not isinstance(children, list):
                self.error(path, f"{location}.children", "must be an array")
            else:
                for index, child in enumerate(children):
                    self.validate_node(child, path, f"{location}.children[{index}]")

    def validate_requirements(self, requirements: Any, path: Path) -> None:
        if requirements is None:
            return
        if not isinstance(requirements, dict):
            self.error(path, "$.requirements", "must be an object")
            return
        sources = requirements.get("sources")
        if not isinstance(sources, list) or not sources:
            self.error(path, "$.requirements.sources", "must be a non-empty array")
        else:
            for index, source in enumerate(sources):
                location = f"$.requirements.sources[{index}]"
                if not isinstance(source, str) or not source:
                    self.error(path, location, "must be a non-empty path string")
                    continue
                candidates = (ROOT / source, WORKSPACE_ROOT / source)
                if not any(candidate.is_file() for candidate in candidates):
                    self.error(path, location, f"requirement source does not exist: {source}")
        assumptions = requirements.get("approvedAssumptions")
        if not isinstance(assumptions, list) or not all(
            isinstance(item, str) and item.strip() for item in assumptions
        ):
            self.error(
                path,
                "$.requirements.approvedAssumptions",
                "must be an array of non-empty strings",
            )

    def validate_penpot(self) -> None:
        document = self.load_json(PENPOT_FILE)
        if document is None:
            return
        value = self.require_object(document, "Penpot configuration")
        if value is None:
            return
        for key in (
            "server",
            "projectName",
            "generatedFileName",
            "componentsPageName",
            "pageFramePrefix",
            "componentPrefix",
            "renderStrategy",
        ):
            if not isinstance(value.get(key), str) or not value[key].strip():
                self.error(document.path, f"$.{key}", "must be a non-empty string")
        if value.get("renderStrategy") not in {"replace-by-name"}:
            self.error(document.path, "$.renderStrategy", "unsupported render strategy")
        if value.get("pageFramePrefix") == value.get("componentPrefix"):
            self.error(document.path, "$", "page and component prefixes must differ")

    def find_unrecognized_json(self) -> None:
        recognized = {TOKENS_FILE, PENPOT_FILE}
        recognized.update(COMPONENTS_DIR.glob("*.components.json"))
        recognized.update(PAGES_DIR.glob("*.page.json"))
        for path in sorted(DESIGN_DIR.rglob("*.json")):
            if path not in recognized:
                self.error(path, "", "JSON file is outside a supported design location")

    def run(self) -> int:
        self.validate_tokens()
        self.validate_components()
        self.validate_pages()
        self.validate_penpot()
        self.find_unrecognized_json()
        if self.errors:
            print(f"Design validation failed with {len(self.errors)} error(s):")
            for message in self.errors:
                print(f"- {message}")
            return 1
        print(
            "Design validation passed: "
            f"{len(self.components)} component(s), {len(self.pages)} page(s), "
            "token references, component variants, requirements, and Penpot config are valid."
        )
        return 0


def main() -> int:
    return Validator().run()


if __name__ == "__main__":
    sys.exit(main())