"""Generate the Chathuram chess pieces from the logo pawn.

Every piece uses the logo pawn's own body and orange collar, taken from
brand-kit/logo/chathuram-pawn.svg (cut out of brand-kit/source/Chathuram-logo.ai
by tools/crop_logo.py). Only the heads differ. The pieces have no faces: the
pawn's head is the logo head with its smile filled in. Only the logo keeps
the smile.

Run from the repository root:  python3 tools/pieces.py
"""
import math
import os
import re

DARK = "#231f20"
LOGO_PAWN = os.path.join("brand-kit", "logo", "chathuram-pawn.svg")
VIEWBOX = "331 334 27 55.5"
# where a piece meets the ground (bottom of the body), used to stand pieces on squares
ANCHOR = (344.0, 386.6)
ORDER = ["pawn", "knight", "bishop", "rook", "queen"]


def _sample(d, n=24):
    toks = re.findall(r"[MLCZ]|-?\d+\.?\d*", d)
    pts, cur, i = [], None, 0
    while i < len(toks):
        t = toks[i]
        if t in "ML":
            cur = (float(toks[i + 1]), float(toks[i + 2])); pts.append(cur); i += 3
        elif t == "C":
            p = [cur] + [(float(toks[i + 1 + 2 * k]), float(toks[i + 2 + 2 * k])) for k in range(3)]
            for k in range(1, n + 1):
                u = k / n
                w = ((1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3)
                pts.append((sum(w[j] * p[j][0] for j in range(4)), sum(w[j] * p[j][1] for j in range(4))))
            cur = p[3]; i += 7
        else:
            i += 1
    return pts


def _hull(points):
    pts = sorted(set(points))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _smooth_closed(points, n=40):
    """A smooth closed path through points resampled evenly along the outline."""
    ring = points + [points[0]]
    lengths = [0.0]
    for a, b in zip(ring, ring[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    res = []
    for k in range(n):
        t = lengths[-1] * k / n
        j = max(i for i in range(len(lengths)) if lengths[i] <= t)
        a, b = ring[j], ring[j + 1]
        f = (t - lengths[j]) / max(1e-9, lengths[j + 1] - lengths[j])
        res.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    d = f"M {res[0][0]:.3f} {res[0][1]:.3f} "
    for i in range(n):
        p0, p1, p2, p3 = res[i - 1], res[i], res[(i + 1) % n], res[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C {c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p2[0]:.3f} {p2[1]:.3f} "
    return d + "Z"


def logo_parts():
    svg = open(LOGO_PAWN).read()
    body, collar, head = re.findall(r'<path\b[^>]*/>', svg)
    d = lambda el: re.search(r'\sd="([^"]*)"', el).group(1)
    # the logo head with its smile notch filled in
    plain_head = _smooth_closed(_hull(_sample(d(head))))
    return d(body), d(collar), plain_head


def heads(plain_head, fill, mask_prefix):
    m = f"{mask_prefix}bishop-slit"
    return {
        "pawn": f'<path fill="{fill}" d="{plain_head}"/>',
        # a soft horse head facing right
        "knight": (f'<path fill="{fill}" d="M 338.4 358.8 C 337.2 354.6 336.9 349.6 338 345.4 C 338.6 343.2 339.2 341.4 339.6 339.2 '
                   'C 339.8 338.2 340.8 337.9 341.4 338.7 L 342.8 340.7 C 346.6 341 350.6 343.6 353.4 347.6 C 354.6 349.3 354.6 351.2 353.2 352.2 '
                   'C 351.8 353.2 349.8 352.8 348.2 352.1 C 347.4 353.8 347.4 356.2 348.4 358.8 Z"/>'),
        # a tall soft mitre with a small ball on top and the classic slit
        "bishop": (f'<mask id="{m}" maskUnits="userSpaceOnUse" x="320" y="320" width="50" height="50">'
                   '<rect x="320" y="320" width="50" height="50" fill="#fff"/>'
                   '<path d="M 349.6 344.6 L 344.8 349.6" stroke="#000" stroke-width="1.5" stroke-linecap="round"/></mask>'
                   f'<g mask="url(#{m})"><circle cx="344.4" cy="337.6" r="2.1" fill="{fill}"/>'
                   f'<path fill="{fill}" d="M 344.4 340.3 C 349.6 343.4 352.6 348.6 351.6 353.4 C 351 356.8 348 358.8 344.4 358.8 '
                   'C 340.8 358.8 337.8 356.8 337.2 353.4 C 336.2 348.6 339.2 343.4 344.4 340.3 Z"/></g>'),
        # a soft tower top with rounded battlements, leaning slightly like the pawn's head
        "rook": (f'<g transform="rotate(-4 344 350)"><path fill="{fill}" d="M 337.4 358.6 C 336.6 358.6 336.2 358 336.3 357.2 '
                 'L 337.2 345.6 C 337.3 344.8 337.8 344.4 338.6 344.4 L 338.6 341.6 C 338.6 340.8 339.1 340.3 339.9 340.3 L 341.6 340.3 '
                 'C 342.4 340.3 342.9 340.8 342.9 341.6 L 342.9 343.2 L 344.9 343.2 L 344.9 341.6 C 344.9 340.8 345.4 340.3 346.2 340.3 '
                 'L 347.9 340.3 C 348.7 340.3 349.2 340.8 349.2 341.6 L 349.2 344.4 C 350 344.4 350.5 344.8 350.6 345.6 L 351.5 357.2 '
                 'C 351.6 358 351.2 358.6 350.4 358.6 Z"/></g>'),
        # the round head with a soft crown of rounded points
        "queen": (f'<path fill="{fill}" d="M 337.6 347.2 L 336.6 340.6 C 336.5 339.9 337.3 339.5 337.8 340 L 340.7 343 L 342.9 338.2 '
                  'C 343.2 337.5 344.2 337.5 344.5 338.2 L 346.4 342.8 L 349.6 339.7 C 350.1 339.2 350.9 339.6 350.8 340.3 L 349.9 347.2 Z"/>'
                  f'<circle cx="337" cy="339.6" r="1.25" fill="{fill}"/><circle cx="343.7" cy="337.3" r="1.25" fill="{fill}"/>'
                  f'<circle cx="350.4" cy="339.3" r="1.25" fill="{fill}"/><ellipse cx="343.8" cy="352.6" rx="7.3" ry="6.4" fill="{fill}"/>'),
    }


def piece_shapes(name, fill, mask_prefix, body, collar, plain_head):
    return (f'<path fill="{fill}" d="{body}"/><path fill="#f15a29" d="{collar}"/>'
            + heads(plain_head, fill, mask_prefix)[name])


def main():
    body, collar, plain_head = logo_parts()
    out = os.path.join("source", "images", "brand", "pieces")
    os.makedirs(out, exist_ok=True)
    for name in ORDER:
        for suffix, fill, prefix in (("", DARK, "d-"), ("-light", "#ffffff", "l-")):
            label = f"Chathuram {name}"
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" role="img" aria-label="{label}">\n'
                   f'  <title>{label}</title>\n  {piece_shapes(name, fill, prefix, body, collar, plain_head)}\n</svg>\n')
            open(os.path.join(out, f"{name}{suffix}.svg"), "w").write(svg)

    # inline groups for the pawn-path animation (scaled to the path)
    scale = 2.75
    tx, ty = -ANCHOR[0] * scale, -ANCHOR[1] * scale
    groups = []
    for name in ORDER:
        current = " is-current" if name == "pawn" else ""
        shapes = piece_shapes(name, "currentColor", "pp-", body, collar, plain_head)
        groups.append(f'          <g class="pp-piece{current}" data-piece="{name}">{shapes}</g>')
    partial = (
        "<!-- generated by tools/pieces.py: do not edit by hand -->\n"
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
