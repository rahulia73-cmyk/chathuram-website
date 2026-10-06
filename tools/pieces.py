"""Generate the Chathuram chess-piece mascots.

Every piece shares the mascot's look (black body, orange collar, a white
smile notch) and sits on a base whose shape shows how the piece moves:
  pawn   - a one-way diagonal sweep (pawns capture diagonally forward)
  bishop - a sweep down both diagonals
  rook   - a straight, square-edged slab
  queen  - a flat slab with diagonal wings (straight + diagonal)
  knight - an L-shaped step

Run from the repository root:  python3 tools/pieces.py
"""
import os

ORANGE = "#f1592a"
VIEWBOX = "-130 0 520 540"
# where the piece meets the ground, used to stand pieces on squares
ANCHOR = (150, 512)

PIECES = {
    "pawn": {
        "head": '<circle cx="146" cy="133" r="72"/>',
        "cuts": ['<path d="M171 137 q24 10 52 2" fill="none" stroke-width="7" stroke-linecap="round"/>'],
        "collar": "M93 223 Q158 189 227 201 L230 231 Q161 221 97 249 Z",
        "body": "M113 261 Q161 247 213 253 Q221 358 248 468 L53 408 Q101 343 113 261 Z",
        "base": "M-120 522 Q-60 497 -12 469 Q3 433 48 425 Q128 419 183 469 Q203 485 243 493 L223 505 Q63 493 -57 515 Q-100 521 -120 522 Z",
    },
    "bishop": {
        "head": '<circle cx="150" cy="40" r="17"/><path d="M150 62 C208 100 220 160 188 206 L112 206 C80 160 92 100 150 62 Z"/>',
        "cuts": ['<path d="M128 112 L186 152" fill="none" stroke-width="9" stroke-linecap="round"/>'],
        "collar": "M95 220 Q150 196 205 220 L207 248 Q150 226 93 248 Z",
        "body": "M112 262 Q150 252 188 262 Q205 370 250 490 L50 490 Q95 370 112 262 Z",
        "base": "M-60 524 Q20 496 78 470 Q100 430 150 424 Q200 430 222 470 Q280 496 360 524 Q150 500 -60 524 Z",
    },
    "rook": {
        "head": '<path d="M82 58 H114 V84 H134 V58 H166 V84 H186 V58 H218 V182 H82 Z"/>',
        "cuts": ['<path d="M160 136 q18 8 40 1" fill="none" stroke-width="8" stroke-linecap="round"/>'],
        "collar": "M76 194 H224 V222 H76 Z",
        "body": "M98 238 H202 L216 490 H84 Z",
        "base": "M36 448 H264 V512 H36 Z",
    },
    "queen": {
        "head": ('<path d="M86 112 L74 38 L112 78 L131 22 L150 70 L169 22 L188 78 L226 38 L214 112 Z"/>'
                 '<circle cx="74" cy="34" r="10"/><circle cx="131" cy="18" r="10"/><circle cx="169" cy="18" r="10"/><circle cx="226" cy="34" r="10"/>'
                 '<circle cx="150" cy="138" r="54"/>'),
        "cuts": ['<path d="M168 142 q20 8 40 1" fill="none" stroke-width="7" stroke-linecap="round"/>',
                 '<path d="M90 104 H210" fill="none" stroke-width="7"/>'],
        "collar": "M88 204 Q150 176 212 204 L214 232 Q150 208 86 232 Z",
        "body": "M110 248 Q150 238 190 248 Q206 360 252 490 L48 490 Q94 360 110 248 Z",
        "base": "M-40 520 L56 468 V452 H244 V468 L340 520 Z",
    },
    "knight": {
        "head": ('<path d="M104 232 C92 160 96 92 116 50 L124 18 L146 46 C186 58 222 94 242 128 '
                 'Q250 146 238 160 Q222 170 198 162 C192 186 194 206 198 232 Z"/>'),
        "cuts": ['<circle cx="160" cy="84" r="8"/>',
                 '<path d="M206 146 q14 6 32 0" fill="none" stroke-width="7" stroke-linecap="round"/>'],
        "collar": "M90 230 Q150 206 210 226 L212 254 Q150 232 88 258 Z",
        "body": "M106 272 Q150 262 198 272 Q210 360 250 490 L50 490 Q96 360 106 272 Z",
        "base": "M0 512 V472 H150 V436 H300 V512 Z",
    },
}

ORDER = ["pawn", "knight", "bishop", "rook", "queen"]


def piece_group(name, fill, prefix):
    """Shapes for one piece. Mask ids are prefixed so several pieces can share a page."""
    p = PIECES[name]
    head_id, body_id = f"{prefix}{name}-h", f"{prefix}{name}-b"
    cuts = "".join(c.replace("<path", '<path stroke="#000"').replace("<circle", '<circle fill="#000"') for c in p["cuts"])
    masks = (
        f'<mask id="{head_id}" maskUnits="userSpaceOnUse" x="-200" y="-40" width="700" height="620">'
        f'<rect x="-200" y="-40" width="700" height="620" fill="#fff"/>{cuts}</mask>'
        f'<mask id="{body_id}" maskUnits="userSpaceOnUse" x="-200" y="-40" width="700" height="620">'
        f'<rect x="-200" y="-40" width="700" height="620" fill="#fff"/>'
        f'<path d="{p["base"]}" fill="#000" stroke="#000" stroke-width="12" stroke-linejoin="round"/></mask>'
    )
    shapes = (
        f'<g fill="{fill}" mask="url(#{head_id})">{p["head"]}</g>'
        f'<path d="{p["collar"]}" fill="{ORANGE}"/>'
        f'<path d="{p["body"]}" fill="{fill}" mask="url(#{body_id})"/>'
        f'<path d="{p["base"]}" fill="{fill}"/>'
    )
    return masks, shapes


def svg_file(name, fill, prefix):
    masks, shapes = piece_group(name, fill, prefix)
    label = f"Chathuram {name} mascot"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" role="img" aria-label="{label}">\n'
            f'  <title>{label}</title>\n  <defs>{masks}</defs>\n  {shapes}\n</svg>\n')


def main():
    out = os.path.join("source", "images", "brand", "pieces")
    os.makedirs(out, exist_ok=True)
    for name in ORDER:
        with open(os.path.join(out, f"{name}.svg"), "w") as f:
            f.write(svg_file(name, "#000", "d-"))
        with open(os.path.join(out, f"{name}-light.svg"), "w") as f:
            f.write(svg_file(name, "#fff", "l-"))

    # inline groups for the pawn-path animation (scaled to the path)
    scale = 0.31
    tx, ty = -ANCHOR[0] * scale, -ANCHOR[1] * scale
    defs, groups = [], []
    for name in ORDER:
        masks, shapes = piece_group(name, "currentColor", "pp-")
        defs.append(masks)
        current = " is-current" if name == "pawn" else ""
        groups.append(f'          <g class="pp-piece{current}" data-piece="{name}">{shapes}</g>')
    partial = (
        "<!-- generated by tools/pieces.py: do not edit by hand -->\n"
        f'      <defs>{"".join(defs)}</defs>\n'
        '      <g class="pp-pawn">\n'
        '        <g class="pp-spin">\n'
        f'          <g transform="translate({tx:.1f} {ty:.1f}) scale({scale})">\n'
        + "\n".join(groups) + "\n"
        "          </g>\n        </g>\n      </g>\n"
    )
    with open(os.path.join("source", "partials", "blocks", "pp-pieces.htm"), "w") as f:
        f.write(partial)


if __name__ == "__main__":
    main()
