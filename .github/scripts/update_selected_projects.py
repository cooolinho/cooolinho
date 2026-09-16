#!/usr/bin/env python3
"""Rendert die "Selected projects"-Tabelle im README aus der GitHub-API.

Umgebungsvariablen:
  GH_TOKEN                 Fine-grained PAT (Metadata: Read-only)
  SELECTED_PROJECTS        Repos, getrennt durch Komma oder Zeilenumbruch
                           ("repo" oder "owner/repo"), Reihenfolge = Tabelle
  GITHUB_REPOSITORY_OWNER  Default-Owner fuer Eintraege ohne "owner/"
  README_PATH              optional, Default README.md

Nur Standardbibliothek, damit im Workflow kein Setup-Step noetig ist.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

START_MARKER = "<!-- SELECTED-PROJECTS:START -->"
END_MARKER = "<!-- SELECTED-PROJECTS:END -->"
MAX_TOPICS = 5


def fail(message):
    print(f"::error::{message}")
    sys.exit(1)


def parse_projects(raw, default_owner):
    projects = []
    for entry in re.split(r"[,\n]", raw):
        entry = entry.strip()
        if not entry:
            continue
        if "/" not in entry:
            if not default_owner:
                fail(f"'{entry}' hat keinen Owner und GITHUB_REPOSITORY_OWNER ist nicht gesetzt.")
            entry = f"{default_owner}/{entry}"
        projects.append(entry)
    return projects


def fetch_repo(full_name, token):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{full_name}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "selected-projects-readme",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            fail(f"{full_name}: HTTP {error.code} - Token ungueltig, abgelaufen oder ohne Zugriff.")
        if error.code == 404:
            fail(f"{full_name}: HTTP 404 - Tippfehler in SELECTED_PROJECTS oder Repo nicht oeffentlich.")
        fail(f"{full_name}: HTTP {error.code} - {error.reason}")
    except urllib.error.URLError as error:
        fail(f"{full_name}: API nicht erreichbar - {error.reason}")


def escape_cell(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def render_row(repo, default_owner):
    owner = repo["owner"]["login"]
    name = repo["name"] if owner.lower() == (default_owner or "").lower() else repo["full_name"]

    description = escape_cell(repo.get("description")) or "—"
    topics = repo.get("topics") or []
    if topics:
        description += "<br><sub>" + " ".join(f"`{t}`" for t in topics[:MAX_TOPICS]) + "</sub>"

    language = escape_cell(repo.get("language")) or "—"
    pushed = (repo.get("pushed_at") or "")[:10] or "—"

    return (
        f"| [{name}]({repo['html_url']}) | {description} | {language} "
        f"| {repo['stargazers_count']} | {repo['forks_count']} | {pushed} |"
    )


def render_table(repos, default_owner):
    lines = [
        "| Project | What it is | Language | ⭐ Stars | 🍴 Forks | Last push |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    lines += [render_row(repo, default_owner) for repo in repos]
    return "\n".join(lines)


def main():
    token = os.environ.get("GH_TOKEN", "").strip()
    raw_projects = os.environ.get("SELECTED_PROJECTS", "")
    default_owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "").strip()
    readme_path = os.environ.get("README_PATH", "README.md")

    if not token:
        fail("GH_TOKEN ist leer - Secret PROJECTS_GITHUB_TOKEN anlegen.")
    projects = parse_projects(raw_projects, default_owner)
    if not projects:
        fail("SELECTED_PROJECTS ist leer - Actions-Variable mit Repo-Namen anlegen.")

    repos = []
    for full_name in projects:
        repo = fetch_repo(full_name, token)
        if repo.get("private"):
            fail(f"{full_name} ist privat und wird nicht im oeffentlichen README angezeigt.")
        repos.append(repo)

    with open(readme_path, encoding="utf-8") as handle:
        readme = handle.read()

    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)
    if not pattern.search(readme):
        fail(f"Marker {START_MARKER} / {END_MARKER} fehlen in {readme_path}.")

    block = f"{START_MARKER}\n{render_table(repos, default_owner)}\n{END_MARKER}"
    updated = pattern.sub(lambda _: block, readme, count=1)

    if updated == readme:
        print(f"unchanged ({len(repos)} projects)")
        return

    with open(readme_path, "w", encoding="utf-8") as handle:
        handle.write(updated)
    print(f"changed ({len(repos)} projects)")


if __name__ == "__main__":
    main()
