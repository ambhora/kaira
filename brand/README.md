# Kaira brand assets

Source files are SVG; PNG exports are provided at the canonical sizes.

| File | Size | Use |
| --- | --- | --- |
| `kaira-icon.svg` / `.png` | 1600 × 1600 | App icon, favicon, avatars. Rounded square, navy background. |
| `kaira-wordmark.svg` / `.png` | 2098 × 1000 | Wordmark alone, navy on light backgrounds. |
| `kaira-wordmark-white.svg` | 2098 × 1000 | Wordmark alone on dark backgrounds. |
| `kaira-logo.svg` / `.png` | 4598 × 2200 | Icon with wordmark to its right; 300 units of spacing between them and 300 units of padding on all sides. Light backgrounds. |
| `kaira-logo-dark.svg` / `.png` | 4598 × 2200 | Same lockup on a navy-dark background. |
| `kaira-mark-mono.svg` | 1600 × 1600 | The mark alone, single colour (`currentColor`), no background. Used in the documentation header. |

The wordmark is set in Inter SemiBold, converted to outlines; no font is
required to render it.

## Colours

| Name | Hex | Role |
| --- | --- | --- |
| Navy | `#1F3A5F` | Primary. Icon background, header, wordmark on light backgrounds. |
| Navy dark | `#142843` | Dark-mode primary and dark lockup background. |
| Teal | `#0F8B8D` | Accent on light backgrounds: links, active states. |
| Teal light | `#4FC3C5` | Accent on dark backgrounds; the tree in the icon. |
| Ink | `#1F2D3D` | Body text and diagram text. |
| Slate | `#5B6B7F` | Secondary text, diagram lines and labels. |
| Mist | `#F4F7FB` | Light panel and figure backgrounds. |

Diagram semantics use Green `#5FAE7F` (accepted / result) and Red `#D08484`
(rejected / error) with the tints `#E9F7EF` and `#FDEEEE`.

## Clear space and minimum size

Keep clear space around the lockup equal to the icon's corner radius
(20 % of the icon height). Do not use the icon below 32 px or the lockup
below 120 px wide; use the mark alone below that.
