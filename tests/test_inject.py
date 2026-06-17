#!/usr/bin/env python3
"""Smoke test for scripts/inject.py.

Builds a minimal synthetic copy of the bits inject.py patches, runs the
injector against it, and asserts every patch landed — then runs it a second
time to prove idempotency. No real extension or fonts required.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INJECT = REPO / "scripts" / "inject.py"

PKG = {
    "contributes": {
        "configuration": [
            {"properties": {"vscode-office.editorTheme": {"enum": ["Auto", "Light", "Warm Light", "Dracula"]}}}
        ]
    },
    "scripts": {"vscode:prepublish": "yarn build", "test": "echo ok"},
}

# base.css must carry the anchors inject.py inserts after.
BASE_CSS = (
    '#vditor[data-editor-theme="Warm Light"] .vditor-content .vditor-outline,\n'
    'body[data-vscode-theme-kind="vscode-light"] #vditor[data-editor-theme="Auto"] .vditor-content .vditor-outline {\n'
    "    filter: brightness(99%);\n}\n"
    '#vditor[data-editor-theme="Dracula"] .vditor-content .vditor-outline,\n'
    'body[data-vscode-theme-kind="vscode-dark"] #vditor[data-editor-theme="Auto"] .vditor-content .vditor-outline {\n'
    "    filter: brightness(110%);\n}\n"
)

EXT_JS = 'var g=["Auto","Light","Solarized","Warm Light","Dim Light","One Dark","Github Dark","Nord","Monokai","Dracula"];'


def build_fixture(root: Path) -> None:
    (root / "out").mkdir(parents=True)
    (root / "resource/vditor/css").mkdir(parents=True)
    (root / "package.json").write_text(json.dumps(PKG), encoding="utf-8")
    (root / "resource/vditor/css/base.css").write_text(BASE_CSS, encoding="utf-8")
    (root / "out/extension.js").write_text(EXT_JS, encoding="utf-8")


def run_inject(root: Path) -> None:
    subprocess.run([sys.executable, str(INJECT), str(root)], check=True)


def check(root: Path) -> None:
    pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
    enum = pkg["contributes"]["configuration"][0]["properties"]["vscode-office.editorTheme"]["enum"]
    assert "Claude" in enum and "Claude Dark" in enum, f"enum not patched: {enum}"
    assert "vscode:prepublish" not in pkg.get("scripts", {}), "prepublish not removed"

    ext = (root / "out/extension.js").read_text(encoding="utf-8")
    assert '"Nord","Monokai","Dracula","|","Claude","Claude Dark"]' in ext, "extension.js quick-pick not patched"

    css = (root / "resource/vditor/css/base.css").read_text(encoding="utf-8")
    assert "claude-fonts (injected)" in css, "font marker missing"
    assert '#vditor[data-editor-theme="Claude"] .vditor-content .vditor-outline,' in css, "light outline not patched"
    assert '#vditor[data-editor-theme="Claude Dark"] .vditor-content .vditor-outline,' in css, "dark outline not patched"


def main() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "build"
        build_fixture(root)
        run_inject(root)
        check(root)
        # idempotent: a second run must not crash or double-apply
        run_inject(root)
        check(root)
        ext = (root / "out/extension.js").read_text(encoding="utf-8")
        assert ext.count('"|","Claude","Claude Dark"]') == 1, "extension.js double-patched"
    print("inject.py smoke test: PASS")


if __name__ == "__main__":
    main()
