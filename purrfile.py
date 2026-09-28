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
from html import escape

API = "https://api.github.com"
COLORS = ["#3178c6", "#f1e05a", "#e34c26", "#3572A5", "#89e051"]


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
            sys.exit("Gebruiker niet gevonden / User not found.")
        if err.code == 403:
            sys.exit("Rate limit bereikt. Zet een GITHUB_TOKEN omgevingsvariabele.")
        raise


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


def render_svg(username, stats):
    width, bar_x, bar_w = 495, 30, 435
    langs = stats["languages"]
    total = sum(c for _, c in langs) or 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="235" viewBox="0 0 {width} 235">',
        f'<defs><clipPath id="bar"><rect x="{bar_x}" y="125" width="{bar_w}" height="10" rx="5"/></clipPath></defs>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="234" rx="10" fill="#0d1117" stroke="#30363d"/>',
        f'<text x="30" y="40" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="600" fill="#e6edf3">{escape(username)} on GitHub</text>',
    ]

    for i, (label, value) in enumerate(
        [("Repos", stats["repos"]), ("Stars", stats["stars"]), ("Forks", stats["forks"])]
    ):
        x = 30 + i * 150
        parts.append(
            f'<text x="{x}" y="80" font-family="Segoe UI, Arial, sans-serif" font-size="26" font-weight="700" fill="#58a6ff">{value}</text>'
        )
        parts.append(
            f'<text x="{x}" y="100" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#8b949e">{label}</text>'
        )

    parts.append('<g clip-path="url(#bar)">')
    parts.append(f'<rect x="{bar_x}" y="125" width="{bar_w}" height="10" fill="#21262d"/>')
    offset = 0.0
    for i, (_, count) in enumerate(langs):
        w = bar_w * count / total
        parts.append(
            f'<rect x="{bar_x + offset:.1f}" y="125" width="{w:.1f}" height="10" fill="{COLORS[i % len(COLORS)]}"/>'
        )
        offset += w
    parts.append("</g>")

    for i, (name, count) in enumerate(langs):
        x = 30 + (i % 3) * 150
        y = 165 + (i // 3) * 24
        pct = round(100 * count / total)
        parts.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{COLORS[i % len(COLORS)]}"/>')
        parts.append(
            f'<text x="{x + 16}" y="{y}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#c9d1d9">{escape(name)} {pct}%</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def render_markdown(username, stats):
    lines = [
        f"### {username} on GitHub",
        "",
        f"- Repos: **{stats['repos']}**  |  Stars: **{stats['stars']}**  |  Forks: **{stats['forks']}**",
    ]
    if stats["languages"]:
        lines.append("- Top talen: " + ", ".join(n for n, _ in stats["languages"]))
    if stats["top"]:
        lines.append("- Top repos: " + ", ".join(f"{n} ({s}★)" for n, s in stats["top"]))
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Genereer een SVG-statistiekenkaart voor een GitHub-profiel.")
    p.add_argument("username", help="GitHub-gebruikersnaam")
    p.add_argument("-o", "--output", default="purrfile.svg", help="Uitvoerbestand (standaard: purrfile.svg)")
    p.add_argument("--include-forks", action="store_true", help="Tel geforkte repo's mee")
    p.add_argument("--markdown", action="store_true", help="Print ook een Markdown-samenvatting")
    args = p.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    stats = summarize(fetch_repos(args.username, token), args.include_forks)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(render_svg(args.username, stats))
    print(f"Kaart opgeslagen als {args.output}")
    if args.markdown:
        print()
        print(render_markdown(args.username, stats))


if __name__ == "__main__":
    main()
