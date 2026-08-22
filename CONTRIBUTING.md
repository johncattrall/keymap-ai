# Contributing to keymap-ai

Thanks for helping. This project's value is verified knowledge, so the bar for content is "known true", not "sounds right".

## What we want most

1. **Pitfalls**: a failure you actually hit. Add to `references/pitfalls.md` as symptom, cause, fix, in that order, one entry, numbered. Include the firmware version if version-sensitive.
2. **QMK hardware test reports**: run a beta-tier recipe on real hardware and open an issue titled `qmk-test: <recipe>` with the board, QMK version, and result. Confirmed recipes move to the stable tier.
3. **Module cookbook updates**: revisions rot. PRs to `references/modules-zmk.md` when a module publishes a new release-matched revision, changes options, or is archived.
4. **Layout specs**: corrections to `references/layouts.md`, especially custom shift-pair tables, with a link to the layout's official spec.
5. **New references**: encoder recipes, dongle/multi-peripheral setups, per-board quirks. Open an issue first to agree scope.

## Ground rules for content

- Verified over plausible: state HOW a claim was verified (hardware test, source reading, compile check, official docs). Unverified but useful content is welcome when labeled as such.
- Version-sensitive claims name the version they were checked against.
- Recipes are minimal and reversible; no personal-keymap opinions baked in as universal advice (platform-dependent guidance, like modifier ordering, must say what it depends on).
- Keep references token-lean: the skill loads these files into an agent's context. Prefer one sharp example over three redundant ones.

## Style

- Plain Markdown, no HTML. Code blocks tagged (`dts`, `c`, `yaml`, `bash`).
- SKILL.md stays portable: frontmatter is `name` and `description` only, no harness-specific fields.
- Scripts are plain Python 3 stdlib + pyyaml, runnable without the skill.

## Testing a change

- Skill format: `npx skills-ref validate .`
- Scripts: run `scripts/draw_zmk.py` against any public zmk-config with an info.json layout.
- README assets: regenerate with the skill's own pipeline from `assets/demo/` (real ZMK keymaps, drawn by `scripts/draw_zmk.py` with the demo config and trackball label files); assets must never be hand-drawn.
- Content: the acceptance bar for audit-checklist changes is that an agent using the skill on a real config finds true things and no false things.

## Process

Small PRs merge fastest. For anything structural (new intents, tier changes, QMK pointing), open an issue first. By contributing you agree your contribution is MIT licensed.
