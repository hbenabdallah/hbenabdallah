"""Render the README stats cards and footer as pixel-art SVGs matching header.svg."""

import datetime
import json
import os
import random
import sys
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "hbenabdallah")
OUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKY = ("#0d1117", "#112a2e", "#1b4d4a")
TEAL = "#2dd4bf"
WHITE = "#e6edf3"
GREY = "#8b949e"
GRASS = ("#2f9e6b", "#3fc98a")
DIRT = ("#4a3120", "#6e4c2f", "#3f2a1b", "#5b3d24")
FLAME = ("#f0883e", "#f2cc60", "#e6edf3")

FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    ":": "00000 01100 01100 00000 01100 01100 00000",
    "/": "00001 00001 00010 00100 01000 10000 10000",
    "+": "00000 00100 00100 11111 00100 00100 00000",
}

ICONS = {
    "star": "0001000 0001000 1111111 0111110 0011100 0110110 1100011",
    "commit": "0000000 0011100 0100010 1100011 0100010 0011100 0000000",
    "pr": "1100011 1100110 0001100 0000000 0110000 0110011 0000011",
    "issue": "0111110 1100011 1001001 1001001 1000001 1101011 0111110",
    "repo": "1111110 1000010 1011010 1000010 1011010 1000010 1111110",
}

FLAME_FRAMES = [
    ["0001000", "0011000", "0011100", "0112110", "1122211", "1223221", "0123210", "0012100"],
    ["0000100", "0001100", "0011100", "0112110", "1122211", "1222321", "0123210", "0012100"],
]


def text_width(text, scale):
    return (len(text) * 6 - 1) * scale


def pixels_path(rows, x, y, scale, on="1"):
    parts = []
    for r, row in enumerate(rows):
        for c, bit in enumerate(row):
            if bit == on:
                parts.append(f"M{x + c * scale} {y + r * scale}h{scale}v{scale}h-{scale}z")
    return "".join(parts)


def text(content, x, y, scale, fill, anchor="start", cls=""):
    content = content.upper()
    if anchor == "middle":
        x -= text_width(content, scale) // 2
    elif anchor == "end":
        x -= text_width(content, scale)
    d = "".join(
        pixels_path(FONT.get(ch, FONT[" "]).split(), x + i * 6 * scale, y, scale)
        for i, ch in enumerate(content)
    )
    cls_attr = f' class="{cls}"' if cls else ""
    return f'<path{cls_attr} d="{d}" fill="{fill}"/>'


def icon(name, x, y, scale, fill):
    return f'<path d="{pixels_path(ICONS[name].split(), x, y, scale)}" fill="{fill}"/>'


def flame(cx, y, scale):
    frames = []
    w = len(FLAME_FRAMES[0][0]) * scale
    for i, frame in enumerate(FLAME_FRAMES):
        layers = "".join(
            f'<path d="{pixels_path(frame, cx - w // 2, y, scale, on=str(level + 1))}" fill="{color}"/>'
            for level, color in enumerate(FLAME)
        )
        frames.append(f'<g class="fr{i}">{layers}</g>')
    return "".join(frames)


def style():
    return """<style>
.tw{animation:tw ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}
.fade{animation:fade 1.2s ease-out both}
@keyframes fade{from{opacity:0}to{opacity:1}}
.fr0{animation:fa .6s steps(1) infinite}
.fr1{animation:fb .6s steps(1) infinite}
@keyframes fa{0%{opacity:1}50%{opacity:0}}
@keyframes fb{0%{opacity:0}50%{opacity:1}}
</style>"""


def sky(width, height, rng, stars, avoid=()):
    out = [
        '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{SKY[0]}"/><stop offset=".6" stop-color="{SKY[1]}"/>'
        f'<stop offset="1" stop-color="{SKY[2]}"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" fill="url(#sky)"/>',
    ]
    placed = 0
    while placed < stars:
        x, y = rng.randrange(0, width, 5), rng.randrange(0, height - 40, 5)
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in avoid):
            continue
        placed += 1
        size = rng.choice((2, 3, 3, 4))
        out.append(
            f'<rect class="tw" style="animation-duration:{rng.uniform(1.6, 4):.1f}s;'
            f'animation-delay:{rng.uniform(0, 4):.1f}s" x="{x}" y="{y}" width="{size}" height="{size}" fill="{WHITE}"/>'
        )
    return out


def ground(width, top, height, rng, block=6):
    paths = {color: [] for color in GRASS + DIRT}
    for x in range(0, width, block):
        grass_depth = rng.choice((1, 1, 2))
        for row, y in enumerate(range(top, top + height, block)):
            if row < grass_depth:
                color = GRASS[1] if row == 0 and rng.random() < 0.3 else GRASS[0]
            else:
                color = rng.choice(DIRT)
            paths[color].append(f"M{x} {y}h{block}v{block}h-{block}z")
    return [f'<path d="{"".join(d)}" fill="{c}"/>' for c, d in paths.items() if d]


