#!/usr/bin/env python3
"""sync_keymaps.py - cross-firmware keymap drift checker (ZMK <-> QMK).

Parses a ZMK .keymap and a QMK keymap.c for the same physical board shape,
normalizes both into canonical (layer, position) -> {tap, hold} bindings via
a ZMK<->QMK equivalence table, and reports drift. Positions where the boards
legitimately differ (board-specific hardware) are declared in a YAML config
and reported separately as intentional.

Usage:
  sync_keymaps.py --zmk zmk-config/config/board.keymap \
                  --qmk qmk-config/keymaps/default/keymap.c \
                  --config sync.yaml [--strict]

Config (YAML):
  layers:            # zmk layer node order -> qmk layer enum order, by name
    - [layer_0, BASE]
    - [layer_1, NAV]
    ...
  ignore:            # positions that are intentionally board-specific
    SYS: [0, 1, 3, 4, 5, ...]      # by qmk layer name, 0-based position
  equiv:             # extra token equivalences, zmk-token: qmk-token
    "td_num": "TD(TD_NUM)"
  ignore_mod_side: true

Exit code 1 when unintentional drift is found (CI-friendly).
Only stdlib + pyyaml. MIT, part of keymap-ai.
"""
import argparse, re, sys
try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")

# ---------- canonical key names ----------
ZMK_KEY = {
    "SPACE": "SPC", "ENTER": "ENT", "RET": "ENT", "ESCAPE": "ESC",
    "BACKSPACE": "BSPC", "BSPC": "BSPC", "DELETE": "DEL", "DEL": "DEL",
    "COMMA": "COMM", "DOT": "DOT", "PERIOD": "DOT", "FSLH": "SLSH",
    "SLASH": "SLSH", "BSLH": "BSLS", "BACKSLASH": "BSLS",
    "APOS": "QUOT", "SQT": "QUOT", "APOSTROPHE": "QUOT",
    "MINUS": "MINS", "EQUAL": "EQL", "GRAVE": "GRV",
    "LBKT": "LBRC", "RBKT": "RBRC", "LEFT_BRACKET": "LBRC",
    "RIGHT_BRACKET": "RBRC", "SEMI": "SCLN", "SEMICOLON": "SCLN",
    "CAPS": "CAPS", "CAPSLOCK": "CAPS", "TAB": "TAB",
    "PAGE_UP": "PGUP", "PG_UP": "PGUP", "PAGE_DOWN": "PGDN", "PG_DN": "PGDN",
    "LEFT_ARROW": "LEFT", "RIGHT_ARROW": "RGHT", "UP_ARROW": "UP",
    "DOWN_ARROW": "DOWN", "LEFT": "LEFT", "RIGHT": "RGHT", "UP": "UP",
    "DOWN": "DOWN", "K_MUTE": "MUTE", "C_MUTE": "MUTE",
    "C_VOL_UP": "VOLU", "C_VOL_DN": "VOLD",
    "PLUS": "PLUS", "ASTRK": "ASTR", "STAR": "ASTR",
    "QMARK": "QUES", "UNDER": "UNDS", "UNDERSCORE": "UNDS",
    "GT": "GT", "LT": "LT", "DQT": "DQT", "EXCL": "EXLM",
    "LCTRL": "LCTL", "LEFT_CONTROL": "LCTL", "LEFT_ALT": "LALT",
    "LEFT_GUI": "LGUI", "LEFT_SHIFT": "LSFT", "LSHFT": "LSFT",
    "RCTRL": "RCTL", "RIGHT_CONTROL": "RCTL", "RIGHT_ALT": "RALT",
    "RIGHT_GUI": "RGUI", "RIGHT_SHIFT": "RSFT", "RSHFT": "RSFT",
    "LCLK": "BTN1", "RCLK": "BTN2", "MCLK": "BTN3",
    "MB1": "BTN1", "MB2": "BTN2", "MB3": "BTN3", "MB4": "BTN4", "MB5": "BTN5",
}
ZMK_MOD = {
    "LEFT_CONTROL": "LC", "LCTRL": "LC", "LEFT_ALT": "LA", "LALT": "LA",
    "LEFT_GUI": "LG", "LGUI": "LG", "LCMD": "LG", "LEFT_SHIFT": "LS",
    "LSHFT": "LS", "LSHIFT": "LS", "RIGHT_CONTROL": "RC", "RCTRL": "RC",
    "RIGHT_ALT": "RA", "RALT": "RA", "RIGHT_GUI": "RG", "RGUI": "RG",
    "RIGHT_SHIFT": "RS", "RSHFT": "RS", "RSHIFT": "RS",
    "LCTL": "LC", "LSFT": "LS", "RCTL": "RC", "RSFT": "RS",
}
QMK_MODTAP = {  # QMK mod-tap/mod-wrap name -> canonical mod
    "LCTL": "LC", "LALT": "LA", "LGUI": "LG", "LSFT": "LS", "LOPT": "LA",
    "LCMD": "LG", "RCTL": "RC", "RALT": "RA", "RGUI": "RG", "RSFT": "RS",
    "ROPT": "RA", "RCMD": "RG", "C": "LC", "A": "LA", "G": "LG", "S": "LS",
}

