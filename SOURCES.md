# Third-party notices & sources

This project (MIT-licensed CSS + scripts) is an **unofficial** Claude-inspired theme
add-on for the VSCode extension [`cweijan.vscode-office`]. It is **not affiliated with,
endorsed by, or sponsored by Anthropic**. "Claude" is used only descriptively, to name
the visual style the theme emulates.

## Host extension

- [`cweijan.vscode-office`](https://github.com/cweijan/vscode-office) (Office Viewer) —
  the extension this theme plugs into. Its code is **not** redistributed here; the build
  script overlays onto your own installed copy.

## Fonts (NOT bundled in this repo)

This repo ships **no font files**. For the exact Claude typography you may supply them
yourself (see README → "Exact Claude fonts"):

| Font | License | Notes |
| :-- | :-- | :-- |
| Anthropic Serif / Sans Web Text, Anthropic Mono Variable | **Proprietary — © Anthropic PBC** | NOT redistributed here. Optional; supply your own. |
| Noto Serif SC | SIL Open Font License 1.1 | CJK serif. Optional; from Google Fonts. |

> The Anthropic fonts are proprietary to Anthropic PBC and are intentionally **not**
> included or redistributed by this repository. Without them the theme falls back to an
> open/system serif (Georgia / Noto Serif SC / Songti SC), which still looks close.

## Palette & font-scheme reference

- [Tsumugii24/claude-typora-theme](https://github.com/Tsumugii24/claude-typora-theme) —
  the Claude-for-Typora theme this project drew its palette and serif font scheme from.
