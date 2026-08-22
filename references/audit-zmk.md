# ZMK config audit checklist

Read every file first: `config/*.keymap`, `config/*.conf`, `build.yaml`, `config/west.yml`, shield overlays under `config/boards/shields/`, and any imported module manifests. Then work through the checks. Report findings ranked by expected payoff with a concrete failure scenario each.

## Deliverable shape

1. Setup overview: hardware, firmware chain (which modules import which), pointing devices and their processing paths.
2. Per-layer binding tables using the derived position grid (print the grid; combos reference these numbers).
3. Combo map and behavior inventory.
4. Findings, ranked. Each: what, why it bites, the fix, which half to reflash.
5. Suggested order of work, each step independently flashable.

## Behavior checks

- **Untuned hold-taps**: `&mt`/`&lt` on defaults (hold-preferred-ish, 200 ms, no positional awareness) under home row mods = misfires during fast rolls. Fix: timeless HRM recipe (see behaviors-zmk.md).
- **Conflicting shift systems**: autoshift + HRM shift + caps_word coexisting means inconsistent capitals. Flag which keys use which system; recommend consolidation, but respect deliberate hybrids (autoshift users often keep Shift for selection only, which changes GACS ordering advice).
- **Mod order vs platform**: GACS is the default reference, but on macOS Cmd belongs on the index fingers; on Windows/Linux Ctrl does. Ask or infer the platform before recommending mod moves (tables in os-and-locale.md). Multi-OS users: check for the BT-profile-plus-OS-layer pattern.
- **Key repeat lost**: `quick-tap-ms = <0>` on a hold-tap kills hold-to-repeat. Suggest ~150-200 unless intentional.
- **`&to` lock round trips**: locking layers with `&to N` then `&to 0` invites stuck-layer mistakes. Consider layer-taps, smart layers (num_word), or tap-dance hybrids that preserve the lock as double-tap.
- **Thumb holds that fire on long presses**: `&mt X SPACE` emits X on any slow space. Only flag if X is not a deliberate feature (users bind dictation/PTT here on purpose; ask).

## Structure checks

- **Raw layer indices everywhere**: automouse targets, tap-dance params, listener children, `&to`/`&lt` args. Recommend `#define` layer names once; every future layer insertion depends on it.
- **Missing display-names**: layers show as `layer_5` in ZMK Studio and diagrams.
- **Duplicate/dead overlay files**: identical overlays in two shield dirs, or nodes defined but disabled (e.g. OLED with `CONFIG_ZMK_DISPLAY=n`). One copy, or delete.
- **Unpinned module revisions**: `revision: main` in west.yml breaks reproducibility. Pin to a tag/commit; match helper-module revisions to the ZMK release (e.g. zmk-auto-layer `v0.3` for ZMK `v0.3`).
- **Empty placeholder layers**: transparent layers that exist "for later" still appear in Studio and shift nothing; fine, but name them.

## System layer checks (almost always incomplete)

The system/settings layer should carry, reachable even one-handed:

- `&bootloader` on BOTH halves (each acts on the half whose key is pressed) so flashing needs no physical button
- `&sys_reset` on both halves
- `&soft_off` (with `hold-time-ms`, e.g. 2000) for travel: full power-down, wake only by reset-button tap, needs `CONFIG_ZMK_PM_SOFT_OFF=y`. Central forwards to peripheral.
- `&out OUT_TOG` (needs `#include <dt-bindings/zmk/outputs.h>`), full BT profile coverage (`BT_SEL 0-4`, `BT_CLR`, consider `BT_DISC`)
- build.yaml should include a `settings_reset` shield target for pairing recovery

## Includes check

Every keycode family needs its header: `&bt` needs `dt-bindings/zmk/bt.h`, `&out` needs `outputs.h`, pointing needs `pointing.h`, RGB needs `rgb.h`. A missing include surfaces as a devicetree "expected number or parenthesized expression" parse error at the first use.

## Input devices present?

Encoders: check per-layer `sensor-bindings` (bound only on base = wasted). Displays: defined-but-disabled nodes, widget config. If the board has pointing devices (ball/trackpad/trackpoint), additionally run the checks in pointing-zmk.md and devices-zmk.md: where processing happens (peripheral vs central), layer-awareness, automouse vs temp-layer, timer refresh sources.

## Locale check

Host set to a non-US layout while the keymap uses US keycode names: works, but keymap and diagrams lie. Recommend joelspadin locale headers (os-and-locale.md). Autoshift/mod-morph shifted pairs assume US pairing; re-derive for the host layout.

## Power checks

`force-awake` sensors, `CONFIG_BT_CTLR_TX_PWR_PLUS_8`, enabled displays: all deliberate battery trades. Flag for awareness, not removal; recommend measuring before changing.
