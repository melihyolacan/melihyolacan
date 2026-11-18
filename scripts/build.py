"""Generates the profile README graphics (light + dark) and the avatar."""
import datetime, json, math, os, sys, urllib.request

OUT = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = json.load(open(os.path.join(ROOT, "data", "static.json")))
LOGIN = "melihyolacan"


def fetch_calendar():
    """Contribution calendar for the last 12 months (includes anonymized private work)."""
    q = ('query{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{date contributionCount}}}}}}' % LOGIN)
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"],
                                          "User-Agent": "profile-readme-build"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    return d["data"]["user"]["contributionsCollection"]["contributionCalendar"]


CAL = fetch_calendar()
DAYS = [(datetime.date.fromisoformat(x["date"]), x["contributionCount"]) for w in CAL["weeks"] for x in w["contributionDays"]]
WEEKS = [(datetime.date.fromisoformat(w["contributionDays"][0]["date"]), sum(x["contributionCount"] for x in w["contributionDays"])) for w in CAL["weeks"]]
TOTAL = CAL["totalContributions"]
os.makedirs(OUT, exist_ok=True)

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "dark": dict(surface="#0d1117", panel="#101614", panel_ink="#EFE9DC", panel_muted="#9AA398", panel_line="#EFE9DC",
                 ink="#ECE6DA", muted="#98A096", rule="#ECE6DA", rule_o="0.16", accent="#F0764A"),
    "light": dict(surface="#ffffff", panel="#F3EEE3", panel_ink="#161B18", panel_muted="#5C665E", panel_line="#161B18",
                  ink="#1A1F1C", muted="#5C665E", rule="#1A1F1C", rule_o="0.18", accent="#C4441C"),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ring(cx, cy, R, k, n=140):
    """One closed contour line; phases drift with k so rings are not parallel."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = R * (1 + 0.085 * math.sin(2 * t + 0.6 + k * 0.11)
                 + 0.055 * math.sin(3 * t + 1.9 - k * 0.17)
                 + 0.03 * math.sin(5 * t + 0.3 + k * 0.23))
        pts.append((cx + r * math.cos(t) * 1.18, cy + r * math.sin(t)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return d


def contours(cx, cy, radii, color, accent, accent_idx, animate=True, base_o=0.34, width=1.1):
    out = []
    for k, R in enumerate(radii):
        is_acc = k == accent_idx
        col = accent if is_acc else color
        op = 0.95 if is_acc else max(0.10, base_o - k * 0.012)
        cls = f' class="c" style="animation-delay:{k * 0.07:.2f}s"' if animate else ""
        out.append(f'<path d="{ring(cx, cy, R, k)}" pathLength="1" fill="none" stroke="{col}" '
                   f'stroke-opacity="{op:.2f}" stroke-width="{1.5 if is_acc else width}"{cls}/>')
    return "\n".join(out)


ANIM = """
  .c{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.8s cubic-bezier(.22,1,.36,1) forwards}
  .pulse{transform-box:fill-box;transform-origin:center;animation:pulse 3.2s ease-out infinite}
  @keyframes draw{to{stroke-dashoffset:0}}
  @keyframes pulse{0%{transform:scale(1);opacity:.55}70%,100%{transform:scale(3.4);opacity:0}}
  @media (prefers-reduced-motion:reduce){.c{animation:none;stroke-dashoffset:0}.pulse{animation:none;opacity:0}}
