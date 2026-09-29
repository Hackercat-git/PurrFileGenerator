<div align="center">

# 🐾 PurrFileGenerator

**Generate a clean, animated SVG stats card for any GitHub profile.**

![preview](preview_full.svg)

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](purrfile.py)

</div>

---

## Features

- **15 icon themes** — cat, robot, space, wave, terminal, fire, diamond, lightning, flower, ghost, moon, pixel, virus, sword, shield
- **15 color palettes** — lavender, forest, ocean, neon, sunset, rose, arctic, ember, earth, slate, crimson, midnight, sage, copper, mono
- **Automatic dark / light mode** — card adapts to the viewer's OS theme via CSS `prefers-color-scheme`
- **Smooth animations** — stat numbers fade up on load, language bar reveals with an eased wipe
- **Current streak counter** — calculates consecutive push days from the GitHub Events API
- **Compact mode** — a 300 × 155 px variant for tight spaces
- **`--accent` override** — swap the accent color on the fly without touching a palette
- **Stats caching** — save a JSON snapshot and re-render offline (`--save-cache` / `--from-cache`)
- **Zero dependencies** — pure Python 3.8 + standard library only

---

## Quick start

```bash
python purrfile.py <username>
```

This fetches the user's public stats and writes `purrfile.svg` to the current directory.

---

## Usage

```
python purrfile.py [username] [options]
```

| Option | Description |
|---|---|
| `username` | GitHub username (or omit and set `GITHUB_USER` env var) |
| `-o FILE` | Output path (default: `purrfile.svg`) |
| `--theme NAME` | Icon theme (default: `cat`) |
| `--palette NAME` | Color palette (default: `lavender`) |
| `--accent #RRGGBB` | Override the accent color |
| `--compact` | Render the 300 × 155 compact card instead |
| `--include-forks` | Count forked repos in the stats |
| `--markdown` | Print a Markdown embed snippet after saving |
| `--save-cache FILE` | Save fetched stats to a JSON file |
| `--from-cache FILE` | Load stats from a cache file instead of the API |
| `--list-themes` | Print all available theme names |
| `--list-palettes` | Print all available palette names |

### Examples

```bash
# Full card with the forest palette and cat theme
python purrfile.py Hackercat-git --palette forest --theme cat

# Compact card with the neon palette and terminal theme
python purrfile.py Hackercat-git --compact --palette neon --theme terminal

# Custom accent color
python purrfile.py Hackercat-git --accent "#ff6b6b"

# Save API response and re-render offline later
python purrfile.py Hackercat-git --save-cache stats.json
python purrfile.py Hackercat-git --from-cache stats.json --palette ocean

# Print a Markdown embed snippet
python purrfile.py Hackercat-git --markdown
```

---

## Authentication

The card works without a token, but the GitHub API allows only **60 unauthenticated requests per hour**. To avoid rate limiting, set a personal access token:

```bash
# macOS / Linux
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Windows PowerShell
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
```

A token with no extra scopes (the default) is sufficient for public data.

---

## Themes & Palettes

**List all available options:**

```bash
python purrfile.py --list-themes
python purrfile.py --list-palettes
```

### Theme icons

`cat` `robot` `space` `wave` `terminal` `fire` `diamond` `lightning` `flower` `ghost` `moon` `pixel` `virus` `sword` `shield`

### Color palettes

`lavender` `forest` `ocean` `neon` `sunset` `rose` `arctic` `ember` `earth` `slate` `crimson` `midnight` `sage` `copper` `mono`

All palettes include both dark and light variants and switch automatically based on the viewer's OS preference.

---

## Compact card

Pass `--compact` to render a smaller 300 × 155 px card — useful in sidebars or narrow profile layouts:

```bash
python purrfile.py <username> --compact --palette neon --theme terminal
```

![compact preview](preview_compact.svg)

---

## Add the card to your GitHub profile

1. Create a repo named exactly like your GitHub username (e.g. `Hackercat-git/Hackercat-git`).
2. Copy `purrfile.py` and `.github/workflows/update-card.yml` into it.
3. Add this line to your profile `README.md`:

```markdown
![Stats](purrfile.svg)
```

4. The included GitHub Action refreshes the card automatically every day at 06:00 UTC.

> **Tip:** Customize the workflow's `--theme` and `--palette` flags to match your profile's style.

---

## GitHub Actions workflow

The bundled `.github/workflows/update-card.yml` runs daily and commits the updated SVG automatically:

```yaml
- run: python purrfile.py ${{ github.repository_owner }} -o purrfile.svg --theme cat --palette forest
```

Edit the `--theme` and `--palette` flags to your liking before copying the workflow to your profile repo.

---

## Running tests

```bash
python -m unittest discover tests
```

---

## License

[MIT](LICENSE) — do whatever you like with it.