def canon_key(name: str) -> str:
    name = name.strip()
    if name.startswith("KC_"):
        name = name[3:]
    if name.startswith("MS_BTN"):
        return "BTN" + name[6:]
    if name.startswith("BTN"):
        return name
    if re.fullmatch(r"N(UMBER_)?([0-9])", name):
        return re.fullmatch(r"N(UMBER_)?([0-9])", name).group(2)
    if re.fullmatch(r"[0-9]", name):
        return name
    return ZMK_KEY.get(name, name)

def canon_mods(mods: set, ignore_side: bool) -> tuple:
    if ignore_side:
        mods = {m[1] for m in mods}   # drop L/R prefix
    return tuple(sorted(mods))

MODFN = re.compile(r"^(LS|LC|LA|LG|RS|RC|RA|RG|LSFT|LCTL|LALT|LGUI|RSFT|RCTL|RALT|RGUI|S|C|A|G|MEH|HYPR|LSA|LCA|LAG|LCAG|SGUI|LSG|RSA|RCS|RCA)\((.*)\)$")
COMPOUND = {
    "MEH": {"LS", "LC", "LA"}, "HYPR": {"LS", "LC", "LA", "LG"},
    "LSA": {"LS", "LA"}, "LCA": {"LC", "LA"}, "LAG": {"LA", "LG"},
    "LCAG": {"LC", "LA", "LG"}, "SGUI": {"LS", "LG"}, "LSG": {"LS", "LG"},
    "RSA": {"RS", "RA"}, "RCS": {"RC", "RS"}, "RCA": {"RC", "RA"},
    "S": {"LS"}, "C": {"LC"}, "A": {"LA"}, "G": {"LG"},
}

def unwrap_mods(expr: str) -> tuple:
    """LG(LA(X)) / MEH(KC_X) / LS(LA(H)) -> (base, {mods})"""
    mods = set()
    expr = expr.strip()
    while True:
        m = MODFN.match(expr)
        if not m:
            break
        fn, inner = m.group(1), m.group(2)
        if fn in COMPOUND:
            mods |= COMPOUND[fn]
        else:
            mods.add(QMK_MODTAP.get(fn, ZMK_MOD.get(fn, fn)))
        expr = inner.strip()
    return canon_key(expr), mods

# ---------- ZMK parsing ----------
def parse_zmk(path, layer_names):
    text = open(path).read()
    defines = dict(re.findall(r"#define\s+(\w+)\s+(\S+)", text))
    layers = {}
    for m in re.finditer(r"(\w+)\s*\{[^{}]*?bindings\s*=\s*<(.*?)>\s*;", text, re.S):
        name, body = m.group(1), m.group(2)
        if name not in [ln[0] for ln in layer_names]:
            continue
        toks = ["&" + " ".join(t.split()) for t in body.split("&") if t.strip()]
        layers[name] = toks
    return layers, defines

def norm_zmk(tok, defines, cfg, ignore_side):
    parts = tok.replace("&", "", 1).split()
    b, args = parts[0], [defines.get(a, a) for a in parts[1:]]
    if tok in cfg.get("equiv", {}):
        return ("SPECIAL", cfg["equiv"][tok])
    key = " ".join([b] + parts[1:])
    if key in cfg.get("equiv", {}):
        return ("SPECIAL", cfg["equiv"][key])
    if b == "trans":
        return ("TRNS",)
    if b == "none":
        return ("NONE",)
    if b in ("kp", "as"):            # autoshift == plain tap cross-firmware
        base, mods = unwrap_mods(args[0])
        return ("KEY", base, canon_mods(mods, ignore_side))
    if b == "shifted":               # macro: LS(x)
        base, mods = unwrap_mods(args[0])
        mods.add("LS")
        return ("KEY", base, canon_mods(mods, ignore_side))
    if b in ("hml", "hmr", "mt"):
        return ("MT", ZMK_MOD.get(args[0], args[0])[:2] if args[0] in ZMK_MOD else ZMK_MOD.get(args[0], args[0]), canon_key(args[1]))
    if b == "lt":
        return ("LT", args[0], canon_key(args[1]))
    if b == "mo":
        return ("MO", args[0])
    if b == "tog":
        return ("TG", args[0])
    if b == "mkp":
        return ("KEY", canon_key(args[0]), ())
    return ("SPECIAL", tok)

# ---------- QMK parsing ----------
def parse_qmk(path, layer_names):
    text = open(path).read()
    defines = dict(re.findall(r"#define\s+(\w+)\s+(.+)", text))
    layers = {}
    for m in re.finditer(r"\[(\w+)\]\s*=\s*LAYOUT\w*\(", text):
        name = m.group(1)
        i, depth, buf, toks = m.end(), 1, "", []
        while depth > 0 and i < len(text):
            c = text[i]
            if c == "(":
                depth += 1; buf += c
            elif c == ")":
                depth -= 1
                if depth > 0: buf += c
            elif c == "," and depth == 1:
                toks.append(buf.strip()); buf = ""
            else:
                buf += c
            i += 1
        if buf.strip():
            toks.append(buf.strip())
        layers[name] = toks
    return layers, defines