"""


def header(t):
    W, H = 840, 300
    cx, cy = 664, 150
    radii = [14 + i * 15.5 for i in range(17)]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Melih Yolaçan, product engineer in Istanbul">
<style>{ANIM}</style>
<defs>
  <clipPath id="p"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0.56" stop-color="{t['panel']}" stop-opacity="1"/>
    <stop offset="0.75" stop-color="{t['panel']}" stop-opacity="0"/>
  </linearGradient>
</defs>
<g clip-path="url(#p)">
  <rect width="{W}" height="{H}" fill="{t['panel']}"/>
  {contours(cx, cy, radii, t['panel_line'], t['accent'], 5)}
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  <circle class="pulse" cx="{cx}" cy="{cy}" r="5" fill="{t['accent']}"/>
  <circle cx="{cx}" cy="{cy}" r="4.5" fill="{t['accent']}"/>
  <text x="{cx + 14}" y="{cy + 4}" font-family="{MONO}" font-size="11.5" letter-spacing="0.6" fill="{t['panel_ink']}">41.01° N  28.98° E</text>
</g>
<text x="48" y="74" font-family="{MONO}" font-size="12.5" letter-spacing="2.4" fill="{t['accent']}">PRODUCT ENGINEER  ·  ISTANBUL</text>
<text x="46" y="143" font-family="{SERIF}" font-size="58" letter-spacing="-1.2" fill="{t['panel_ink']}">Melih Yolaçan</text>
<text font-family="{SANS}" font-size="18" fill="{t['panel_ink']}" fill-opacity="0.86">
  <tspan x="48" y="186">AI-native products, built end to end:</tspan>
  <tspan x="48" y="211">from the model pipeline to the shipped interface.</tspan>
</text>
<line x1="48" y1="242" x2="88" y2="242" stroke="{t['accent']}" stroke-width="2"/>
<text x="48" y="266" font-family="{MONO}" font-size="11.5" letter-spacing="1.2" fill="{t['panel_muted']}">SINCE {STATIC['since']}   ·   {STATIC['repos'] // 10 * 10}+ REPOS   ·   {TOTAL / 1000:.1f}K CONTRIBUTIONS / YEAR</text>
</svg>'''


def label(t, num, text, y=22):
    return f'''<text x="0" y="{y}" font-family="{MONO}" font-size="12.5" letter-spacing="2.4" fill="{t['accent']}">{num}</text>
<text x="34" y="{y}" font-family="{MONO}" font-size="12.5" letter-spacing="2.4" fill="{t['muted']}">{esc(text)}</text>
<line x1="0" y1="{y + 16}" x2="840" y2="{y + 16}" stroke="{t['rule']}" stroke-opacity="{t['rule_o']}"/>'''


def row(t, y, name, desc_lines, stack, size=30, link=None, rule=True):
    """A ledger row: serif name on the left, description and stack on the right."""
    s = f'<text x="0" y="{y + 36}" font-family="{SERIF}" font-size="{size}" letter-spacing="-0.4" fill="{t["ink"]}">{esc(name)}</text>\n'
    if link:
        s += f'<text x="1" y="{y + 60}" font-family="{MONO}" font-size="12" letter-spacing="0.4" fill="{t["accent"]}">{esc(link)} ↗</text>\n'
    yy = y + 27
    for ln in desc_lines:
        s += f'<text x="268" y="{yy}" font-family="{SANS}" font-size="16" fill="{t["ink"]}" fill-opacity="0.9">{esc(ln)}</text>\n'
        yy += 23
    s += f'<text x="268" y="{yy + 1}" font-family="{MONO}" font-size="12" letter-spacing="0.5" fill="{t["muted"]}">{esc(stack)}</text>\n'
    h = (yy + 1 - y) + 24
    if rule:
        s += f'<line x1="0" y1="{y + h}" x2="840" y2="{y + h}" stroke="{t["rule"]}" stroke-opacity="{t["rule_o"]}"/>\n'
    return s, h


def svg(W, H, body, aria):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(aria)}">\n{body}\n</svg>'


def product(t, num_label, name, desc, stack, link=None):
    body = ""
    y = 0
    if num_label:
        body += label(t, *num_label)
        y = 44
    r, h = row(t, y, name, desc, stack, size=34, link=link)
    return svg(840, y + h + 1, body + r, name)


SECTORS = [
    ("E-commerce", ["Multi-store commerce platform where AI designs", "and ships each storefront."], "GO  /  NEXT.JS  /  POSTGRESQL"),
    ("Community", ["Community and mentoring platform with", "memberships, courses and chat."], "GO  /  REACT"),
    ("Sports technology", ["Multilingual product site published in 16 languages."], "NEXT.JS"),
    ("Consumer AI", ["Bilingual AI-powered consumer app with payments."], "NEXT.JS  /  HONO  /  BUN"),
    ("Client work", ["Websites, CRMs and internal tools for client businesses."], "NEXT.JS  /  TYPESCRIPT"),
]


def sectors(t):
    body = label(t, "02", "OTHER WORK, BY SECTOR")
    y = 44
    for i, (n, d, s) in enumerate(SECTORS):
        r, h = row(t, y, n, d, s, size=24, rule=i < len(SECTORS) - 1)
        body += r
        y += h
    return svg(840, y, body, "Other work, by sector")


def activity(t):
    """Weekly contributions over the last 12 months, drawn as an elevation profile."""
    W = 840
    active = sum(1 for _, c in DAYS if c)
    best_day, best = max(DAYS, key=lambda x: x[1])
    streak = cur = 0
    for _, c in DAYS:
        cur = cur + 1 if c else 0
        streak = max(streak, cur)
    body = label(t, "03", "ACTIVITY, LAST 12 MONTHS")
    stats = [(0, f"{TOTAL:,}", "CONTRIBUTIONS", 60),
             (372, f"{active}", "ACTIVE DAYS", 34),
             (522, f"{best}", "BEST DAY · " + best_day.strftime("%b %-d").upper(), 34),
             (700, f"{streak}", "DAY STREAK", 34)]
    for x, num, cap, size in stats:
        body += f'<text x="{x}" y="108" font-family="{SERIF}" font-size="{size}" letter-spacing="-0.5" fill="{t["ink"]}">{num}</text>\n'
        body += f'<text x="{x + 1}" y="132" font-family="{MONO}" font-size="11.5" letter-spacing="1.4" fill="{t["muted"]}">{cap}</text>\n'
    top, base = 172, 322
    vals = [v for _, v in WEEKS]
    peak = max(vals)
    step = 10 ** (len(str(peak)) - 1)
    step = step // 2 if peak / step < 3 else step
    ymax = max(step, math.ceil(peak / step) * step)
    X = lambda i: i * W / (len(vals) - 1)
    Y = lambda v: base - v / ymax * (base - top)
    for g in range(step, ymax + 1, step):
        if g > peak * 1.02:
            break
        body += f'<line x1="0" y1="{Y(g):.1f}" x2="{W}" y2="{Y(g):.1f}" stroke="{t["rule"]}" stroke-opacity="0.09"/>\n'
        body += f'<text x="0" y="{Y(g) - 5:.1f}" font-family="{MONO}" font-size="10.5" fill="{t["muted"]}">{g:,}</text>\n'
    pts = " L".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
    body += f'<defs><linearGradient id="a" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{t["accent"]}" stop-opacity="0.34"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0.02"/></linearGradient></defs>\n'
    body += f'<path d="M0,{base} L{pts} L{W},{base} Z" fill="url(#a)"/>\n'
    body += f'<path class="ln" pathLength="1" d="M{pts}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>\n'
    body += f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{t["rule"]}" stroke-opacity="0.32"/>\n'
    last_month, last_x = None, -99
    for i, (d, _) in enumerate(WEEKS):
        m = (d + datetime.timedelta(days=6)).month
        if m != last_month and last_month is not None and X(i) - last_x > 44 and X(i) < W - 20:
            body += f'<line x1="{X(i):.1f}" y1="{base}" x2="{X(i):.1f}" y2="{base + 5}" stroke="{t["rule"]}" stroke-opacity="0.32"/>\n'
            body += f'<text x="{X(i):.1f}" y="{base + 20}" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="0.8" fill="{t["muted"]}">{(d + datetime.timedelta(days=6)).strftime("%b").upper()}</text>\n'
            last_x = X(i)
        last_month = m
    pi = vals.index(peak)
    px, py = X(pi), Y(peak)
    anchor, lx = ("end", px - 12) if px > W / 2 else ("start", px + 12)
    body += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{t["accent"]}" stroke="{t["surface"]}" stroke-width="2"/>\n'
    body += f'<text x="{lx:.1f}" y="{py - 4:.1f}" text-anchor="{anchor}" font-family="{SANS}" font-size="13.5" fill="{t["ink"]}">{peak:,} in one week</text>\n'
    style = ('<style>.ln{stroke-dasharray:1;stroke-dashoffset:1;animation:d 2.2s cubic-bezier(.22,1,.36,1) .2s forwards}'
             '@keyframes d{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.ln{animation:none;stroke-dashoffset:0}}</style>\n')
    return svg(W, base + 30, style + body, "Activity over the last 12 months")


STACK = [
    ("LANGUAGES", "TypeScript   Go   Python   Swift"),
    ("PRODUCT", "Next.js   React   Expo / React Native   Hono   Bun   PostgreSQL"),
    ("AI", "LLM agents and tool use   Image and video pipelines   Self-hosted GPU inference"),
    ("SHIPPING", "Vercel   Railway   Cloudflare Workers and R2   Stripe"),
]


def stack(t):
    body = label(t, "04", "WHAT I WORK WITH")
    y = 44
    for i, (k, v) in enumerate(STACK):
        body += f'<text x="0" y="{y + 27}" font-family="{MONO}" font-size="12" letter-spacing="1.8" fill="{t["muted"]}">{k}</text>\n'
        parts = v.split("   ")
        sep = f'</tspan><tspan fill="{t["accent"]}" fill-opacity="0.9" dx="9">/</tspan><tspan dx="9">'
        body += f'<text x="150" y="{y + 28}" font-family="{SANS}" font-size="15.5" fill="{t["ink"]}"><tspan>{sep.join(esc(p) for p in parts)}</tspan></text>\n'
        y += 46
        if i < len(STACK) - 1:
            body += f'<line x1="0" y1="{y}" x2="840" y2="{y}" stroke="{t["rule"]}" stroke-opacity="{t["rule_o"]}"/>\n'
    return svg(840, y, body, "What I work with")


PRINCIPLES = [
    ("1", ["One person,", "whole product."], ["Research, design, backend,", "frontend and deployment."]),
    ("2", ["By hand first,", "then automated."], ["Do it manually, measure it,", "and only then automate it."]),
    ("3", ["Shipped", "behind gates."], ["Tests, visual checks and real-data", "verification before going live."]),
]


def principles(t):
    body = label(t, "05", "HOW I WORK")
    for i, (n, head, sub) in enumerate(PRINCIPLES):
        x = i * 290
        body += f'<text x="{x}" y="100" font-family="{SERIF}" font-size="60" fill="{t["accent"]}">{n}</text>\n'
        yy = 140
        for ln in head:
            body += f'<text x="{x}" y="{yy}" font-family="{SERIF}" font-size="23" letter-spacing="-0.2" fill="{t["ink"]}">{esc(ln)}</text>\n'
            yy += 28
        yy += 2
        for ln in sub:
            body += f'<text x="{x}" y="{yy}" font-family="{SANS}" font-size="14" fill="{t["muted"]}">{esc(ln)}</text>\n'
            yy += 20
    return svg(840, 240, body, "How I work")


def avatar():
    t = THEMES["dark"]
    S = 800
    radii = [30 + i * 30 for i in range(22)]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">
<defs><radialGradient id="g" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="{t['panel']}" stop-opacity="0.96"/>
  <stop offset="0.52" stop-color="{t['panel']}" stop-opacity="0.9"/>
  <stop offset="1" stop-color="{t['panel']}" stop-opacity="0"/>
</radialGradient></defs>
<rect width="{S}" height="{S}" fill="{t['panel']}"/>
{contours(430, 410, radii, t['panel_line'], t['accent'], 9, animate=False, base_o=0.42, width=2)}
<circle cx="400" cy="400" r="300" fill="url(#g)"/>
<text x="392" y="492" text-anchor="middle" font-family="{SERIF}" font-size="280" letter-spacing="-2" fill="{t['panel_ink']}">MY</text>
<circle cx="622" cy="476" r="17" fill="{t['accent']}"/>
</svg>'''


files = {}
for name, t in THEMES.items():
    files[f"header-{name}.svg"] = header(t)
    files[f"adsops-{name}.svg"] = product(
        t, ("01", "WHAT I'M BUILDING"), "Adsops",
        ["AI creative production for advertisers: a studio,", "an agent and ad boards in one SaaS."],
        "TYPESCRIPT  /  NEXT.JS  /  BUN", link="adsops.ai")
    files[f"nodeops-{name}.svg"] = product(
        t, None, "Nodeops",
        ["In-browser Node runtime and a hosted", "prompt-to-app platform."], "TYPESCRIPT")
    files[f"sectors-{name}.svg"] = sectors(t)
    files[f"activity-{name}.svg"] = activity(t)
    files[f"stack-{name}.svg"] = stack(t)
    files[f"principles-{name}.svg"] = principles(t)
for fn, content in files.items():
    open(os.path.join(OUT, fn), "w").write(content)
print(len(files), "files")
