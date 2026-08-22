# ZMK pointing: per-layer motion processing and gestures

Applies to ANY relative pointing device: trackball, Cirque trackpad, trackpoint (device-specific setup lives in devices-zmk.md). Hardware-verified on a dual-PMW3610 wireless split (nice!nano v2, ZMK v0.3). The listener semantics below were confirmed against `app/src/pointing/input_listener.c`; they are the difference between working and mysteriously broken.

## Where processing runs (the key architectural fact)

- Processors on an **input-split child node** (`zmk,input-split`) run on the PERIPHERAL before transmission. They cannot be layer-aware; the peripheral does not track layers usefully for this.
- Processors on an **input-listener** run on the CENTRAL and support per-layer child nodes.

Therefore: for any per-layer behavior on a peripheral-side device, send raw motion (keep only rate limiting on the split node) and interpret on the central listener:

```dts
&trackball_peripheral_split {
    input-processors = <&zip_ble_report_rate_limit>;
};
```

Cost: raw x/y over BLE instead of processed events; a report-rate-limit processor keeps traffic sane.

## Listener child-node semantics (memorize these)

From ZMK source, v0.3:

1. Children are evaluated in DECLARATION ORDER; the first child whose `layers` list contains ANY currently-active layer wins, runs its chain, and (without `process-next;`) evaluation STOPS. Base processors are only the fallback when no child matched.
2. **Layer 0 is always active.** A child with `0` in its layers list matches on EVERY layer and shadows every child declared after it. Never put layer 0 in a child; make that behavior the base chain instead.
3. Multiple layers are often active simultaneously (momentary holds, temp-layer tails). Declaration order is therefore PRIORITY order: put the most specific/override layers first.

Canonical shape:

```dts
&trackball_peripheral_listener {
    status = "okay";
    // base = default for any layer without an override below
    input-processors = <&zip_xy_to_scroll_mapper>, <&zip_scroll_snap>, <&zip_scroll_scaler 1 2>;

    win_gestures {                 // declared first: must beat the mouse layer
        layers = <5>;
        input-processors = <&zip_win_throw>, <&zip_xy_scaler 0 1>;
    };
    precision_pointer {
        layers = <4>;
        input-processors = <&zip_xy_scaler 3 4>, <&zip_temp_layer 4 800>;
    };
};
```

## Mouse layer activation: temp-layer beats driver automouse

Driver-level automouse (`automouse-layer` on the sensor node) refreshes its timer only from THAT sensor. With two pointing devices, the layer times out while the other device is in active use. Fix: remove the driver property and use core `&zip_temp_layer <layer> <timeout-ms>` referenced from BOTH devices' chains; a shared node instance means either device refreshes the same timer.

Temp-layer details: any key press ends it unless the position is in `excluded-positions`; exclude the mouse layer's click/mod/shortcut positions so clicking does not dismiss the layer, and deliberately leave the explicit exit key un-excluded. `require-prior-idle-ms` (e.g. 150) stops ball brushes mid-typing from raising the layer.

## Scroll

`&zip_xy_to_scroll_mapper` maps x to horizontal wheel and y to vertical: horizontal scroll comes free but feels unusable without axis locking. Add kot149/zmk-scroll-snap (`&zip_scroll_snap`, AFTER the mapper) to lock each gesture to its dominant axis. Speed via `&zip_scroll_scaler <mul> <div>`. Direction fixes belong on the sensor node (`x-invert`/`y-invert`/`xy-swap`), not in software chains.

## Pointer speed

CPI is the clean lever (sensor resolution), software scalers multiply counts. ZMK has no acceleration curve; the OS pointer acceleration still applies. Typical: 800-1200 CPI pointer ball, 200-400 scroll ball, `&zip_xy_scaler 3 4`-ish for a precision mode.

## Motion-to-keypress gestures (experimental module)

zettaface/zmk-input-processor-keybind quantizes motion into key behaviors. Verified details: binding order is RIGHT, LEFT, DOWN, UP (source enum); `mode = <1>` is 4-way; `tick` = movement units per activation (scale to CPI: ~60 at CPI 200, ~200 at CPI 800); `wait-ms` is the anti-repeat cooldown (250 for one-shot flicks, ~80 for continuous actions like pane resizing); follow with `&zip_xy_scaler 0 1` to zero residual motion so gestures do not also move the pointer. Vertical sense depends on sensor orientation; expect to swap the down/up binding pair after first hardware test. Module self-describes as unstable: keep it inside layer-scoped children so removal cannot affect anything else.

## Which half to flash

Sensor node and split-node changes: the half that owns the device. Listener/keymap changes: central (but the keymap compiles into both; flash both when unsure). Peripheral processing changes (e.g. moving to raw motion): BOTH halves, and a stale peripheral silently sends pre-processed events that make central-side logic appear broken.
