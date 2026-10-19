#!/usr/bin/env python3
"""Generate a YouTube custom theme CSS from an omarchy theme's colors.toml.

    ./gen-theme.py ristretto              # -> themes/ristretto.css
    ./gen-theme.py --all                  # every dark omarchy theme
    ./gen-theme.py rose-pine --force      # light themes (see note below)
    ./gen-theme.py ristretto --stdout     # print instead of writing

Theme sources, first match wins:
    ~/.config/omarchy/themes/<name>/colors.toml   (local override)
    /usr/share/omarchy/themes/<name>/colors.toml  (stock)

The palette is read fresh every run, so retuned themes regenerate correctly.
Light themes are skipped by default: the stylesheet forces dark surfaces, so a
light palette comes out with text the same shade as the background.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

try:
    import tomllib
except ModuleNotFoundError:  # python < 3.11
    sys.exit("gen-theme.py needs Python 3.11+ (tomllib)")

HERE = pathlib.Path(__file__).resolve().parent
THEME_DIRS = [
    pathlib.Path.home() / ".config" / "omarchy" / "themes",
    pathlib.Path("/usr/share/omarchy/themes"),
]
OUT_DIR = HERE / "themes"

# colors.toml key -> role. Ristretto mapping, valid for the rest of the set:
#   dark_background  #211b1b  page canvas
#   background       #2c2525  panels, search, menus
#   darker_background#181414  masthead, scroll tracks
#   lighter_background #3d2f2a hover / raised
ROLE_KEYS = {
    "bg": "dark_background",
    "surface": "background",
    "deep": "darker_background",
    "hover": "lighter_background",
    "accent": "accent",
    "fg": "foreground",
    "fg_dim": "light_foreground",
    "muted": "dark_foreground",
    "red": "red",
    "green": "green",
}


def find_theme(name: str) -> pathlib.Path:
    for base in THEME_DIRS:
        p = base / name / "colors.toml"
        if p.is_file():
            return p
    sys.exit(f"theme {name!r} not found in: " + ", ".join(str(d) for d in THEME_DIRS))


def load_colors(path: pathlib.Path) -> dict[str, str]:
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    missing = [k for k in (*ROLE_KEYS.values(), "mode") if k not in data]
    if missing:
        sys.exit(f"{path} is missing: {', '.join(missing)}")
    return {k: v for k, v in data.items() if isinstance(v, str)}


def mix(hex_color: str, with_hex: str, weight: float) -> str:
    """Blend hex_color toward with_hex by weight (0..1)."""
    a = [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(with_hex[i : i + 2], 16) for i in (1, 3, 5)]
    out = [round(x + (y - x) * weight) for x, y in zip(a, b)]
    return "#" + "".join(f"{c:02x}" for c in out)


def palette_block(name: str, c: dict[str, str]) -> str:
    r = {role: c[key] for role, key in ROLE_KEYS.items()}
    accent_soft = mix(r["accent"], "#ffffff", 0.18)
    # the yellow/orange of the palette is a nicer hover than a washed accent
    accent_soft = c.get("orange", accent_soft) if name in ("ristretto",) else accent_soft

    lines = [
        "html {",
        f"  /* --- {name} roles --- */",
        f"  --rs-bg: {r['bg']};",
        f"  --rs-deep: {r['deep']};",
        f"  --rs-surface: {r['surface']};",
        f"  --rs-hover: {r['hover']};",
        f"  --rs-accent: {r['accent']};",
        f"  --rs-accent-soft: {accent_soft};",
        f"  --rs-fg: {r['fg']};",
        f"  --rs-fg-dim: {r['fg_dim']};",
        f"  --rs-muted: {r['muted']};",
        f"  --rs-red: {r['red']};",
        f"  --rs-green: {r['green']};",
        "  --rs-line: color-mix(in srgb, var(--rs-fg) 12%, transparent);",
        "",
        "  /* translucent foreground tints (guides, chips, tracks) */",
        "  --rs-tint-6: color-mix(in srgb, var(--rs-fg) 6%, transparent);",
        "  --rs-tint-7: color-mix(in srgb, var(--rs-fg) 7%, transparent);",
        "  --rs-tint-8: color-mix(in srgb, var(--rs-fg) 8%, transparent);",
        "  --rs-tint-10: color-mix(in srgb, var(--rs-fg) 10%, transparent);",
        "  --rs-tint-14: color-mix(in srgb, var(--rs-fg) 14%, transparent);",
        "  --rs-tint-18: color-mix(in srgb, var(--rs-fg) 18%, transparent);",
        "  --rs-tint-22: color-mix(in srgb, var(--rs-fg) 22%, transparent);",
        "  --rs-tint-32: color-mix(in srgb, var(--rs-fg) 32%, transparent);",
        "  --rs-tint-40: color-mix(in srgb, var(--rs-fg) 40%, transparent);",
        "",
        "  /* legacy YouTube tokens, still used in a few spots */",
        f"  --yt-spec-base-background: {r['bg']};",
        f"  --yt-spec-raised-background: {r['surface']};",
        f"  --yt-spec-menu-background: {r['surface']};",
        f"  --yt-spec-general-background-a: {r['bg']};",
        f"  --yt-spec-general-background-b: {r['bg']};",
        f"  --yt-spec-general-background-c: {r['deep']};",
        f"  --yt-spec-brand-background-solid: {r['bg']};",
        f"  --yt-spec-brand-background-primary: {r['bg']};",
        f"  --yt-spec-text-primary: {r['fg']};",
        f"  --yt-spec-text-secondary: {r['fg_dim']};",
        f"  --yt-spec-text-disabled: {r['muted']};",
        f"  --yt-spec-icon-active-other: {r['fg']};",
        f"  --yt-spec-icon-inactive: {r['fg_dim']};",
        f"  --yt-spec-call-to-action: {r['accent']};",
        f"  --yt-spec-themed-blue: {r['accent']};",
        "  --yt-spec-badge-chip-background: color-mix(in srgb, var(--rs-fg) 8%, transparent);",
        f"  --yt-spec-static-brand-red: {r['accent']};",
        "  color-scheme: dark;",
        "}",
    ]
    return "\n".join(lines)


def build(name: str, force: bool) -> tuple[str, str]:
    path = find_theme(name)
    colors = load_colors(path)
    if colors.get("mode") == "light" and not force:
        raise SystemExit(
            f"{name}: light theme, skipped (the stylesheet forces dark surfaces). "
            "Use --force to generate anyway."
        )
    template = (HERE / "template.css").read_text()
    css = (
        template.replace("@@PALETTE@@", palette_block(name, colors))
        .replace("@@THEME@@", name)
        .replace("@@TITLE@@", f"{name.upper()} FOR YOUTUBE")
    )
    return name, css


def main() -> None:
    ap = argparse.ArgumentParser(description="omarchy theme -> YouTube custom CSS")
    ap.add_argument("theme", nargs="?", help="omarchy theme name, or --all")
    ap.add_argument("--all", action="store_true", help="build every dark omarchy theme")
    ap.add_argument("--force", action="store_true", help="allow light themes")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = ap.parse_args()

    if args.all:
        names = sorted(
            d.name
            for base in THEME_DIRS
            if base.is_dir()
            for d in base.iterdir()
            if (d / "colors.toml").is_file()
        )
        names = sorted(set(names))
        built = []
        for n in names:
            try:
                name, css = build(n, args.force)
            except SystemExit as exc:
                print(f"  skip {exc}", file=sys.stderr)
                continue
            OUT_DIR.mkdir(exist_ok=True)
            (OUT_DIR / f"{name}.css").write_text(css)
            built.append(name)
        print(f"wrote {len(built)} themes to {OUT_DIR}:")
        print("  " + "\n  ".join(built))
        return

    if not args.theme:
        dark, light = [], []
        seen = set()
        for base in THEME_DIRS:
            if not base.is_dir():
                continue
            for d in sorted(base.iterdir()):
                f = d / "colors.toml"
                if not f.is_file() or d.name in seen:
                    continue
                seen.add(d.name)
                mode = load_colors(f).get("mode", "dark")
                (light if mode == "light" else dark).append(d.name)
        print("dark themes (buildable):")
        print("  " + "  ".join(sorted(dark)))
        print("light themes (need --force):")
        print("  " + "  ".join(sorted(light)))
        print("\nusage: ./gen-theme.py <theme> [--stdout] | --all")
        return

    name, css = build(args.theme, args.force)
    if args.stdout:
        print(css)
        return
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{name}.css"
    out.write_text(css)
    print(f"wrote {out} ({len(css.splitlines())} lines)")


if __name__ == "__main__":
    main()
