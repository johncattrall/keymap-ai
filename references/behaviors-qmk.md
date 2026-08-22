# QMK behavior recipes (beta tier)

Compile-verify everything with `qmk compile`; verify current option names against docs.qmk.fm (QMK core moves faster than ZMK). Label hardware-untested advice as beta.

## Home row mods

```c
// config.h
#define TAPPING_TERM 200
#define PERMISSIVE_HOLD          // hold wins when another key press+release nests inside the term
#define QUICK_TAP_TERM 120       // double-tap-hold repeats the tap
```

For same-hand misfire suppression (the ZMK positional-trigger analog): QMK core's chordal-hold feature if present in the user's version, else getreuer's Achordion userspace library. Per-key tuning via `get_tapping_term()`. Discuss `HOLD_ON_OTHER_KEY_PRESS` vs `PERMISSIVE_HOLD` explicitly; the aggressive option suits thumb layer-taps more than home row mods.

## Caps Word

`CAPS_WORD_ENABLE = yes`; activation via `QK_CAPS_WORD_TOGGLE`, or both-shifts/double-shift options in config.h.

## One-shot mods (Callum-style)

`QK_ONE_SHOT_MOD` keycodes or `OSM(MOD_LSFT)`; `ONESHOT_TIMEOUT`; consider callum-style custom implementations only when core one-shots fall short.

## Custom shift pairs

Key Overrides (`KEY_OVERRIDE_ENABLE`) are the mod-morph analog:

```c
const key_override_t comma_semi = ko_make_basic(MOD_MASK_SHIFT, KC_COMM, KC_SCLN);
```

Needed for Graphite-style layouts; pull pairs from the layout spec.

## Layers

`MO`/`LT` for momentary, `TG` for locks, `DF` for base switching (non-persistent; `set_single_persistent_default_layer()` writes EEPROM). Keep alpha layers lowest; layer order semantics match ZMK (highest active wins).

## Smart-layer analog

QMK has no core num_word; getreuer's "layer lock" + community num-word implementations exist in userspace. Recommend only with the beta caveat, or approximate with `TG` plus a well-placed exit.

## Tap dance

`TAP_DANCE_ENABLE`; same latency caveat as ZMK: a lone tap resolves only after `TAPPING_TERM`.
