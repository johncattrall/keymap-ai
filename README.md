<p align="center">
  <img src="assets/banner.svg" alt="keymap-ai" width="800"/>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"/></a>
  <img src="https://img.shields.io/badge/ZMK-stable-2ea44f" alt="ZMK: stable"/>
  <img src="https://img.shields.io/badge/QMK-beta-orange" alt="QMK: beta"/>
  <img src="https://img.shields.io/badge/Agent%20Skills-portable-8a2be2" alt="Agent Skills standard"/>
</p>

An [Agent Skill](https://agentskills.io) that turns your coding agent into a custom-keyboard firmware expert. Audit your ZMK or QMK config, tune home row mods that never misfire, make trackballs and trackpads layer-aware, wire your window manager to ball flicks, localize for your language and OS, generate per-layer keymap diagrams with CI, and debug the failures the docs don't cover.

Works with Claude Code, Codex CLI, Cursor, Gemini CLI, opencode, and any other harness supporting the Agent Skills standard.

## Install

```bash
npx skills add johncattrall/keymap-ai
```

That detects your installed agents (Claude Code, Codex, Cursor, Gemini CLI, opencode, ...) and adds the skill to each.

Codex users can alternatively install it as a skill-only plugin:

```
codex plugin marketplace add johncattrall/keymap-ai
```

or from inside Codex: `$skill-installer install https://github.com/johncattrall/keymap-ai/tree/main/skills/keymap-ai`

Manual fallback: copy `skills/keymap-ai/` into your agent's skills directory (e.g. `~/.claude/skills/` or `~/.agents/skills/`).

## A real before and after

These are not mockups. The "before" is the actual first commit of a real Crosses config; the "after" is the same keyboard today, evolved through this skill's audit-and-apply loop in a single day. Both images are drawn by the skill's own pipeline.

<img src="assets/before.svg" alt="Initial commit: hold-for-shift on every key, locked layers, each trackball hardwired to one role" width="100%"/>

*Before: the initial commit. Hold-any-key-for-shift at 200 ms, lower/raise layer locks, one trackball permanently a pointer and the other permanently scroll.*

<img src="assets/after.svg" alt="Today: tuned home row mods, combos, smart numpad thumb, auto mouse layer with mod-clicks, and both balls layer-aware" width="100%"/>

*After: timeless home row mods, combos for momentary layers, a smart NumWord thumb (tap for numbers, auto-exits), an auto-raised mouse layer with mirrored clicks and mod-click home row, a full numpad layer, and both trackballs layer-aware: snapped scroll and pointer on base, precision mode on Mouse, window throw/resize gestures on the pad layer.*

Getting there is conversational: **"audit my config"** produces layer tables, a combo map, and findings ranked by payoff, each with a failure scenario, the fix, and which half to reflash; then apply them one reversible commit at a time.

## How it routes

```mermaid
flowchart LR
    U(("you")) --> S["keymap-ai<br/>SKILL.md"]
    S --> A["Audit<br/><i>review my config</i>"]
    S --> P["Pointing<br/><i>trackball / trackpad / encoder</i>"]
    S --> D["Draw<br/><i>diagrams + CI</i>"]
    S --> L["Layout<br/><i>Graphite, Colemak-DH...</i>"]
    S --> O["Platform<br/><i>multi-OS, locale, WM</i>"]
    S --> B["Debug<br/><i>build errors, pitfalls</i>"]
    A --> R[("references/<br/>10 files, field-verified")]
    P --> R
    D --> R
    L --> R
    O --> R
    B --> R
```

Everything is intent-routed from natural language; no commands to memorize. The skill reads your actual config before advising, states its assumptions, and verifies version-sensitive claims against live docs instead of asserting from memory.

## Coverage

| Area | What's inside |
|---|---|
| Boards | Splits, unibody, dongle topologies; 30-key minimalists to 60+; advice calibrated to key count |
| Behaviors | Timeless home row mods, smart layers (numword), caps word, tap-dance hybrids, mod-morphs, autoshift trade-offs, travel soft-off |
| Pointing | Trackballs, Cirque trackpads, PS/2 trackpoints: per-layer processing, scroll with axis snapping, precision modes, motion-to-keypress gestures |
| Other hardware | Rotary encoders (per-layer bindings), OLED/nice!view displays, RGB, status widgets |
| Platform | macOS/Windows/Linux modifier conventions, multi-OS profile+layer switching, window manager tables (Amethyst, Rectangle, AeroSpace, yabai, i3/sway, Hyprland, komorebi), dictation-collision checks, per-half battery levels on the host |
| International | Locale keycode headers (zmk-locale-generator), unicode input per OS, dead-key gotchas, non-US shifted pairs |
| Layouts | Any published layout: curated guidance for Colemak-DH, Graphite, Gallium, Canary, Dvorak, plus spec-driven generation for Workman, Sturdy, Focal, Engram, Hands Down, Semimak, APT and others |
| Tooling | keymap-drawer diagrams (per-layer, dark-mode aware, trackballs drawn in place), GitHub Actions integration, README generation |
| Debugging | Build-error playbooks plus a 21-entry field-verified pitfall database |

## Support tiers

| Firmware | Tier | Meaning |
|---|---|---|
| ZMK | **Stable** | Recipes hardware-verified on wireless splits with pointing devices |
| QMK | **Beta** | Audit, behaviors, layouts, diagrams; compile-verified, not yet hardware-tested. Pointing recipes deferred |

QMK users: everything the skill generates can be validated with `qmk compile` before flashing. If you test QMK advice on hardware, open an issue with the result; that is exactly how the QMK tier graduates to stable.

## What's inside

```
.codex-plugin/plugin.json   Codex skill-only plugin manifest
skills/keymap-ai/
  SKILL.md                  intent routing: audit / apply / pointing / draw / layout / platform / debug
  references/
    audit-zmk.md              the audit checklist (behaviors, structure, system layer, locale, power)
    audit-qmk.md              the QMK equivalent (beta)
    behaviors-zmk.md          timeless HRM, smart layers, mod-morphs, soft off
    behaviors-qmk.md          tap-hold tuning, Caps Word, key overrides (beta)
    pointing-zmk.md           per-layer motion processing: listener semantics, gestures
    devices-zmk.md            trackpads, trackpoints, encoders, displays, dongles, RGB
    os-and-locale.md          multi-OS patterns, window managers, international layouts
    modules-zmk.md            west.yml cookbook for community modules
    layouts.md                alt-layout guidance and generation
    diagrams.md               keymap-drawer + CI + README conventions
    pitfalls.md             21 field-verified failure modes with fixes
    debug.md                build-error and hardware-symptom playbooks
  scripts/
    draw_zmk.py             deterministic parse/augment/draw pipeline
```

## Why this exists

The hardest knowledge in custom keyboard firmware lives in folklore: hold-tap tuning that actually works, input-listener child-node ordering, smart-layer continue-list rules, which module fork has which devicetree options, why your mouse layer captures input. This skill encodes that folklore, sourced from real hardware debugging, so the next person doesn't pay for it in evenings.

## Contributing

Contributions are very welcome, especially: pitfalls you hit (symptom, cause, fix), QMK hardware test reports, locale and layout corrections, module cookbook updates when revisions move, and device recipes for hardware we haven't covered (encoder-heavy boards, dongles, trackpoint builds). See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

Standing on the shoulders of the community: [ZMK](https://zmk.dev), [QMK](https://qmk.fm), [urob](https://github.com/urob) (timeless HRM, zmk-auto-layer), [caksoylar](https://github.com/caksoylar/keymap-drawer) (keymap-drawer), [joelspadin](https://github.com/joelspadin/zmk-locale-generator) (locale tooling), [getreuer](https://getreuer.info/posts/keyboards/) (QMK userspace patterns), [infused-kim](https://github.com/infused-kim/kb_zmk_ps2_mouse_trackpoint_driver) (trackpoint driver), [itouuuuuuuuu](https://github.com/itouuuuuuuuu/zmk-battery-bar) and [carlosedp](https://github.com/carlosedp/zmk-split-battery) (per-half battery apps for macOS and Windows), and the module authors credited in `references/modules-zmk.md`.

## License

[MIT](LICENSE)
