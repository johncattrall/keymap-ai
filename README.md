# keymap-ai

An [Agent Skill](https://agentskills.io) that turns your coding agent into a custom-keyboard firmware expert. Audit your ZMK or QMK config, tune home row mods that never misfire, make trackballs layer-aware, generate per-layer keymap diagrams with CI, and debug the failures the docs don't cover.

Works with Claude Code, Codex CLI, Cursor, Gemini CLI, opencode, and any other harness supporting the Agent Skills standard.

## Install

```bash
npx skills add johncattrall/keymap-ai
```

That detects your installed agents and adds the skill to each. Or copy this repo into your agent's skills directory manually (e.g. `~/.claude/skills/keymap-ai` or `~/.agents/skills/keymap-ai`).

## What it does

Talk to your agent naturally inside your keymap repo:

| You say | It does |
|---|---|
| "Audit my zmk config" | Full review: layer tables, combo map, findings ranked by payoff, each with a failure scenario, a fix, and which half to reflash |
| "Fix my home row mods" | Timeless hold-tap tuning (balanced flavor, positional triggers, prior-idle) with position defines generated for your board |
| "Make the left trackball scroll, but act as a precision pointer on the mouse layer" | Per-layer input processing done correctly: raw motion to the central listener, child-node ordering rules, shared temp-layer timers |
| "Set up keymap diagrams" | keymap-drawer config, per-layer SVGs (trackballs and encoders drawn in place with per-layer roles), dark-mode-aware, CI job that keeps them current |
| "Add a Graphite toggle layer" | Alt layout generated at the correct layer index, indices converted to defines, mods carried over positionally, mod-morphs for custom shift pairs |
| "My build failed" / "the mouse layer captures my inputs" | Playbooks plus a field-verified pitfall database covering the failures that cost real debugging hours |

## Support tiers

| Firmware | Tier | Meaning |
|---|---|---|
| ZMK | Stable | Recipes hardware-verified on wireless splits with pointing devices |
| QMK | Beta | Audit, behaviors, layouts, and diagrams; compile-verified, not yet hardware-tested. Pointing-device recipes deferred |

QMK users: everything the skill generates can be validated with `qmk compile` before flashing. If you test QMK advice on hardware, open an issue with the result, that is exactly how the QMK tier graduates to stable.

## What's inside

```
SKILL.md                    intent routing: audit / apply / pointing / draw / layout / debug
references/
  audit-zmk.md              the audit checklist (behaviors, structure, system layer, includes, power)
  audit-qmk.md              the QMK equivalent (beta)
  behaviors-zmk.md          timeless HRM, smart layers, mod-morphs, soft off
  behaviors-qmk.md          tap-hold tuning, Caps Word, key overrides (beta)
  pointing-zmk.md           trackballs: listener semantics, per-layer processing, gestures
  modules-zmk.md            west.yml cookbook for community modules
  layouts.md                alt-layout guidance and generation (Graphite, Colemak-DH, Canary)
  diagrams.md               keymap-drawer + CI + README conventions
  pitfalls.md               16 field-verified failure modes with fixes
  debug.md                  build-error and hardware-symptom playbooks
scripts/
  draw_zmk.py               deterministic parse/augment/draw pipeline
```

The skill's core principle: read the user's actual config before advising, state assumptions, prefer small reversible commits, and verify version-sensitive claims against the live docs rather than asserting from memory.

## Why this exists

ZMK's hardest knowledge lives in folklore: hold-tap tuning that actually works, input-listener child-node semantics, smart-layer continue-list rules, which module fork has which devicetree options. This skill encodes that folklore, sourced from real hardware debugging, so the next person doesn't pay for it in evenings.

## Contributing

Contributions are very welcome, especially: pitfalls you hit with symptom/cause/fix, QMK hardware test reports, module cookbook updates when revisions move, and layout spec corrections. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

Standing on the shoulders of the community: [ZMK](https://zmk.dev), [QMK](https://qmk.fm), [urob](https://github.com/urob) (timeless HRM, zmk-auto-layer), [caksoylar](https://github.com/caksoylar/keymap-drawer) (keymap-drawer), [getreuer](https://getreuer.info/posts/keyboards/) (QMK userspace patterns), and the module authors credited in `references/modules-zmk.md`.

## License

[MIT](LICENSE)
