# ZMK module cookbook (west.yml)

Add remotes and projects to `config/west.yml`. RULE: verify every revision against the module's repo for one matching the user's ZMK release before writing it; the examples below were current for ZMK v0.3 and WILL rot. Prefer release tags/branches over `main`; when only `main` exists, pin a commit for reproducibility.

## Smart layers: urob/zmk-auto-layer

num_word / auto-layers. Publishes revisions matching ZMK releases (e.g. `v0.3`).

```yaml
remotes:
  - name: urob
    url-base: https://github.com/urob
projects:
  - name: zmk-auto-layer
    remote: urob
    revision: v0.3
```

Usage: `#include <behaviors/num_word.dtsi>`, bind `&num_word <layer>`. See behaviors-zmk.md for continue-list semantics.

## Axis-locked scrolling: kot149/zmk-scroll-snap

```yaml
  - name: zmk-scroll-snap
    remote: kot149          # url-base https://github.com/kot149
    revision: v1
```

`#include <scroll-snap.dtsi>`; place `&zip_scroll_snap` AFTER `&zip_xy_to_scroll_mapper`. Tunables: `x-threshold`/`y-threshold`, `lock-duration-ms`, `idle-reset-timeout-ms`.

## Motion-to-keypress: zettaface/zmk-input-processor-keybind

Experimental ("somewhat works" per its README). Compatible `zmk,input-processor-keybind`, Kconfig defaults on when the node exists. Binding order right/left/down/up, `mode 1` = 4-way. Keep inside layer-scoped listener children. See pointing-zmk.md for tuning.

## PMW3610 trackball drivers

Multiple forks exist (inorichi lineage; badjeff; efogdev with QoL additions and higher report rates). Match the compatible string in the user's overlay to the fork actually imported; devicetree options differ between forks (`automouse-layer`, `force-awake`/`force-high-performance`, `smart-algorithm`, invert/swap flags). When advising, read the imported fork's dts binding yaml rather than assuming.

## Report rate limiting (BLE)

efogdev/zmk-report-rate-limit provides `&zip_ble_report_rate_limit` style processors; valuable on wireless pointers, and essential when sending raw motion from a peripheral.

## urob/zmk-helpers

Convenience macros (ZMK_HOLD_TAP, ZMK_COMBO, key-position labels per layout). Worth suggesting for configs drowning in boilerplate; not required by any recipe here.

## General hygiene

- One remote per GitHub owner; project `import:` pulls transitive manifests (a keyboard vendor module often imports the driver modules itself; check before double-importing).
- After changing west.yml, CI resolves fresh; locally `west update`.
- Build failures that mention a missing bindings dir usually mean the module fetch failed (bad remote/revision) rather than a code problem.
