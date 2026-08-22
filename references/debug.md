# Debugging playbooks

Check `references/pitfalls.md` first; most field issues are catalogued there. This file covers the diagnostic method.

## Build failures (ZMK / GitHub Actions)

Read the FIRST error, not the CMake cascade after it.

- `devicetree error: <file>:<line> (column <n>): parse error: expected number or parenthesized expression` - an undefined token at that exact spot; almost always a missing `#include <dt-bindings/zmk/...>` for a keycode family, or a typoed keycode/behavior param.
- `undefined node label` - referencing `&node` that no imported overlay defines: wrong module revision, missing module, or the label lives in a shield you are not building.
- Missing bindings directory in the gen_defines invocation - a module failed to fetch: check west.yml remote/revision spelling and that the revision exists.
- Kconfig warnings about unknown symbols - the module providing that Kconfig is not in the build, or the option name changed between releases.
- Works locally, fails in CI (or vice versa) - west manifest drift; pin revisions.

Reproduce cheaply: push to a branch, or local `west build` in a zmk workspace with `-DZMK_CONFIG` / `-DZMK_EXTRA_MODULES` pointing at the repo. For QMK: `qmk compile -kb <kb> -km <km>` validates without hardware.

## "The keyboard does the wrong thing"

Interrogate before theorizing; these four questions localize most problems:

1. Which half was flashed, with which artifact, from which CI run? (Stale halves are the top cause of "the fix did nothing", and peripheral-processing changes require both halves.)
2. Has ZMK Studio ever been used to change anything? (Persisted state shadows keymap edits; Restore Stock Settings or settings_reset firmware clears it.)
3. Exactly which layer was active, and how was it entered? (Multiple layers can be active; tap-dance entry has resolution latency; temp-layers have tails.)
4. Which device produced the input, and what did the OTHER device do? (Splits process per-side; listener children select per active layer.)

Then map the symptom to the processing path: sensor node → split node (peripheral) → BLE → listener base/children (central) → HID. Every stage has a distinct failure signature: direction flips are sensor-node config; layer-blindness is peripheral-side processing; wrong-override selection is child order; ghost layer activity is timer refresh sources.

## Bluetooth and split-link issues

Order of escalation: reselect profile (`BT_SEL`), disconnect+repair the profile (`BT_DISC`, forget on host, `BT_CLR` on keyboard), settings_reset firmware on BOTH halves then re-pair halves to each other first, host second. Signal issues on hosts with weak BT: `CONFIG_BT_CTLR_TX_PWR_PLUS_8=y`, consider `CONFIG_BT_CTLR_PHY_2M=n` for compatibility. Split halves pair to each other at first boot after settings reset; flashing both halves fresh and powering them together re-establishes it.

## Battery drain

Suspects in order: display enabled, `force-awake`/high-performance sensor flags, BT TX power boost, short idle-sleep timeout disabled, debug logging left on (`CONFIG_ZMK_USB_LOGGING`). Measure one change at a time; days-long feedback loops punish shotgun changes.
