"""Cut a region out of a flat SVG (one <path> per shape) by each shape's bounding box."""
import re, sys, json

def rgb_to_hex(m):
    r, g, b = (round(float(x) * 2.55) for x in m.groups())
    return f"#{r:02x}{g:02x}{b:02x}"

def load(path):
    s = open(path).read()
    return re.findall(r'<path\b[^>]*/>', s)

def bbox(el):
    d = re.search(r'\sd="([^"]*)"', el).group(1)
    nums = [float(n) for n in re.findall(r'-?\d+\.?\d*(?:e-?\d+)?', d)]
    pts = list(zip(nums[0::2], nums[1::2]))
    t = re.search(r'transform="matrix\(([^)]*)\)"', el)
    if t:
        a, b, c, dd, e, f = (float(x) for x in t.group(1).split(','))
        pts = [(a * x + c * y + e, b * x + dd * y + f) for x, y in pts]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

def crop(paths, rect, drop_fills=(), pad=2.0):
    x0, y0, x1, y1 = rect
    keep = []
    for el in paths:
        bx0, by0, bx1, by1 = bbox(el)
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            el2 = re.sub(r'rgb\(([\d.]+)%,\s*([\d.]+)%,\s*([\d.]+)%\)', rgb_to_hex, el)
            if any(f'fill="{c}"' in el2 for c in drop_fills):
                continue
            keep.append((el2, (bx0, by0, bx1, by1)))
    ux0 = min(b[0] for _, b in keep) - pad; uy0 = min(b[1] for _, b in keep) - pad
    ux1 = max(b[2] for _, b in keep) + pad; uy1 = max(b[3] for _, b in keep) + pad
    return [k for k, _ in keep], (ux0, uy0, ux1 - ux0, uy1 - uy0)

def write(path, els, vb, title, recolor=None):
    body = "\n".join(els)
    if recolor:
        for a, b in recolor.items():
            body = body.replace(a, b)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.2f} {vb[1]:.2f} {vb[2]:.2f} {vb[3]:.2f}" '
           f'role="img" aria-label="{title}">\n<title>{title}</title>\n{body}\n</svg>\n')
    open(path, "w").write(svg)

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    paths = load(src)
    jobs = json.loads(sys.argv[3])
    for name, spec in jobs.items():
        els, vb = crop(paths, spec["rect"], tuple(spec.get("drop", [])))
        write(f"{out}/{name}.svg", els, vb, spec["title"], spec.get("recolor"))
        print(name, len(els), "shapes", [round(v, 1) for v in vb])