def expand_qmk(tok, defines):
    seen = set()
    while tok in defines and tok not in seen:
        seen.add(tok); tok = defines[tok].strip()
    return tok

def norm_qmk(tok, defines, cfg, ignore_side, zmk_layer_of):
    tok = expand_qmk(tok, defines)
    if tok in ("KC_TRNS", "_______"):
        return ("TRNS",)
    if tok in ("KC_NO", "XXXXXXX"):
        return ("NONE",)
    m = re.match(r"^(\w+)_T\((KC_\w+)\)$", tok)
    if m:
        return ("MT", QMK_MODTAP.get(m.group(1), m.group(1)), canon_key(m.group(2)))
    m = re.match(r"^LT\((\w+),\s*(KC_\w+)\)$", tok)
    if m:
        return ("LT", zmk_layer_of.get(m.group(1), m.group(1)), canon_key(m.group(2)))
    m = re.match(r"^MO\((\w+)\)$", tok)
    if m:
        return ("MO", zmk_layer_of.get(m.group(1), m.group(1)))
    m = re.match(r"^TG\((\w+)\)$", tok)
    if m:
        return ("TG", zmk_layer_of.get(m.group(1), m.group(1)))
    base, mods = unwrap_mods(tok)
    return ("KEY", base, canon_mods(mods, ignore_side))

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zmk", required=True)
    ap.add_argument("--qmk", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--strict", action="store_true",
                    help="also fail on SPECIAL-vs-SPECIAL mismatches")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    ignore_side = cfg.get("ignore_mod_side", True)
    pairs = [tuple(p) for p in cfg["layers"]]
    cfg["equiv"] = cfg.get("equiv", {}) or {}
    cfg["equiv_rev"] = {v: k for k, v in cfg["equiv"].items()}
    # map qmk layer enum name -> zmk define used in lt/mo/tog comparison space
    layer_alias = cfg.get("layer_alias", {})  # e.g. NAV: L_NAV
    zmk_layer_of = None  # built after zmk defines are parsed

    zl, zdef = parse_zmk(args.zmk, pairs)
    ql, qdef = parse_qmk(args.qmk, pairs)
    zmk_layer_of = {q: zdef.get(layer_alias.get(q, q), layer_alias.get(q, q))
                    for _, q in pairs}

    drift, intentional, special = [], [], []
    for zname, qname in pairs:
        zt, qt = zl.get(zname), ql.get(qname)
        if zt is None or qt is None:
            drift.append((qname, "-", "MISSING LAYER", zt is None, qt is None))
            continue
        if len(zt) != len(qt):
            drift.append((qname, "-", f"key count {len(zt)} vs {len(qt)}", "", ""))
            continue
        ignored = set(cfg.get("ignore", {}).get(qname, []))
        for pos, (a, b) in enumerate(zip(zt, qt)):
            na = norm_zmk(a, zdef, cfg, ignore_side)
            nb = norm_qmk(b, qdef, cfg, ignore_side, zmk_layer_of)
            bx = expand_qmk(b, qdef)
            # SPECIAL equivalence: config maps zmk token string -> qmk token
            if na[0] == "SPECIAL" and na[1] in (b, bx):
                continue
            if na[0] == "SPECIAL" and nb[0] == "SPECIAL":
                if na[1] == b or nb[1] == a or na[1] == nb[1]:
                    continue
                (special if not args.strict else drift).append(
                    (qname, pos, a.strip(), b.strip()))
                continue
            # fall-through equivalence for default-layer alternates
            if na == ("TRNS",) and nb != ("TRNS",):
                base_q = ql.get(pairs[0][1])
                if base_q and pos < len(base_q):
                    nb_base = norm_qmk(base_q[pos], qdef, cfg, ignore_side, zmk_layer_of)
                    if nb == nb_base:
                        continue
            # layer names: compare via alias map
            if na != nb:
                row = (qname, pos, a.strip(), b.strip())
                (intentional if pos in ignored else drift).append(row)

    if intentional:
        print(f"intentionally different ({len(intentional)}):")
        for r in intentional:
            print(f"  [{r[0]}:{r[1]}]  zmk: {r[2]:<28} qmk: {r[3]}")
    if special:
        print(f"special (unverified equivalence, pass --strict to fail) ({len(special)}):")
        for r in special:
            print(f"  [{r[0]}:{r[1]}]  zmk: {r[2]:<28} qmk: {r[3]}")
    if drift:
        print(f"DRIFT ({len(drift)}):")
        for r in drift:
            print(f"  [{r[0]}:{r[1]}]  zmk: {r[2]:<28} qmk: {r[3]}")
        sys.exit(1)
    print("in sync: no unintentional drift.")

if __name__ == "__main__":
    main()
