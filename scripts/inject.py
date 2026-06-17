#!/usr/bin/env python3
"""Inject the Claude themes into a copied cweijan.vscode-office build dir.

Two edits, both idempotent:
  1. package.json -> contributes.configuration.properties["vscode-office.editorTheme"].enum
     gets "Claude" and "Claude Dark" appended (if absent).
  2. resource/vditor/css/base.css -> add Claude / Claude Dark to the light / dark
     `.vditor-outline` brightness groups (purely cosmetic, keeps the outline panel
     filter consistent with the rest of the themes).

Usage: python3 inject.py <build_dir>
"""
import base64
import json
import sys
from pathlib import Path

THEMES = ["Claude", "Claude Dark"]

FONT_MARKER = "/* claude-fonts (injected) */"
# Small Anthropic fonts -> inlined as base64 data-URIs so they always load in the
# webview (no path/CSP dependency). Noto Serif SC is 25MB -> referenced by url().
DATA_FONTS = [
    ("Anthropic Serif Web Text", "AnthropicSerifWebText.ttf"),
    ("Anthropic Sans Web Text", "AnthropicSansWebText.ttf"),
    ("Anthropic Mono Variable", "AnthropicMonoVariable.ttf"),
]
URL_FONTS = [
    ("Noto Serif SC", "NotoSerifSC-VariableFont_wght.ttf"),
]


def patch_package_json(pkg: Path) -> None:
    data = json.loads(pkg.read_text(encoding="utf-8"))
    # `contributes.configuration` may be a single object or a list of sections.
    config = data["contributes"]["configuration"]
    sections = config if isinstance(config, list) else [config]
    enum = None
    for section in sections:
        props = section.get("properties", {})
        if "vscode-office.editorTheme" in props:
            enum = props["vscode-office.editorTheme"]["enum"]
            break
    if enum is None:
        sys.exit("vscode-office.editorTheme property not found in package.json")
    for name in THEMES:
        if name not in enum:
            enum.append(name)
    # We repackage the already-compiled `out/`, so drop the prepublish hook
    # (it runs `yarn build`, which we neither need nor have a toolchain for).
    scripts = data.get("scripts")
    if isinstance(scripts, dict):
        scripts.pop("vscode:prepublish", None)
    # Match upstream's tab indentation; keep non-ASCII intact; trailing newline.
    pkg.write_text(json.dumps(data, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  package.json enum -> {enum}")


def patch_fonts(css: Path, fonts: Path) -> None:
    """Append @font-face rules to base.css so the Claude fonts load reliably.

    Anthropic fonts are embedded as base64 data-URIs (zero path/CSP risk);
    Noto Serif SC (CJK, ~25MB) is referenced by url() relative to base.css.
    Idempotent via FONT_MARKER.
    """
    text = css.read_text(encoding="utf-8")
    if FONT_MARKER in text:
        print("  base.css fonts already injected")
        return
    blocks = [FONT_MARKER]
    for family, fname in DATA_FONTS:
        f = fonts / fname
        if not f.is_file():
            # Anthropic fonts are optional/proprietary (not shipped). Skip the
            # @font-face; the CSS font stack falls back to an open/system serif.
            print(f"  note: {fname} absent — skipped (fallback serif)")
            continue
        b64 = base64.b64encode(f.read_bytes()).decode("ascii")
        blocks.append(
            f'@font-face{{font-family:"{family}";'
            f'src:url("data:font/ttf;base64,{b64}") format("truetype");'
            f"font-weight:100 900;font-display:swap;}}"
        )
    for family, fname in URL_FONTS:
        if (fonts / fname).is_file():
            blocks.append(
                f'@font-face{{font-family:"{family}";'
                f'src:url("fonts/{fname}") format("truetype");'
                f"font-weight:100 900;font-display:swap;}}"
            )
        else:
            print(f"  note: {fname} absent — CJK will fall back to Songti SC")
    css.write_text(text + "\n" + "\n".join(blocks) + "\n", encoding="utf-8")
    print(f"  base.css @font-face injected ({len(blocks) - 1} face(s))")


def patch_extension_js(js: Path) -> None:
    """Add Claude themes to the hardcoded quick-pick list in the compiled JS.

    The Settings-UI dropdown reads package.json's enum, but the in-editor
    "Select Editor Theme" quick-pick is built from a hardcoded array in
    out/extension.js. Selecting from that quick-pick is also what live-applies
    the theme, so this patch is required for the theme to actually switch.
    """
    text = js.read_text(encoding="utf-8")
    target = '"Nord","Monokai","Dracula"]'
    addition = '"Nord","Monokai","Dracula","|","Claude","Claude Dark"]'
    if addition in text:
        print("  extension.js already patched")
        return
    count = text.count(target)
    if count != 1:
        sys.exit(f"extension.js: expected exactly 1 theme-array match, found {count}")
    text = text.replace(target, addition, 1)
    js.write_text(text, encoding="utf-8")
    print("  extension.js quick-pick theme list patched")


def patch_base_css(css: Path) -> None:
    text = css.read_text(encoding="utf-8")
    sel = '#vditor[data-editor-theme="{}"] .vditor-content .vditor-outline,\n'
    # Light group: insert Claude right after the "Warm Light" line.
    light_anchor = sel.format("Warm Light")
    if sel.format("Claude") not in text and light_anchor in text:
        text = text.replace(light_anchor, light_anchor + sel.format("Claude"), 1)
    # Dark group: insert Claude Dark right after the "Dracula" line.
    dark_anchor = sel.format("Dracula")
    if sel.format("Claude Dark") not in text and dark_anchor in text:
        text = text.replace(dark_anchor, dark_anchor + sel.format("Claude Dark"), 1)
    css.write_text(text, encoding="utf-8")
    print("  base.css outline groups patched")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python3 inject.py <build_dir>")
    build = Path(sys.argv[1])
    pkg = build / "package.json"
    css = build / "resource" / "vditor" / "css" / "base.css"
    js = build / "out" / "extension.js"
    fonts = build / "resource" / "vditor" / "css" / "fonts"
    for p in (pkg, css, js):
        if not p.is_file():
            sys.exit(f"file not found: {p}")
    patch_package_json(pkg)
    patch_base_css(css)
    patch_fonts(css, fonts)
    patch_extension_js(js)
    print("inject.py: done")


if __name__ == "__main__":
    main()
