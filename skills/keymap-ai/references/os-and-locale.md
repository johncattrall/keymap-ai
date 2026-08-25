# OS integration, window managers, and international layouts

## Ask the platform first

Modifier advice is platform-dependent; never recommend mod placement without knowing the OS mix.

| | macOS | Windows | Linux |
|---|---|---|---|
| Dominant shortcut mod | Cmd (GUI) | Ctrl | Ctrl |
| Rarest mod | Ctrl | GUI (mostly WM) | GUI (mostly WM) |
| Suggested home-row emphasis | GUI on index | Ctrl on index | Ctrl on index |
| Word-wise nav | Opt+arrows | Ctrl+arrows | Ctrl+arrows |
| Workspace switch | Ctrl+arrows (Spaces) | Win+Ctrl+arrows | WM-specific (Super+N) |

## Multi-OS keyboards (one board, several hosts)

ZMK cannot detect the host OS. The robust pattern couples OS choice to the Bluetooth profile the user already switches:

```dts
// System layer: one key per host = profile + OS layer together
mac_host: mac_host {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    bindings = <&bt BT_SEL 0>, <&to L_BASE>;         // mac uses base as-is
};
win_host: win_host {
    compatible = "zmk,behavior-macro";
    #binding-cells = <0>;
    bindings = <&bt BT_SEL 1>, <&tog L_WINMODS>;     // overlay swapping Cmd/Ctrl
};
```

The OS overlay layer redefines only the keys that differ (swapped GUI/Ctrl home-row mods, word-nav chords, shortcut macros). Keep it directly above base, below function layers. Alternative for light needs: duplicate chord keys per OS on a shortcuts layer, no overlay.

## Window manager cheat table

When wiring WM control into layers or pointer gestures, confirm the user's actual bindings (all of these are remappable):

| OS | WM | Default mod flavor | Notes |
|---|---|---|---|
| macOS | Amethyst | mod1 = Opt+Shift, mod2 = Ctrl+Opt+Shift | throw-to-space on mod2+arrows; several useful commands (focus main) unbound by default |
| macOS | Rectangle | Ctrl+Opt (+Cmd for thirds) | positional, not tiling |
| macOS | AeroSpace | Alt-based, i3-like | config file defines everything |
| macOS | yabai | none (skhd user-defined) | must ask the user |
| Linux | i3 / sway | $mod = Super typically | Super+1..N workspaces |
| Linux | Hyprland | SUPER | user config decides the rest |
| Windows | native + FancyZones | Win+arrows, Win+Ctrl+arrows (desktops) | zero-install baseline |
| Windows | komorebi / GlazeWM | Alt-based defaults | i3-flavored |

Collision check before binding: dictation/voice input (often a modified Space or a held key), Spotlight/PowerToys Run, screenshot chords. A "standard" WM chord that collides with the user's dictation trigger is a field-verified failure mode.

## Per-half battery levels on the host (hardware-verified on macOS; Windows app available)

Split centrals expose only their OWN battery over the standard Bluetooth
battery service by default; the peripheral's level never reaches the host.
Host apps that show both halves need the central to fetch and proxy it:
itouuuuuuuuu/zmk-battery-bar (macOS menu bar) and carlosedp/zmk-split-battery
(Windows 10 19041+ tray icon with low-battery toasts, needs the .NET Desktop
Runtime). Both read the same GATT battery services, so the firmware side is
identical. Add to the CENTRAL's .conf:

```ini
CONFIG_ZMK_BATTERY_REPORTING=y
CONFIG_ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_FETCHING=y
CONFIG_ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_PROXY=y
```

Only the central needs reflashing. Three gotchas, all field-verified:
battery data travels over Bluetooth GATT, so the host must be connected to
the keyboard via BLE (USB alone shows nothing); the proxy adds a SECOND
GATT battery service, and hosts cache GATT databases, so if only one level
appears after reflashing, remove and re-pair the keyboard once to force
fresh service discovery; native OS battery UIs often show only the first
service, which is expected, the per-half readout comes from the app.
Power cost is negligible: the peripheral already samples its battery on
the default ~60 s interval, and a level is only transmitted when the
integer percentage changes.

## International layouts (the "my keycodes type the wrong symbols" problem)

ZMK sends HID usage codes; the HOST's layout maps them to characters. `&kp SEMI` types ö on a German layout because the host says so. Tooling:

- **joelspadin/zmk-locale-generator** produces per-locale headers (`keys_de.h` etc.) defining names like `DE_OE` for the HID code that yields that character under the host layout. The companion **joelspadin/zmk-locales** module packages these for west.yml consumption. This is the correct fix for "I want to TYPE my language's characters and label them honestly in my keymap".
- Diagrams: keymap-drawer needs a matching `zmk_keycode_map` for locale headers; generate label maps alongside.
- Characters outside the host layout entirely need unicode input macros, which are OS-specific: macOS Option-codes or the Unicode Hex Input source, Windows WinCompose or Alt-codes, Linux IBus Ctrl+Shift+U. Community modules exist for unicode macros but every one is OS-conditional; wire them to the OS-overlay pattern above.
- Dead keys (´ ` ^ on intl layouts) behave as the HOST defines; a "types nothing until next key" report on an intl setup is usually a dead key, not a firmware bug.

Audit additions for non-US users: base layer keycodes named with US names but hosts set to another layout (works but unreadable and diagram-wrong: recommend locale headers); shifted-pair assumptions (US pairing baked into autoshift/mod-morph advice breaks on other layouts; derive pairs from the host layout).

## Board archetypes (calibrate advice to key count)

- **30-36 keys**: everything above applies at full strength: layers, combos, smart layers, thumb discipline are load-bearing.
- **40-50 keys**: number row or extra columns relieve pressure; smart num layers optional; HRM still the highest-value tune.
- **58+ / unibody / row-staggered conversions**: HRM and layers are preferences, not necessities; audits should not push minimalist dogma. Encoders/displays more common here.
- **One-handed / accessibility builds**: mirror layers (`&mo` + mirrored bindings), sticky mods, and dwell-friendly timings dominate; standard misfire advice may invert (longer terms, hold-preferred flavors).
