# QMK config audit checklist (beta tier)

Status: compile-verified guidance, not hardware-tested by the maintainers. Label high-stakes advice accordingly and verify version-sensitive claims against docs.qmk.fm. Validate every generated change with `qmk compile -kb <keyboard> -km <keymap>`; it needs no hardware.

Read first: `keymap.c` (or `keymap.json`), `config.h`, `rules.mk`, and any userspace directory. Deliverable shape matches the ZMK audit: layer tables, findings ranked by payoff, order of work.

## Behavior checks

- **Untuned tap-hold**: mod-taps/layer-taps on default `TAPPING_TERM` (200) with no mode flags misfire under home row mods. The modern baseline: per-key `TAPPING_TERM` where needed, `PERMISSIVE_HOLD` or `HOLD_ON_OTHER_KEY_PRESS` chosen deliberately (know the difference before recommending), and getreuer's **Achordion/**chordal-hold-style same-hand suppression as the QMK analog of ZMK's positional hold triggers. QMK core has grown chordal-hold options in recent versions: check docs.qmk.fm for the current native option before recommending the userspace library.
- **Caps Word** (`CAPS_WORD_ENABLE`) for CONSTANTS instead of shift gymnastics.
- **Auto Shift** trade-offs mirror ZMK autoshift: capitals wait out the timeout; interacts with tap-hold keys.
- **One Shot Mods** for Callum-style setups; check `ONESHOT_TIMEOUT`.
- **Layer access**: `MO`/`LT`/`TG`/`DF` mix; flag `TG` locks with no visible state and no easy exit; `DF` without persistence surprises after power-off.

## Structure checks

- Layer enum names vs magic numbers in `keymap.c`; `layer_names` for tooling.
- `rules.mk` feature bloat vs firmware size (older AVR boards hit flash limits: `LTO_ENABLE`, disable unused features like mousekeys/console when not needed).
- Combos, tap dance, key overrides: inventory and check terms/timeouts.
- Userspace (`users/<name>`) shared across boards: flag copy-paste drift between keymaps instead.

## System/utility checks

- `QK_BOOT` reachable on every board (both halves for splits) so flashing needs no physical reset.
- `EE_CLR` (EEPROM clear) reachable or documented for settings recovery.
- Split-specific: handedness setting (`SPLIT_HAND_PIN` / EEPROM handedness), `SPLIT_USB_DETECT` on boards that need it.

## Pointing devices (deferred)

QMK pointing-device recipes are not yet in this skill's verified tier. For trackball boards (Charybdis, Ploopy-alikes): point at docs.qmk.fm Pointing Device docs and the board vendor's reference keymap; do not improvise processing chains from ZMK knowledge, the architectures differ.

## Diagrams

keymap-drawer supports QMK natively: `qmk c2json` then `keymap parse -q`, or parse via/`keymap.json` directly with `-c`. The rest of the diagrams reference applies unchanged.
