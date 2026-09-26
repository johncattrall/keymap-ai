# Keeping ZMK and QMK boards in sync

For users running the same layout on boards with different firmware. The
approach is drift detection, not code generation: both keymaps stay
independently editable, and `scripts/sync_keymaps.py` reduces each to
canonical (layer, position) -> {tap, hold} bindings through a ZMK<->QMK
equivalence table and diffs them. Board-specific hardware (Bluetooth rows,
soft-off, trackball cells, encoders) is declared per-layer in a YAML config
and reported as intentional rather than drift. Run it in both repos' CI so
a push that changes shared layout in one repo fails the other's check until
the change is ported; porting is mechanical for anything both firmwares can
express.

Hardware-verified equivalences the script encodes (also useful when porting
by hand):

- ZMK `&kp X` and `&as X` both normalize to a plain tap; QMK autoshift is a
  global feature, not per-key syntax.
- `&hml/&hmr/&mt MOD X` <-> `MOD_T(KC_X)`; `&lt L X` <-> `LT(L, KC_X)`;
  `&mo/&tog` <-> `MO()/TG()`. Layer identity must be compared through a name
  map, never raw indices: the boards may hold different layer counts (a
  trackball Mouse layer with no wired counterpart) so the same layer can sit
  at different indices per board.
- Modifier chords compare side-insensitively by default (`RS(RA(RC(T)))` on
  one board, `MEH(KC_T)` on the other: same effect on the host).
- Custom constructs pair up via an explicit `equiv` table: a ZMK tap-dance
  node <-> `TD(...)`, a smart-layer behavior <-> its custom keycode, ZMK
  mod-morph shift pairs <-> QMK key overrides.
- Fall-through equivalence: an alternate alpha layer is a toggled overlay in
  ZMK (thumbs can be `&trans`) but a DEFAULT layer in QMK, where transparent
  keys have nothing to fall through to and must be duplicated explicitly.
  The checker treats ZMK-transparent as equal to a QMK binding that matches
  the QMK base layer at the same position.

Porting checklist beyond bindings: hold-tap feel (ZMK timeless HRM ~=
Achordion or CHORDAL_HOLD plus PERMISSIVE_HOLD and QUICK_TAP_TERM), combos
(QMK combos are keycode-based; set `COMBO_ONLY_FROM_LAYER 0` to make them
positional like ZMK's), autoshift timeout, and smart-layer continue rules,
which need custom C on QMK.
