# Alternate alpha layouts: advice and generation

## Honest guidance first (give this before generating anything)

Behavior and layer improvements deliver most of the comfort win for zero relearning; an alpha switch costs 2-6 weeks of reduced speed, breaks vim HJKL muscle memory, and complicates OS shortcuts. Recommend alphas only for comfort/RSI-driven users or the deliberately curious, and always as a TOGGLE so QWERTY remains one keypress away.

Quick chooser:

- **Colemak-DH**: gentlest transition from QWERTY (many keys keep positions), largest ecosystem and OS-level fallbacks.
- **Graphite / Gallium**: current best all-round metrics (low same-finger bigrams, low lateral stretch); custom shifted punctuation pairs; smaller ecosystem.
- **Canary**: roll-heavy feel, for people who liked Colemak but want more rolls.
- **Dvorak**: historical; rarely the right recommendation today.

The curated list above is guidance, not a limit: generation works for ANY published layout (Workman, Sturdy, Focal, Engram, Hands Down variants, Semimak, MTGAP, APT, Norman, ...) because the recipe is spec-driven. Fetch the layout's official spec (letters AND shift pairs) from its repo at generation time; do not recite from memory. For obscure layouts without a canonical spec repo, ask the user to paste their reference grid.

## Generation recipe (ZMK)

1. **Insertion index matters**: highest active layer wins in ZMK, so an alpha layer must sit BELOW all function layers: insert directly above base (index 1), never append after function layers.
2. **Renumber once, with defines**: inserting shifts every later index. Convert all raw indices (`&to`, `&lt`, `&mo`, tap-dance params, `&num_word`, temp-layer/automouse targets, listener children `layers`) to `#define L_NAME n` in the same change so this is the last renumbering ever.
3. **Positional carry-over**: home row mods stay on the same physical fingers wrapping the new letters; autoshift/behavior wrappers likewise. The layer-access key (e.g. `&lt L_SYS Q`) keeps its hold on the same position wrapping the new letter.
4. **Freed and displaced keys**: layouts move punctuation onto/off the main grid; re-home displaced keys deliberately (e.g. if `'` moves onto the grid, its old thumb can become Backspace on this layer; if a letter lands on a former Backspace position, decide where Backspace lives on this layer).
5. **Custom shift pairs**: mod-morphs (see behaviors-zmk.md) for every pair that differs from US-QWERTY shifting.
6. **Toggle**: `&tog L_ALT_ALPHA` on the system layer. Toggles do not survive power cycles; say so.
7. **Diagrams**: the drawing pipeline picks the layer up automatically; add the README embed.

## Generation recipe (QMK, beta)

Same logic, simpler mechanics: define the layout layer in `keymap.c`, `DF()`/`TG()` to switch (DF persists until power-off; use `set_single_persistent_default_layer` + EEPROM for sticky), Key Overrides or custom shift handling for non-standard pairs. Compile-verify with `qmk compile`; hardware-verify before trusting, and label the advice beta.

## What does NOT change with an alpha switch

Positional things: combos defined by key positions, layer access holds, trackball/encoder behavior, physical nav clusters. Keycode things DO follow the OS: window-manager chords still emit the same letters. Vim users: HJKL as arrows breaks semantically; offer a nav-layer arrows habit instead.
