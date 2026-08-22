# ZMK input devices beyond trackballs

The central fact: EVERY pointing device in ZMK (trackball, trackpad, trackpoint) feeds the same input-listener architecture, so all of pointing-zmk.md's semantics (peripheral vs central processing, child-node ordering, temp-layer activation, per-layer processors) apply unchanged. This file covers device-specific setup; pointing-zmk.md covers what to do with the motion.

## Cirque Pinnacle trackpads (Glidepoint)

Common on Sweeps, Ferris variants, and DIY thumb-pad builds. Modules: the Pinnacle input driver exists in several maintained forks (e.g. te9no/zmk-module-cirque-trackpad; petejohanson's cirque-input-module lineage). Check which fork is current for the user's ZMK release before writing west.yml; devicetree options differ (SPI vs I2C wiring, `dr-gpios`, sensitivity, absolute vs relative mode).

- Relative mode behaves exactly like a trackball: all listener recipes apply.
- Tap-to-click and gestures: prefer handling taps as `&mkp` on a mouse layer raised by `&zip_temp_layer`; driver-level tap detection varies by fork.
- Scroll: same `zip_xy_to_scroll_mapper` chain; trackpads benefit even more from axis snapping and lower scroll scalers than balls do.
- Circular scroll / absolute-mode features are fork-specific: read the fork's binding YAML, do not assume.

## PS/2 trackpoint (ThinkPad-style)

infused-kim/kb_zmk_ps2_mouse_trackpoint_driver is the established module (with an example zmk-config repo). Realities to set expectations on:

- PS/2 needs specific wiring (clock/data lines, often UART-assisted) and a reset circuit on some modules; this is a hardware-integration project, not a config tweak.
- Trackpoints drift and need calibration options (`sampling-rate`, sensitivity, negative inertia); the driver exposes trackpoint-specific settings; read its README rather than reciting.
- Once events flow, everything downstream is standard: listeners, layers, temp-layer mouse activation.

## Rotary encoders (core ZMK)

No module needed. Two parts:

1. Hardware: `sensors` node with `alps,ec11` (or compatible) and `triggers-per-rotation`.
2. Keymap: `sensor-bindings` per layer: `sensor-bindings = <&inc_dec_kp C_VOL_UP C_VOL_DN>;`

Per-layer sensor-bindings are the encoder analog of per-layer pointer processing: volume on base, scroll (`&inc_dec_kp PG_UP PG_DN` or mouse wheel via `&inc_dec_msc SCRL_UP SCRL_DOWN`) on nav, zoom/undo-redo chords on an edit layer. Audit check: encoders bound only on layer 0 are wasted potential; encoders with no `sensor-bindings` on some layer fall through per the transparent rules.

## Displays

- OLED (SSD1306) and nice!view (sharp memory LCD) are core-supported; `CONFIG_ZMK_DISPLAY=y` plus the right shield/overlay node. nice!view wants `CONFIG_ZMK_WIDGET_*` choices and costs less battery than OLED.
- Audit checks: display node defined but display disabled (dead weight, confusion); widget set unconfigured; battery/BT status widgets are the ones users actually want.
- Community widget modules exist (e.g. caksoylar's rgbled-widget for status via a single LED on displayless boards; useful for BT profile feedback).

## Dongle setups

Three-unit topologies (two halves + a dongle as central) trade keyboard battery life for an always-powered central and lower latency to the host. Implications the skill must respect:

- The DONGLE is central: all listener/keymap processing runs there; both keyboard halves are peripherals sending raw events; per-layer pointing works the same but "which unit to flash" answers change (keymap changes = dongle).
- Peripheral count and split config come from the shield/board definition; audit the `west.yml`/shield source rather than assuming two units.
- Battery reporting for multiple peripherals needs `CONFIG_ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_FETCHING`-family options; check the release's docs.

## RGB underglow / backlight

Core support (`CONFIG_ZMK_RGB_UNDERGLOW`, `&rgb_ug` behaviors, needs `dt-bindings/zmk/rgb.h`). Audit angle: wireless boards pay real battery for RGB; check for an off-by-default state and an accessible toggle, and `CONFIG_ZMK_RGB_UNDERGLOW_AUTO_OFF_IDLE`/`_USB` options.

## Key wells and exotic layouts

Dactyl-likes, Glove80, and unibody boards change nothing about firmware semantics; only the physical layout file (for diagrams) and position numbering differ. Always regenerate the position grid from the board's actual layout before writing positional config (combos, hold-trigger positions).
