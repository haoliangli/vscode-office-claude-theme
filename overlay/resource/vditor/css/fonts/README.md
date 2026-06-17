# fonts/ (optional, not committed)

This folder is where the build picks up **optional** fonts for the exact Claude look.
Font files are git-ignored — none ship with the repo.

The theme works without them (it falls back to Georgia / Noto Serif SC / Songti SC).
For the exact Claude typography, drop these files here (or let `build.sh` find them via
`FONT_SRC` — see the top-level README):

- `AnthropicSerifWebText.ttf`  — Latin serif (proprietary, © Anthropic PBC)
- `AnthropicSansWebText.ttf`   — Latin sans (proprietary, © Anthropic PBC)
- `AnthropicMonoVariable.ttf`  — mono / code (proprietary, © Anthropic PBC)
- `NotoSerifSC-VariableFont_wght.ttf` — CJK serif (SIL OFL, from Google Fonts)

See `SOURCES.md` for licensing. The Anthropic fonts are proprietary and are **not**
distributed with this project — supply your own copies.
