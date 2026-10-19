# Ristretto for YouTube

Custom CSS theme for **Enhancer for YouTube** (and any Stylish/Stylus-style injector),
built from the omarchy `ristretto` palette. This is the hand-checked snapshot — the
rest of the theme family and the generator live in the parent directory.

| file | what it is |
|---|---|
| `ristretto-youtube.css` | the theme — paste the whole file into the Custom theme box |
| `omarchy-colors.toml` | frozen copy of the source palette (`/usr/share/omarchy/themes/ristretto/colors.toml`) for reference |
| `preview.png` | screenshot of the theme applied to youtube.com |

## Palette → role mapping

| role | hex | omarchy key |
|---|---|---|
| canvas | `#211b1b` | dark_background |
| top bar, scrollbar track | `#181414` | darker_background |
| search, menus, panels | `#2c2525` | background |
| hover, raised | `#3d2f2a` | lighter_background |
| accent (progress bar, CTA, logo, active nav) | `#f38d70` | accent |
| accent hover | `#fb9a77` | orange |
| primary text | `#e6d9db` | foreground |
| secondary text | `#c3b7b8` | light_foreground |
| muted text / metadata | `#72696a` | muted / dark_foreground |
| LIVE badge | `#fd6883` | red |
| links, unvisited | `#f38d70` | accent |

## Install

1. Enhancer for YouTube → **Theme** → `YouTube Dark` (or turn on YouTube's own
   dark appearance). A CSS box cannot set YouTube's `dark` attribute, and the theme
   is written for a dark host.
2. Tick **Custom theme**.
3. Paste the full contents of `ristretto-youtube.css` into the box → **Save**.
4. Reload the YouTube tab.

## Tuning

Everything hangs off the `--rs-*` tokens at the top of the CSS:

```css
html {
  --rs-bg: #211b1b;      /* page canvas        */
  --rs-deep: #181414;    /* masthead, tracks   */
  --rs-surface: #2c2525; /* menus, search      */
  --rs-hover: #3d2f2a;   /* hover / raised     */
  --rs-accent: #f38d70;  /* progress bar, CTAs */
  --rs-fg: #e6d9db;      /* primary text       */
  --rs-muted: #72696a;   /* metadata           */
}
```

Swap `--rs-accent` for `#f9cc6c` (yellow) or `#a8a9eb` (magenta) to re-key the
theme without touching a selector.

## Notes / limits

- Same file as `../themes/ristretto.css` — regenerate with `../gen-theme.py ristretto`.
- Written against YouTube's 2026 UI: both the legacy custom elements (`ytd-*`,
  `ytp-*`) and the newer class-based components (`ytSearchboxComponent*`,
  `ytChipShape*`, `ytSpecButtonShapeNext*`, `ytBadgeShapeThumbnail*`, `yt-tab-shape`).
  YouTube hardcodes colors per element now — it publishes almost no `--yt-spec-*`
  variables — so a variable-only theme will appear to do nothing.
- Live chat is an iframe and always stays stock.
- If YouTube ships a redesign, the fix is an inventory pass: find elements whose
  computed `background-color` / `color` differ from their parent's, then re-map
  those to the `--rs-*` tokens.