def svg(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" shape-rendering="crispEdges">\n'
        + style() + "\n" + "\n".join(body) + "\n</svg>\n"
    )


def short(n):
    if n >= 10000:
        return f"{n / 1000:.1f}K".replace(".0K", "K")
    return str(n)


def graphql(token, query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "pixel-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def fetch_stats(token):
    years_query = """query($login:String!){user(login:$login){
      contributionsCollection{contributionYears}
      pullRequests{totalCount} issues{totalCount}
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,ISSUE,REPOSITORY]){totalCount}
      repositories(ownerAffiliations:OWNER,isFork:false,first:100){nodes{stargazerCount}}}}"""
    user = graphql(token, years_query, {"login": LOGIN})["user"]

    year_fields = "\n".join(
        f'y{year}:contributionsCollection(from:"{year}-01-01T00:00:00Z",to:"{year}-12-31T23:59:59Z"){{'
        "totalCommitContributions restrictedContributionsCount "
        "contributionCalendar{weeks{contributionDays{date contributionCount}}}}"
        for year in user["contributionsCollection"]["contributionYears"]
    )
    years = graphql(token, f"query($login:String!){{user(login:$login){{{year_fields}}}}}", {"login": LOGIN})["user"]

    days = {}
    commits = 0
    for collection in years.values():
        commits += collection["totalCommitContributions"] + collection["restrictedContributionsCount"]
        for week in collection["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                days[day["date"]] = day["contributionCount"]

    return {
        "stars": sum(r["stargazerCount"] for r in user["repositories"]["nodes"]),
        "commits": commits,
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "contributed": user["repositoriesContributedTo"]["totalCount"],
        "days": days,
    }


def streaks(days):
    today = datetime.date.today().isoformat()
    ordered = sorted(d for d in days if d <= today)
    longest = run = 0
    for date in ordered:
        run = run + 1 if days[date] else 0
        longest = max(longest, run)
    current = 0
    for date in reversed(ordered):
        if days[date]:
            current += 1
        elif date != today or current:
            break
    return sum(days[d] for d in ordered), current, longest


def stats_card(stats):
    width, height = 480, 200
    rng = random.Random(7)
    body = sky(width, height, rng, 14, avoid=[(14, 10, 300, 48), (10, 50, width, 172)])
    body.append(text("GitHub Stats", 24, 18, 3, TEAL))
    rows = [
        ("star", "Total stars", stats["stars"]),
        ("commit", "Total commits", stats["commits"]),
        ("pr", "Pull requests", stats["prs"]),
        ("issue", "Issues", stats["issues"]),
        ("repo", "Contributed to", stats["contributed"]),
    ]
    for i, (name, label, value) in enumerate(rows):
        y = 56 + i * 22
        body.append(icon(name, 24, y, 2, TEAL))
        body.append(text(label, 48, y, 2, GREY))
        body.append(text(short(value), width - 24, y, 2, WHITE, anchor="end", cls="fade"))
    body += ground(width, 176, 24, rng)
    return svg(width, height, body)


def streak_card(days):
    width, height = 480, 200
    total, current, longest = streaks(days)
    rng = random.Random(11)
    body = sky(width, height, rng, 14, avoid=[(10, 54, width - 10, 150), (210, 10, 270, 54)])
    columns = [
        (80, total, ("Total", "contribs")),
        (240, current, ("Current", "streak")),
        (400, longest, ("Longest", "streak")),
    ]
    for cx, value, labels in columns:
        colour = TEAL if cx == 240 else WHITE
        body.append(text(short(value), cx, 64, 4, colour, anchor="middle", cls="fade"))
        for j, label in enumerate(labels):
            body.append(text(label, cx, 112 + j * 18, 2, GREY, anchor="middle"))
    body.append(flame(240, 20, 4))
    body.append(f'<path d="M160 56h2v84h-2zM318 56h2v84h-2z" fill="{SKY[2]}"/>')
    body += ground(width, 176, 24, rng)
    return svg(width, height, body)


def footer():
    width, height = 1200, 90
    rng = random.Random(3)
    body = sky(width, height, rng, 30)
    for x in range(30, width, 90):
        stem_x = x + rng.randrange(0, 60, 6)
        petal = rng.choice((TEAL, "#7c8ad1", WHITE))
        body.append(f'<path d="M{stem_x} 48h6v12h-6z" fill="{GRASS[0]}"/>')
        body.append(f'<path d="M{stem_x - 6} 42h6v6h-6zM{stem_x + 6} 42h6v6h-6zM{stem_x} 36h6v6h-6z" fill="{petal}"/>')
        body.append(f'<path d="M{stem_x} 42h6v6h-6z" fill="#f2cc60"/>')
    body += ground(width, 60, 30, rng)
    return svg(width, height, body)


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GH_TOKEN is required")
    stats = fetch_stats(token)
    cards = {
        "stats.svg": stats_card(stats),
        "streak.svg": streak_card(stats["days"]),
        "footer.svg": footer(),
    }
    for name, content in cards.items():
        with open(os.path.join(OUT_DIR, name), "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
