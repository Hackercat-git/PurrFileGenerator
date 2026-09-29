#!/usr/bin/env python3
"""PurrFileGenerator - generate a clean SVG stats card for any GitHub profile.

No third-party dependencies: only the Python standard library.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape

API = "https://api.github.com"

# ---- Themes (icon motif) and palettes (colors) ----------------------------

def _icon_cat(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{c}">'
            '<ellipse cx="0" cy="6" rx="6.5" ry="5.5"/><ellipse cx="-6.5" cy="-2.5" rx="2.4" ry="3"/>'
            '<ellipse cx="-2.5" cy="-6.5" rx="2.4" ry="3"/><ellipse cx="2.5" cy="-6.5" rx="2.4" ry="3"/>'
            '<ellipse cx="6.5" cy="-2.5" rx="2.4" ry="3"/></g>')

def _icon_robot(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="{c}" stroke-width="1.6">'
            f'<rect x="-7" y="-4" width="14" height="11" rx="3"/>'
            f'<circle cx="-3" cy="1" r="1.4" fill="{c}"/><circle cx="3" cy="1" r="1.4" fill="{c}"/>'
            f'<line x1="0" y1="-4" x2="0" y2="-8"/><circle cx="0" cy="-9" r="1.4" fill="{c}"/></g>')

def _icon_space(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{c}">'
            '<path d="M0,-9 L2.2,-2.6 L9,-2.2 L3.6,2 L5.4,8.6 L0,4.8 L-5.4,8.6 L-3.6,2 L-9,-2.2 L-2.2,-2.6 Z"/></g>')

def _icon_wave(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round">'
            '<path d="M-9,2 Q-5,-6 0,2 T9,2"/><path d="M-9,7 Q-5,-1 0,7 T9,7" stroke-opacity="0.5"/></g>')

def _icon_terminal(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round">'
            '<path d="M-8,-6 L-2,0 L-8,6"/><line x1="1" y1="6" x2="8" y2="6"/></g>')

def _icon_leaf(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{c}">'
            '<path d="M0,9 C-9,7 -9,-7 0,-9 C9,-7 9,7 0,9 Z"/>'
            '<line x1="0" y1="9" x2="0" y2="-9" stroke="#0006" stroke-width="1"/></g>')

def _icon_coffee(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="{c}" stroke-width="1.7">'
            '<path d="M-7,-3 h11 v6 a5.5,5.5 0 0 1 -5.5,5.5 h0 A5.5,5.5 0 0 1 -7,3 Z"/>'
            '<path d="M4,-1 q4,0 4,3 q0,3 -4,3"/>'
            '<path d="M-3,-6 q1,-2 0,-4" stroke-linecap="round"/><path d="M1,-6 q1,-2 0,-4" stroke-linecap="round"/></g>')

def _icon_pixel(x, y, s, c):
    coords = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    r = 2.6
    rects = "".join(f'<rect x="{cx*6-r}" y="{cy*6-r}" width="{r*2}" height="{r*2}" fill="{c}"/>' for cx, cy in coords)
    return f'<g transform="translate({x},{y}) scale({s})">{rects}</g>'

def _icon_music(x, y, s, c):
    bars = [(-8,4),(-3,8),(2,3),(7,7)]
    rects = "".join(f'<rect x="{bx-1.5}" y="{-h}" width="3" height="{h*2}" rx="1.5" fill="{c}"/>' for bx, h in bars)
    return f'<g transform="translate({x},{y}) scale({s})">{rects}</g>'

def _icon_weather(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<g fill="{c}"><ellipse cx="-3" cy="0" rx="5" ry="4"/><ellipse cx="3" cy="-1" rx="6" ry="5"/><ellipse cx="8" cy="1" rx="4" ry="3.2"/></g>'
            '<path d="M1,7 L-2,13 L1,13 L-1,18" fill="none" stroke="#facc15" stroke-width="1.8" stroke-linecap="round"/></g>')

def _icon_book(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="{c}" stroke-width="1.7">'
            '<path d="M0,-6 C-3,-8 -8,-8 -9,-6 L-9,7 C-8,5 -3,5 0,7 Z"/>'
            '<path d="M0,-6 C3,-8 8,-8 9,-6 L9,7 C8,5 3,5 0,7 Z"/></g>')

def _icon_fire(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{c}">'
            '<path d="M0,-9 C4,-4 6,-1 4,3 C7,1 8,-2 8,-2 C9,4 5,9 -1,9 C-7,9 -9,3 -6,-1 '
            'C-5,1 -3,1 -3,-1 C-4,-4 -2,-7 0,-9 Z"/></g>')

def _icon_snow(x, y, s, c):
    lines = "".join(f'<line x1="0" y1="-9" x2="0" y2="9" stroke="{c}" stroke-width="1.6" transform="rotate({a})"/>' for a in (0, 60, 120))
    return f'<g transform="translate({x},{y}) scale({s})">{lines}</g>'

def _icon_dragon(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" fill="{c}">'
            '<path d="M-9,4 L-4,-8 L-1,-1 L3,-9 L6,0 L9,-6 L7,5 C3,8 -5,8 -9,4 Z"/></g>')

def _icon_rainbow(x, y, s, c):
    cols = ["#f87171", "#fbbf24", "#4ade80", "#38bdf8", "#a78bfa"]
    arcs = "".join(
        f'<path d="M-9,{4-i*2} A{9-i*1.5},{9-i*1.5} 0 0 1 9,{4-i*2}" fill="none" stroke="{col}" stroke-width="1.8"/>'
        for i, col in enumerate(cols)
    )
    return f'<g transform="translate({x},{y}) scale({s})">{arcs}</g>'

THEMES = {
    "cat": _icon_cat, "robot": _icon_robot, "space": _icon_space, "ocean": _icon_wave,
    "terminal": _icon_terminal, "plant": _icon_leaf, "coffee": _icon_coffee, "gaming": _icon_pixel,
    "music": _icon_music, "weather": _icon_weather, "book": _icon_book, "fire": _icon_fire,
    "ice": _icon_snow, "dragon": _icon_dragon, "rainbow": _icon_rainbow,
}

# palette: (bg1, bg2, accent1, accent2, text_main, text_dim, lang_colors...)
# lang_colors: 5 colors for the language bar, tuned per palette
PALETTES = {
    "lavender": ("#150f23", "#0d1117", "#c084fc", "#f472b6", "#f5f3ff", "#a78bfa",
                 ["#c084fc", "#f472b6", "#818cf8", "#e879f9", "#a78bfa"]),
    "tuxedo":   ("#1a1a1a", "#0a0a0a", "#e6e6e6", "#9e9e9e", "#ffffff", "#bdbdbd",
                 ["#e6e6e6", "#9e9e9e", "#bdbdbd", "#d4d4d4", "#737373"]),
    "tabby":    ("#3a1f0f", "#1f1008", "#fb923c", "#fbbf24", "#fff7ed", "#fdba74",
                 ["#fb923c", "#fbbf24", "#f97316", "#facc15", "#ea580c"]),
    "calico":   ("#241a12", "#0f0a06", "#f97316", "#111827", "#fef3e2", "#e2b98a",
                 ["#f97316", "#fb923c", "#ea580c", "#fbbf24", "#c2410c"]),
    "siamese":  ("#2b241c", "#171310", "#d6a06b", "#8b5e34", "#fdf6ec", "#c9a274",
                 ["#d6a06b", "#c9a274", "#b45309", "#f59e0b", "#92400e"]),
    "neon":     ("#0a0018", "#020009", "#22d3ee", "#e879f9", "#f0f9ff", "#67e8f9",
                 ["#22d3ee", "#e879f9", "#34d399", "#f472b6", "#818cf8"]),
    "midnight": ("#0b1020", "#05070f", "#facc15", "#eab308", "#fff9e6", "#fde68a",
                 ["#facc15", "#eab308", "#fbbf24", "#f59e0b", "#d97706"]),
    "pastel":   ("#241b2e", "#150f1c", "#f9a8d4", "#6ee7b7", "#fdf2f8", "#f5c2dd",
                 ["#f9a8d4", "#6ee7b7", "#c4b5fd", "#fde68a", "#a5f3fc"]),
    "autumn":   ("#2c1508", "#170a03", "#ea580c", "#f59e0b", "#fff1e6", "#fdba74",
                 ["#ea580c", "#f59e0b", "#dc2626", "#d97706", "#b45309"]),
    "grayscale":("#1c1c1c", "#0e0e0e", "#d4d4d4", "#8a8a8a", "#f5f5f5", "#b0b0b0",
                 ["#d4d4d4", "#a3a3a3", "#737373", "#e5e5e5", "#525252"]),
    "ocean":    ("#031826", "#010d16", "#22d3ee", "#0ea5e9", "#ecfeff", "#7dd3fc",
                 ["#22d3ee", "#0ea5e9", "#38bdf8", "#06b6d4", "#0284c7"]),
    "sakura":   ("#241019", "#12080d", "#fda4c7", "#f472b6", "#fff0f5", "#f9c9d9",
                 ["#fda4c7", "#f472b6", "#fb7185", "#e879f9", "#f9a8d4"]),
    "forest":   ("#0f1f14", "#08120c", "#4ade80", "#a3e635", "#f0fdf4", "#86efac",
                 ["#4ade80", "#a3e635", "#34d399", "#86efac", "#22c55e"]),
    "sunset":   ("#2a1030", "#160819", "#fb7185", "#f59e0b", "#fff1f2", "#fda4af",
                 ["#fb7185", "#f59e0b", "#f472b6", "#fbbf24", "#e11d48"]),
    "classic":  ("#0d1117", "#0d1117", "#58a6ff", "#3fb950", "#e6edf3", "#8b949e",
                 ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657"]),
}


def fetch_json(url, token=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "purrfile"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            sys.exit("User not found.")
        if err.code == 403:
            sys.exit("Rate limit reached. Set a GITHUB_TOKEN environment variable.")
        sys.exit(f"GitHub API error {err.code}: {err.reason}")
    except urllib.error.URLError as err:
        sys.exit(f"Network error: {err.reason}")
    except OSError as err:
        sys.exit(f"Connection error: {err}")


def fetch_repos(username, token=None):
    repos, page = [], 1
    while True:
        url = f"{API}/users/{username}/repos?per_page=100&page={page}&type=owner"
        batch = fetch_json(url, token)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def summarize(repos, include_forks=False):
    if not include_forks:
        repos = [r for r in repos if not r.get("fork")]
    langs = Counter(r["language"] for r in repos if r.get("language"))
    top = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:3]
    return {
        "repos": len(repos),
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
        "forks": sum(r.get("forks_count", 0) for r in repos),
        "languages": langs.most_common(5),
        "top": [(r["name"], r.get("stargazers_count", 0)) for r in top],
    }


def render_svg(username, stats, theme="cat", palette="lavender"):
    icon = THEMES.get(theme, _icon_cat)
    pal = PALETTES.get(palette, PALETTES["lavender"])
    bg1, bg2, ac1, ac2, tmain, tdim = pal[:6]
    lang_colors = pal[6]

    width, height = 495, 250
    bar_x, bar_w, bar_y = 30, 435, 140

    langs = stats["languages"]
    total = sum(c for _, c in langs) or 1
    font = "Segoe UI, Arial, sans-serif"
    updated = datetime.now(timezone.utc).strftime("%-d %b %Y")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"'
        f' viewBox="0 0 {width} {height}" role="img"'
        f' aria-label="{escape(username)} GitHub stats">',
        f'<title>{escape(username)} on GitHub</title>',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>',
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{ac1}"/><stop offset="1" stop-color="{ac2}"/></linearGradient>',
        f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>',
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" '
        f'fill="url(#bg)" stroke="{ac1}" stroke-opacity="0.35"/>',
        icon(453, 34, 1.3, ac1),
        f'<text x="30" y="42" font-family="{font}" font-size="19" font-weight="700" fill="{tmain}">'
        f"{escape(username)} on GitHub</text>",
        f'<rect x="30" y="54" width="46" height="3" rx="1.5" fill="url(#accent)"/>',
    ]

    for i, (label, value) in enumerate(
        [("Repos", stats["repos"]), ("Stars", stats["stars"]), ("Forks", stats["forks"])]
    ):
        x = 30 + i * 150
        parts.append(
            f'<text x="{x}" y="98" font-family="{font}" font-size="28" font-weight="700" fill="{tmain}">{value}</text>'
        )
        parts.append(f'<text x="{x}" y="118" font-family="{font}" font-size="12" fill="{tdim}">{label}</text>')

    parts.append(f'<text x="{bar_x}" y="{bar_y - 12}" font-family="{font}" font-size="12" fill="{tdim}">Languages</text>')
    parts.append('<g clip-path="url(#bar)">')
    parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" fill="{bg1}"/>')

    # Floating point fix: track cumulative fraction to avoid rounding drift
    cumulative = 0.0
    for i, (_, count) in enumerate(langs):
        fraction = count / total
        x_start = bar_x + bar_w * cumulative
        x_end = bar_x + bar_w * (cumulative + fraction)
        w = x_end - x_start
        fill = lang_colors[i % len(lang_colors)]
        parts.append(f'<rect x="{x_start:.2f}" y="{bar_y}" width="{w:.2f}" height="10" fill="{fill}"/>')
        cumulative += fraction
    parts.append("</g>")

    for i, (name, count) in enumerate(langs):
        x = 30 + (i % 3) * 150
        y = bar_y + 38 + (i // 3) * 26
        pct = round(100 * count / total)
        fill = lang_colors[i % len(lang_colors)]
        parts.append(icon(x + 6, y - 4, 0.55, fill))
        parts.append(f'<text x="{x + 18}" y="{y}" font-family="{font}" font-size="12" fill="{tdim}">{escape(name)} {pct}%</text>')

    parts.append(
        f'<text x="{width - 14}" y="{height - 12}" font-family="{font}" font-size="10"'
        f' fill="{tdim}" text-anchor="end" opacity="0.6">purrfile · {updated}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render_markdown(username, stats):
    lines = [
        f"### {username} on GitHub",
        "",
        f"- Repos: **{stats['repos']}** | Stars: **{stats['stars']}** | Forks: **{stats['forks']}**",
    ]
    if stats["languages"]:
        lines.append("- Top languages: " + ", ".join(n for n, _ in stats["languages"]))
    if stats["top"]:
        lines.append("- Top repos: " + ", ".join(f"{n} ({s}★)" for n, s in stats["top"]))
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Generate an SVG stats card for a GitHub profile.")
    p.add_argument("username", nargs="?", help="GitHub username")
    p.add_argument("-o", "--output", default="purrfile.svg", help="Output file (default: purrfile.svg)")
    p.add_argument("--include-forks", action="store_true", help="Include forked repositories")
    p.add_argument("--markdown", action="store_true", help="Also print a Markdown summary")
    p.add_argument("--theme", choices=sorted(THEMES), default="cat", help="Icon theme (default: cat)")
    p.add_argument("--palette", choices=sorted(PALETTES), default="lavender", help="Color palette (default: lavender)")
    p.add_argument("--list-themes", action="store_true", help="List all available themes and exit")
    p.add_argument("--list-palettes", action="store_true", help="List all available palettes and exit")
    args = p.parse_args(argv)

    if args.list_themes:
        print("Available themes: " + ", ".join(sorted(THEMES)))
        return
    if args.list_palettes:
        print("Available palettes: " + ", ".join(sorted(PALETTES)))
        return

    if not args.username:
        p.error("username is required unless using --list-themes or --list-palettes")

    token = os.environ.get("GITHUB_TOKEN")
    stats = summarize(fetch_repos(args.username, token), args.include_forks)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(render_svg(args.username, stats, theme=args.theme, palette=args.palette))
    print(f"Card saved as {args.output}")
    if args.markdown:
        print()
        print(render_markdown(args.username, stats))


if __name__ == "__main__":
    main()
