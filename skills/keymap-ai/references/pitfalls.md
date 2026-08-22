# Pitfall database

Field-verified failure modes. Match user symptoms here before deep debugging; each entry names the symptom, cause, and fix.

## Firmware behavior

1. **A per-layer input override never fires.** A listener child with layer 0 in its `layers` list matches on every layer (layer 0 is always active) and shadows all children declared after it. Fix: layer 0 behavior goes in the base chain; children only for exception layers.
2. **The wrong input override fires when two layers are active.** Momentary holds and temp-layer tails keep multiple layers active; the first declared matching child wins. Fix: order children by priority, not chronology.
3. **A layer keeps re-activating while using a second pointing device, or times out during active use.** Driver automouse timers refresh only from their own sensor. Fix: core `&zip_temp_layer` shared by both devices' chains.
4. **Peripheral-side trackball ignores layers.** Input-split processing happens before transmission. Fix: raw motion over the link, interpret on the central listener.
5. **Smart layer (num_word) drops unexpectedly, or never drops.** `continue-list` replaces defaults when set; entries match keycode+modifier subset; the terminating key press executes ON the layer before deactivation. Check all three.
6. **Flicking/typing right after a tap-dance key lands on the old layer.** Tap-dance waits its tapping-term to resolve; motion is not a key event and does not resolve it early. Fix: brief pause, or reduce the term, or avoid tap-dance for latency-sensitive entry.
7. **Devicetree parse error "expected number or parenthesized expression" at a keycode.** Missing dt-bindings header for that keycode family (`outputs.h` for `&out`, `bt.h` for `&bt`, `pointing.h`, `rgb.h`). The line/column in the error points at the first bare token.
8. **Keys type garbage after a keymap change that "should work".** ZMK Studio persists runtime changes in flash across reflashes; they shadow keymap edits until Restore Stock Settings (or settings_reset firmware) clears them.
9. **Hold-to-repeat stopped working everywhere.** A hold-tap with `quick-tap-ms 0` never auto-repeats. Set ~150-200.
10. **New firmware behaves like the old one.** A stale half: peripheral-processing changes require flashing BOTH halves; artifact downloaded from the wrong CI run; or Studio state (see 8).

## Toolchain and repo

11. **`git push` rejected right after CI ran.** The diagram bot committed to the remote. `git pull --rebase` is part of the push rhythm; conflicts in generated SVG/YAML files can be resolved either way, CI redraws them.
12. **keymap-drawer single-layer images are half empty.** `n_columns` in draw_config applies to single-layer draws too, reserving blank columns. Remove it (or use a draw-specific config) for per-layer output.
13. **SVGs render tiny on GitHub.** Dimensionless SVGs (no width/height) get a small default size in `<img>` contexts. Do the opposite of stripping: oversize the declared width/height (e.g. 2x) and let GitHub's `max-width: 100%` clamp them to full column width.
14. **SVG previews look corrupted in a raster tool but fine on GitHub.** cairosvg mishandles percentage font sizes and prefers-color-scheme blocks. Verify with a real browser engine (headless Chromium) before "fixing" the SVG.
15. **Diagram styling readable in light mode only.** Hardcoded label/fill colors fight dark mode. Use keymap-drawer `dark_mode: auto` and keep custom colors to elements that carry their own background (e.g. a colored key) with outlined text.
16. **Skill/CI advice rot.** Module revisions move; check the module's releases for one matching the user's ZMK release (many publish `v0.x` branches in lockstep) rather than pinning `main` or trusting remembered revisions.

17. **A config-folder shield overlay silently does nothing for one property.** Devicetree fragments merge in order and the LAST writer wins; a shield module's own overlay is merged after `config/boards/shields/...` copies, so a property both files set keeps the module's value while everything else from the config copy applies. Symptom class: "I changed X and nothing happened". Fix: put contested overrides in the `.keymap` file, which is merged last of all; ALWAYS verify final values in the compiled `build/zephyr/zephyr.dts` rather than in the overlay you edited. (Hardware-verified: a module overlay's hardcoded `zip_temp_layer 4 600` outranked two config overlays saying `5 800`.)

18. **After inserting a layer and renumbering, a half randomly "dies", enters the bootloader mid-use, or toggles layers on its own.** Some module or overlay outside the repo still holds a hardcoded layer INDEX (see 17); after renumbering it points at a different layer. Worst case: an automouse processor raising the SYSTEM layer on every ball twitch, so ordinary typing lands on `&bootloader`/`&sys_reset`/`&soft_off` keys. Fixes: grep the entire west workspace (all modules, not just the repo) for old layer indices before renumbering; keep `&bootloader`/`&soft_off` off any layer an automatic mechanism can raise. Symptom signature worth memorizing: "half dead, red LED, needs reset, USB logger drops to prompt" = the half is sitting in its UF2 bootloader, not crashed.

19. **A "dead" split half that reflashing old firmware always revives.** Check whether the half is in its bootloader (mass-storage drive mounted, bootloader LED) before assuming firmware breakage; an accidental `&bootloader` press (see 18) puts it there, and any reflash "fixes" it only because flashing exits the bootloader. Also produces confusing "instant eject, no transfer time" reports when a UF2 copy targets a drive in an unexpected state.

20. **Layer lookups scramble after changing layer structure with ZMK Studio enabled.** Studio persists a layer-order table (`keymap_layer_orders`) in NVS and every index-to-id lookup goes through it; stored state from the old structure misdirects lookups under the new one, especially when a layer is INSERTED (appending preserves existing ids). Fix ritual after any layer-structure change: Studio -> Restore Stock Settings (does not touch Bluetooth bonds), then reset the half.

21. **Peripheral-half firmware suspected after a keymap change.** Rebuild both commits locally and compare: peripheral images are typically byte-identical across keymap-only changes (the keymap compiles out of the peripheral), which exonerates that half in minutes and redirects the search to the central. `west build` with the gnuarmemb toolchain reproduces CI closely enough for this comparison.
