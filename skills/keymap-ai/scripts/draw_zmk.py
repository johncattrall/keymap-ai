#!/usr/bin/env python3
"""keymap-ai: parse a ZMK keymap and draw per-layer + combined SVGs.

Wraps keymap-drawer (pip install keymap-drawer) with the conventions from
references/diagrams.md:
  - per-layer SVGs named <name>_<layer-slug>.svg plus a combined <name>.svg
  - optional virtual keys (trackballs/encoders) injected from a YAML file
  - declared SVG dimensions doubled so GitHub renders images at full
    column width (max-width clamps them)

Usage:
  draw_zmk.py --keymap config/kb.keymap --layout config/info.json \
              [--layout-name NAME] [--config keymap_drawer.config.yaml] \
              [--virtual-keys keymap-drawer/trackballs.yaml \
               --virtual-positions '[{"x":5.0,"y":2.2,"w":1.4,"h":1.4}, ...]'] \
              [--out-dir keymap-drawer] [--name kb]

The virtual-keys YAML maps layer display-names to a list of drawer key specs
(one per virtual position, in order), with a required "default" entry:
  default:
    - {t: Scroll, h: v+h snap, type: trackball}
    - {t: Pointer, type: trackball}
  Mouse:
    - {t: Precision, type: trackball}
    - {t: Pointer, type: trackball}
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

import yaml


def run(cmd, out_path=None):
    if out_path:
        with open(out_path, "w") as fh:
            subprocess.run(cmd, stdout=fh, check=True)
    else:
        return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--keymap", required=True)
    ap.add_argument("--layout", required=True, help="QMK-style info.json physical layout")
    ap.add_argument("--layout-name", default=None, help="layout key inside info.json (default: first)")
    ap.add_argument("--config", default="keymap_drawer.config.yaml")
    ap.add_argument("--virtual-keys", default=None, help="YAML of per-layer labels for virtual keys")
    ap.add_argument("--virtual-positions", default=None, help="JSON list of layout entries for virtual keys")
    ap.add_argument("--out-dir", default="keymap-drawer")
    ap.add_argument("--name", default=None, help="output basename (default: keymap filename stem)")
    args = ap.parse_args()

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    name = args.name or pathlib.Path(args.keymap).stem
    parsed_path = out / f"{name}.yaml"

    base = ["keymap", "-c", args.config]
    run(base + ["parse", "-z", args.keymap], parsed_path)

    # physical layout, with optional virtual keys appended
    info = json.load(open(args.layout))
    layout_key = args.layout_name or next(iter(info["layouts"]))
    draw_layout_path = args.layout
    if args.virtual_positions:
        positions = json.loads(args.virtual_positions)
        info["layouts"][layout_key]["layout"].extend(positions)
        draw_layout_path = str(out / "layout.json")
        json.dump(info, open(draw_layout_path, "w"), indent=1)

    # per-layer virtual key labels
    km = yaml.safe_load(open(parsed_path))
    if args.virtual_keys:
        labels = yaml.safe_load(open(args.virtual_keys))
        if "default" not in labels:
            sys.exit("virtual-keys YAML needs a 'default' entry")
        for layer, keys in km["layers"].items():
            keys.extend(labels.get(layer, labels["default"]))
        yaml.safe_dump(km, open(parsed_path, "w"), allow_unicode=True, sort_keys=False)

    draw = base + ["draw", str(parsed_path), "-j", draw_layout_path]
    if args.layout_name:
        draw += ["-l", args.layout_name]
    generated = []
    for layer in km["layers"]:
        target = out / f"{name}_{slug(layer)}.svg"
        run(draw + ["-s", layer], target)
        generated.append(target)
        print(f"drew {layer}")
    combined = out / f"{name}.svg"
    run(draw, combined)
    generated.append(combined)

    # Oversize declared dimensions to 2x the viewBox so GitHub renders
    # full-width (see diagrams.md). Only touch files generated THIS run,
    # and only when still at 1x, so re-runs never compound the scaling.
    pat = re.compile(r'^<svg width="([0-9.]+)" height="([0-9.]+)" viewBox="0 0 ([0-9.]+) ([0-9.]+)"')
    for svg_path in generated:
        svg = svg_path.read_text()
        m = pat.match(svg)
        if m and abs(float(m.group(1)) - float(m.group(3))) < 0.01:
            w, h = int(float(m.group(3))) * 2, int(float(m.group(4))) * 2
            svg_path.write_text(pat.sub(
                f'<svg width="{w}" height="{h}" viewBox="0 0 {m.group(3)} {m.group(4)}"', svg, count=1))
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
