# ZMK behavior recipes

## Timeless home row mods (urob recipe)

Generate position defines for the actual key count first (print the grid). For a 3x5+3 split:

```dts
#define KEYS_L 0 1 2 3 4 10 11 12 13 14 20 21 22 23 24
#define KEYS_R 5 6 7 8 9 15 16 17 18 19 25 26 27 28 29
#define THUMBS 30 31 32 33 34 35

hml: home_row_mod_left {
    compatible = "zmk,behavior-hold-tap";
    #binding-cells = <2>;
    flavor = "balanced";
    tapping-term-ms = <280>;
    quick-tap-ms = <175>;
    require-prior-idle-ms = <150>;
    bindings = <&kp>, <&kp>;
    hold-trigger-key-positions = <KEYS_R THUMBS>;
    hold-trigger-on-release;
};
// hmr mirrors with KEYS_L THUMBS
```

Why each part: balanced flavor resolves as hold when another key press+release fits inside the term; the long term removes timing pressure; require-prior-idle kills misfires mid-typing-burst; positional triggers force same-hand presses to resolve as taps; hold-trigger-on-release allows stacking multiple mods on one hand. Expected user-visible change: same-hand mod chords now need the other hand or a deliberate hold past the term. Keep `label` properties if the user's existing behaviors carry them (their ZMK revision accepts them); do not add labels to fresh configs on newer ZMK.

## Smart layers (zmk-auto-layer)

num_word: tap once, layer activates, digits and continue-list keys keep it alive, first other key press ends it. Module: urob/zmk-auto-layer, revision matched to the ZMK release. `#include <behaviors/num_word.dtsi>`, bind `&num_word <LAYER>`.

Critical semantics (verified in source, behavior_auto_layer.c):

- Setting `continue-list` REPLACES the default list (`BACKSPACE DELETE DOT COMMA PLUS MINUS STAR FSLH EQUAL`); repeat the defaults when extending.
- Entries match keycode PLUS modifiers as a subset: `LS(LA(SPACE))` in the list keeps the layer alive for that chord while a plain Space still exits. Use this to whitelist exact shortcut chords fired from the layer.
- `ignore-numbers` (default in num_word.dtsi) keeps digits from ending it; `ignore-modifiers` covers bare modifier presses.
- Ball/pointer motion is not a key event and never ends a smart layer.
- The terminating key press is processed on the layer BEFORE deactivation: if the layer binds something at that position, that binding fires. Layers dense with bindings make surprising terminators; transparent positions fall through to base cleanly.

Tap-dance hybrid preserving a lock: `bindings = <&num_word N>, <&to N>, <&to M>;` gives tap = smart, double-tap = lock, triple-tap = other lock. Note tap-dance resolution wait (its tapping-term) before a lone tap takes effect.

## Thumb patterns

Layer-taps (`&lt`) beat `&to` locks for momentary access; keep locks reachable via double-tap or combos. `&caps_word` for CONSTANTS. One-shot `&sk LSHFT` is a cheap trial of Callum-style shifting. Respect deliberate thumb holds (dictation triggers, push-to-talk) before "fixing" them.

## Mod-morphs (custom shift pairs)

Needed for layouts like Graphite that re-pair shifted punctuation:

```dts
comma_morph: comma_morph {
    compatible = "zmk,behavior-mod-morph";
    #binding-cells = <0>;
    bindings = <&kp COMMA>, <&kp SEMI>;   // tap: , shift: ;
    mods = <(MOD_LSFT|MOD_RSFT)>;
};
```

Pull the layout's official shift-pair table from its spec repo at generation time; do not recite pairs from memory.

## Autoshift (macro + hold-tap pattern)

Hold-for-shifted via a one-param macro wrapping a tap-preferred hold-tap. Trade-offs to surface: capitals wait out the tapping term; `quick_tap_ms 0` kills repeat; HRM keys typically bypass it (two shift systems). Viable, especially with Shift demoted to selection duty; just make the inconsistency explicit.

## Travel soft off

```dts
&soft_off { hold-time-ms = <2000>; };
```

Plus `CONFIG_ZMK_PM_SOFT_OFF=y`. Bind on the system layer, both halves' outer corners. Central forwards shutdown to the peripheral first; wake is reset-button tap only, which is a feature: keys in a bag cannot wake it.
