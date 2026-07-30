#!/usr/bin/env python3
"""Auto-generate GitHub profile README from live repo data."""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER = "earentir"
ORG = "network-plane"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "earentir-profile-readme-generator",
    "X-GitHub-Api-Version": "2022-11-28",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def api_json(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} for {url}: {e.read().decode()[:500]}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_repos(owner: str, is_org: bool = False):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/{'orgs' if is_org else 'users'}/{owner}/repos?per_page=100&page={page}&sort=updated"
        data = api_json(url)
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def categorize(repos: list[dict]):
    categories = {
        "🌐 Network Stack (network-plane)": [],
        "🛠️ Dev Tools & CLI": [],
        "🔌 Hardware & System Info": [],
        "📡 DNS & Network Utilities": [],
        "🎬 API Clients & Media": [],
        "🖥️ TUI & Terminal Apps": [],
        "🎮 Games, Bots & Fun": [],
        "📊 Calculators & Productivity": [],
        "📁 Other Projects": [],
        "🗃️ Archived Projects": [],
    }

    dev_tools = {
        "pbuild", "updatego", "gitcng", "gitearelease", "fndupe", "ttail",
        "linknife", "discordupdate", "tablemaker", "identifybin", "confstore",
        "gitea-release",
    }
    hardware = {"cpuid", "gosmbios", "tsmbios", "ehw", "xdb", "mkfat", "dsktool"}
    dns_net = {"tunneldnsctl", "r53q", "sslcheck", "subscan", "prvdns"}
    api_media = {
        "earapi", "tmdbclient", "tmdbapidata", "steamapidata", "go-proxmox",
        "netflixtudumscrapper",
    }
    tui = {"mdnfo", "retrotui", "tui-json-viewer", "keyboardtester", "contribmap"}
    games_fun = {"tamegatchi", "holedivers", "etbot", "discordmagictime", "randomstreamscripts"}
    calc_prod = {
        "inflation", "simpleinterestcalculations", "simplecal", "commoncal",
        "timeoff", "relplanner", "internettime", "RailStationHelper", "nightrelcalc",
    }
    web = {"homepage", "earentir.github.io", "planeweb", "cmsmgmt"}
    libs = {".trunk"}

    total_stars = 0

    for r in repos:
        name = r["name"]
        owner_name = r["owner"]["login"]
        archived = r.get("archived", False)
        stars = r.get("stargazers_count", 0) or 0
        total_stars += stars

        item = {
            "name": name,
            "owner": owner_name,
            "url": r["html_url"],
            "description": (r.get("description") or "").strip(),
            "stars": stars,
            "archived": archived,
        }

        if archived:
            categories["🗃️ Archived Projects"].append(item)
            continue

        if owner_name == ORG:
            categories["🌐 Network Stack (network-plane)"].append(item)
            continue

        if name in dev_tools:
            categories["🛠️ Dev Tools & CLI"].append(item)
        elif name in hardware:
            categories["🔌 Hardware & System Info"].append(item)
        elif name in dns_net:
            categories["📡 DNS & Network Utilities"].append(item)
        elif name in api_media:
            categories["🎬 API Clients & Media"].append(item)
        elif name in tui:
            categories["🖥️ TUI & Terminal Apps"].append(item)
        elif name in games_fun:
            categories["🎮 Games, Bots & Fun"].append(item)
        elif name in calc_prod:
            categories["📊 Calculators & Productivity"].append(item)
        elif name in web:
            categories["📁 Other Projects"].append(item)
        elif name in libs:
            categories["📁 Other Projects"].append(item)
        else:
            categories["📁 Other Projects"].append(item)

    # Sort each category by stars desc
    for cat in categories:
        categories[cat].sort(key=lambda x: x["stars"], reverse=True)

    return categories, total_stars


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_html_table(repos_list: list[dict]) -> str:
    if not repos_list:
        return "_No projects in this category._\n"
    lines = [
        '<table width="100%">',
        '<thead><tr><th width="35%">Repository</th><th width="65%">Description</th></tr></thead>',
        '<tbody>',
    ]
    for r in repos_list:
        name = escape_html(r["name"])
        url = r["url"]
        desc = escape_html(r["description"] or "")
        if len(desc) > 90:
            desc = desc[:87] + "..."
        lines.append(f'<tr><td><a href="{url}">{name}</a></td><td>{desc}</td></tr>')
    lines.append('</tbody>')
    lines.append('</table>')
    return "\n".join(lines) + "\n"


