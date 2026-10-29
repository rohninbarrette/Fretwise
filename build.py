#!/usr/bin/env python3
"""Build the installable web app into docs/ (the folder GitHub Pages serves).

fretwise.html is the single source file (it is also published as a claude.ai artifact,
which adds its own page wrapper). This script wraps it in a full HTML page with the
tags iPhones need for "Add to Home Screen", and writes the manifest, service worker
and icons next to it.

Run:  python3 build.py
"""
import hashlib, json, os, re, struct, zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, 'docs')
BG_LIGHT, BG_DARK, ACCENT = '#eceee9', '#121513', '#17655d'


# ---------- icons (drawn here so no image tools are needed) ----------
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def png(path, size, pixels):
    raw = b''.join(b'\x00' + bytes(row) for row in pixels)
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def icon(size, scale=1.0):
    """A chord box: nut, frets, six strings and three finger dots, on the app's teal.
    scale < 1 shrinks the drawing toward the centre (for the maskable icon's safe zone)."""
    bg, white, root = hex_rgb(ACCENT), (250, 251, 248), (242, 193, 78)
    S = size
    def u(v):  # unit square (0..1) -> pixels, scaled about the centre
        return (0.5 + (v - 0.5) * scale) * S
    rects, circles = [], []
    x0, x1 = 0.26, 0.74
    rects.append((u(x0) - S * 0.012 * scale, u(0.215), u(x1) + S * 0.012 * scale, u(0.262), white))      # nut
    for y in (0.40, 0.56, 0.72):
        rects.append((u(x0), u(y) - S * 0.006 * scale, u(x1), u(y) + S * 0.006 * scale, white))           # frets
    for i in range(6):
        x = x0 + (x1 - x0) * i / 5
        w = S * (0.011 - i * 0.0012) * scale
        rects.append((u(x) - w, u(0.24), u(x) + w, u(0.80), white))                                     # strings
    r = S * 0.052 * scale
    for (i, fy, col) in ((1, 0.48, root), (3, 0.48, white), (4, 0.32, white)):
        circles.append((u(x0 + (x1 - x0) * i / 5), u(fy), r, col))

    def rect_cov(px, py, rc):
        ax0, ay0, ax1, ay1, _ = rc
        w = max(0.0, min(px + 1, ax1) - max(px, ax0))
        h = max(0.0, min(py + 1, ay1) - max(py, ay0))
        return w * h

    def circ_cov(px, py, c):
        cx, cy, rr, _ = c
        dx, dy = px + 0.5 - cx, py + 0.5 - cy
        d = (dx * dx + dy * dy) ** 0.5
        if d < rr - 0.8:
            return 1.0
        if d > rr + 0.8:
            return 0.0
        n, hit = 4, 0
        for sy in range(n):
            for sx in range(n):
                ex, ey = px + (sx + 0.5) / n - cx, py + (sy + 0.5) / n - cy
                hit += ex * ex + ey * ey <= rr * rr
        return hit / (n * n)

    rows = []
    for py in range(S):
        row = []
        for px in range(S):
            c = list(bg)
            for shape in rects:
                a = rect_cov(px, py, shape)
                if a:
                    c = [c[k] + (shape[4][k] - c[k]) * a for k in range(3)]
            for shape in circles:
                # a teal ring around each dot keeps it from merging into the string under it
                ring = (shape[0], shape[1], shape[2] * 1.28, bg)
                for s2 in (ring, shape):
                    a = circ_cov(px, py, s2)
                    if a:
                        c = [c[k] + (s2[3][k] - c[k]) * a for k in range(3)]
            row.extend(int(round(v)) for v in c)
        rows.append(row)
    return rows


def build_icons():
    out = os.path.join(DOCS, 'icons')
    os.makedirs(out, exist_ok=True)
    for name, size, scale in (('icon-192.png', 192, 1.0), ('icon-512.png', 512, 1.0),
                              ('icon-maskable-512.png', 512, 0.8), ('apple-touch-icon.png', 180, 1.0)):
        path = os.path.join(out, name)
        if not os.path.exists(path):
            png(path, size, icon(size, scale))
            print('  drew', name)


# ---------- page ----------
def build_page():
    src = open(os.path.join(ROOT, 'fretwise.html'), encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', src).group(1)
    body_at = src.index('<div class="wrap">')
    head = src[:body_at]
    head = re.sub(r'<title>.*?</title>\n?', '', head)
    head = re.sub(r'<meta name="claude:[^>]*>\n?', '', head)
    body = src[body_at:]
    page = f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Guitar chord finder, chord library, scales, circle of fifths, song sketchpad, tuner and practice tools.">
<meta name="theme-color" content="{BG_LIGHT}" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="{BG_DARK}" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{title}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" href="icons/icon-192.png">
<style>html,body{{margin:0;padding:0}}</style>
{head.strip()}
</head>
<body>
{body.strip()}
<script>if ('serviceWorker' in navigator) addEventListener('load', () => navigator.serviceWorker.register('sw.js'));</script>
</body>
</html>
'''
    with open(os.path.join(DOCS, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    return page


def build_manifest():
    m = {
        'name': 'Fretwise', 'short_name': 'Fretwise',
        'description': 'Guitar chord finder, chord library, scales, circle of fifths, song sketchpad, tuner and practice tools.',
        'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'any',
        'background_color': BG_LIGHT, 'theme_color': BG_LIGHT,
        'icons': [
            {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
            {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }
    with open(os.path.join(DOCS, 'manifest.webmanifest'), 'w') as f:
        json.dump(m, f, indent=2)


SW = '''// Offline support. The cache name changes with every build, so phones pick up new versions.
const CACHE = 'fretwise-__VERSION__';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('fretwise-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (req.mode === 'navigate'){
    // the page: try the network first (so updates show up), fall back to the saved copy after 3 s or offline
    const net = fetch(req).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); return res; });
    const slow = new Promise(r => setTimeout(r, 3000)).then(() => caches.match('index.html'));
    e.respondWith(Promise.race([net.catch(() => caches.match('index.html')), slow.then(hit => hit || net)]));
    return;
  }
  // icons, manifest and Google Fonts: cache first, then keep a copy
  if (url.origin === location.origin || url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com'){
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok || res.type === 'opaque'){ const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    })));
  }
});
'''


def build_sw(page):
    version = hashlib.sha256(page.encode('utf-8')).hexdigest()[:10]
    with open(os.path.join(DOCS, 'sw.js'), 'w') as f:
        f.write(SW.replace('__VERSION__', version))
    return version


if __name__ == '__main__':
    os.makedirs(DOCS, exist_ok=True)
    build_icons()
    page = build_page()
    build_manifest()
    v = build_sw(page)
    open(os.path.join(DOCS, '.nojekyll'), 'w').close()
    print(f'Built docs/ (version {v})')
