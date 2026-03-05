from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_lint_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "lint_template_components.py"
    spec = importlib.util.spec_from_file_location("lint_template_components", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Ensure decorators/dataclasses can resolve module metadata during exec.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_tmpl009_flags_component_svg_not_allowlisted(tmp_path, monkeypatch):
    lint = _load_lint_module()

    component_file = tmp_path / "services" / "portal" / "templates" / "components" / "example.html"
    component_file.parent.mkdir(parents=True, exist_ok=True)
    component_file.write_text("<div><svg><path d='M0 0'></path></svg></div>", encoding="utf-8")

    allowlist = tmp_path / ".component-svg-allowlist"
    allowlist.write_text("", encoding="utf-8")

    monkeypatch.setattr(lint, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lint, "PORTAL_TEMPLATES", tmp_path / "services" / "portal" / "templates")
    monkeypatch.setattr(lint, "COMPONENT_DIR", tmp_path / "services" / "portal" / "templates" / "components")
    monkeypatch.setattr(lint, "COMPONENT_SVG_ALLOWLIST_FILE", allowlist)
    lint.load_component_svg_allowlist.cache_clear()

    violations = lint.scan_file(component_file)
    assert any(v.code == "TMPL009" for v in violations)


def test_tmpl009_skips_allowlisted_component_svg(tmp_path, monkeypatch):
    lint = _load_lint_module()

    component_file = tmp_path / "services" / "portal" / "templates" / "components" / "spinner.html"
    component_file.parent.mkdir(parents=True, exist_ok=True)
    component_file.write_text("<span><svg><circle></circle></svg></span>", encoding="utf-8")

    allowlist = tmp_path / ".component-svg-allowlist"
    allowlist.write_text(
        "services/portal/templates/components/spinner.html | animated loading spinner\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(lint, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(lint, "PORTAL_TEMPLATES", tmp_path / "services" / "portal" / "templates")
    monkeypatch.setattr(lint, "COMPONENT_DIR", tmp_path / "services" / "portal" / "templates" / "components")
    monkeypatch.setattr(lint, "COMPONENT_SVG_ALLOWLIST_FILE", allowlist)
    lint.load_component_svg_allowlist.cache_clear()

    violations = lint.scan_file(component_file)
    assert not any(v.code == "TMPL009" for v in violations)