def generate_readme(categories: dict, total_stars: int, total_repos: int) -> str:
    lines = [
        '<div align="center">',
        "",
        '<!-- Animated header -->',
        '<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color=58A6FF&center=true&vCenter=true&width=1000&lines=Hallo;I+am+a+Senior+DevOps+Tech+Lead;I+love+building+tooling+and+platforms;Checkout+Network+Plane+a+full+stack+of+services" alt="Typing SVG" />',
        "",
        "<br>",
        "",
        '[![Website](https://img.shields.io/badge/Website-earentir.dev-58A6FF?style=flat-square&logo=firefox&logoColor=white)](https://earentir.dev)',
        '[![GitHub Followers](https://img.shields.io/github/followers/earentir?style=flat-square&logo=github&color=181717)](https://github.com/earentir)',
        f'[![Repos](https://img.shields.io/badge/Repos-{total_repos}+-181717?style=flat-square&logo=github)](https://github.com/earentir?tab=repositories)',
        "",
        "</div>",
        "",
        "---",
        "",
        "## 📊 GitHub Analytics",
        "",
        '<div align="center">',
        "",
        '<a href="https://github.com/earentir">',
        '  <img height="180em" src="https://github-readme-stats.vercel.app/api?username=earentir&show_icons=true&theme=github_dark&hide_border=true&include_all_commits=true&count_private=true&bg_color=0d1117&title_color=58a6ff&icon_color=58a6ff&text_color=c9d1d9&cache_seconds=86400" />',
        "</a>",
        '<a href="https://github.com/earentir">',
        '  <img height="180em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=earentir&layout=compact&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=58a6ff&text_color=c9d1d9&langs_count=10&cache_seconds=86400" />',
        "</a>",
        "",
        "<br><br>",
        "",
        '<a href="https://github.com/earentir">',
        '  <img src="https://github-readme-streak-stats.herokuapp.com/?user=earentir&theme=github-dark-blue&hide_border=true&background=0d1117&stroke=30363d&ring=58a6ff&fire=58a6ff&currStreakLabel=58a6ff" alt="GitHub Streak" />',
        "</a>",
        "",
        "<br><br>",
        "",
        '<a href="https://github.com/earentir">',
        '  <img src="https://github-readme-activity-graph.vercel.app/graph?username=earentir&theme=github-dark&hide_border=true&bg_color=0d1117&color=58a6ff&line=58a6ff&point=c9d1d9" alt="Activity Graph" />',
        "</a>",
        "",
        "</div>",
        "",
        "---",
        "",
        "## 🚀 Projects by Category",
        "",
        f"> **{total_repos} repositories** across personal projects and the [**Network Plane**](https://github.com/network-plane) ecosystem.",
        "",
    ]

    for cat_name, cat_repos in categories.items():
        if not cat_repos:
            continue
        lines.append(f"### {cat_name}")
        lines.append("")
        lines.append(format_html_table(cat_repos))

    lines.extend([
        "---",
        "",
        "## 🛠️ Tech Stack",
        "",
        '<div align="center">',
        "",
        "![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)",
        "![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)",
        "![Pascal](https://img.shields.io/badge/Pascal-00599C?style=for-the-badge&logo=delphi&logoColor=white)",
        "![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)",
        "![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)",
        "![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)",
        "",
        "</div>",
        "",
        "---",
        "",
        '<div align="center">',
        "",
        '> *"Building tooling since 1998"*',
        "",
        "<br>",
        "",
        f'![GitHub Stars](https://img.shields.io/badge/Total_Stars-{total_stars}-FFD700?style=for-the-badge&logo=github&logoColor=white)',
        "",
        "</div>",
        "",
    ])

    return "\n".join(lines)


def main():
    print("Fetching user repos...")
    user_repos = fetch_repos(USER, is_org=False)
    print(f"  → {len(user_repos)} user repos")

    print("Fetching org repos...")
    org_repos = fetch_repos(ORG, is_org=True)
    print(f"  → {len(org_repos)} org repos")

    all_repos = user_repos + org_repos
    total_repos = len(all_repos)
    print(f"Total repos: {total_repos}")

    categories, total_stars = categorize(all_repos)
    print(f"Total stars: {total_stars}")

    readme = generate_readme(categories, total_stars, total_repos)

    output_path = Path(__file__).resolve().parent.parent / "README.md"
    output_path.write_text(readme, encoding="utf-8")
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
