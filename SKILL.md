---
name: keymap-ai
description: Expert assistant for ZMK and QMK keyboard firmware configs. Use when auditing or improving a zmk-config or QMK keymap, tuning home row mods or hold-taps, adding smart layers (numword, caps word), configuring trackballs/pointing devices and per-layer input processors, generating keymap-drawer diagrams and CI, adding alternate layouts (Graphite, Colemak-DH, Canary), debugging firmware build errors or layer capture issues, or when the user mentions keymaps, layers, combos, tapping term, split keyboards, or keyboard firmware.
---

# keymap-ai

Expert knowledge for custom keyboard firmware: ZMK (stable tier, hardware-verified) and QMK (beta tier). Route on the user's intent, load only the references that intent needs, and always ground claims in the user's actual config files rather than assumptions.

## First steps, always

1. Locate the config: a zmk-config repo (`config/*.keymap`, `build.yaml`, `config/west.yml`) or a QMK keymap (`keymap.c` / `keymap.json`, `config.h`, `rules.mk`). Read the keymap fully before advising.
2. Identify the hardware: split or unibody, key count, pointing devices, encoders, displays, wireless or wired. For ZMK splits, determine which half is central (check `Kconfig.defconfig` or build.yaml snippets).
3. Note the firmware version: ZMK release from `west.yml` (e.g. `v0.3`), QMK from the repo. Verify version-sensitive advice against the docs for THAT version (zmk.dev / docs.qmk.fm) instead of asserting from memory.
4. Never guess layer numbers or key positions. Derive the position grid from the physical layout and state it in the response.

## Intents

### Audit ("audit my config", "review my keymap")

Load `references/audit-zmk.md` (or `references/audit-qmk.md`). Produce: a per-layer table of bindings, a combo map, a behavior inventory, then findings ranked by expected payoff, each with a concrete failure scenario and fix. End with a suggested order of work where every step is independently flashable. Deliver as a report the user can keep.

### Apply ("implement recommendation N", "fix my home row mods")

Load `references/behaviors-zmk.md` or `references/behaviors-qmk.md` for the recipe. Make one reversible change at a time. State which half (or halves) must be reflashed. After editing, re-check every hardcoded layer index the change may have shifted.

### Pointing ("trackball", "scroll", "per-layer mouse behavior")

ZMK: load `references/pointing-zmk.md`. This is the least documented area of ZMK and the file encodes hardware-verified semantics; follow it exactly, especially listener child-node ordering rules. QMK pointing is deferred in this version: say so, offer general QMK docs guidance, and verify everything against docs.qmk.fm.

### Draw ("diagrams", "visualize my keymap", "README images")

Load `references/diagrams.md`. Use keymap-drawer; set up per-layer SVGs, virtual keys for trackballs/encoders, dark-mode-aware transparent styling, and the CI job that keeps images current.

### Layout ("add Graphite", "try Colemak-DH", "which layout should I learn")

Load `references/layouts.md`. Give honest switching-cost guidance before generating anything. For generation: insert the alpha layer BELOW all function layers, convert raw layer indices to #defines in the same change, carry mods and behaviors over positionally, and use mod-morphs for layouts with custom shift pairs.

### Debug ("build failed", "keys do the wrong thing", "layer won't deactivate")

Load `references/debug.md` and `references/pitfalls.md`. Match symptoms against the pitfall database first; most field problems are already catalogued there.

## Tier honesty

ZMK content is hardware-verified. QMK content is compile-verified but not hardware-tested; label QMK advice as such when stakes are high, and prefer pointing users at `qmk compile` to validate changes cheaply. Never present untested pointing-device recipes as proven.

## Style

State assumptions explicitly. Prefer small reversible commits over big rewrites. When a recommendation is withdrawn by user context (platform, workflow, physical constraints), record why rather than silently dropping it. Keyboards are personal: audit findings are options with reasoning, not mandates.
