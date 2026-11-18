#!/usr/bin/env python3
"""Assemble the MkDocs source tree in build/site-src/ from the repository.

The docs site is a *view* of files that already exist — nothing here is maintained twice:

  docs/**                                  -> site root (hand-written pages)
  source/<tier>/<name>/SKILL.md            -> skills/<name>/index.md   (one page per skill)
  source/<tier>/<name>/{references,assets} -> skills/<name>/...
  sample/                                  -> sample/
  CONTRIBUTING.md, CHANGELOG.md, agents/   -> contributing.md, changelog.md, agents/

Relative links are rewritten so they keep pointing at the same file after the move. A link to a
repository file that is not part of the site becomes a GitHub URL, so `mkdocs build --strict`
fails only on links that are broken in the repository too.

Never commit the output: build/ is gitignored and rebuilt in CI.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "site-src"
REPO_URL = "https://github.com/parvez3019/ai-coding-microservices-skills"
TIERS = ("principles", "workflows", "profiles")
TIER_LABEL = {"principles": "Principle", "workflows": "Workflow", "profiles": "Profile"}

LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith(" "):
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, text[match.end():]


def summary(description: str, limit: int = 220) -> str:
    """First sentence of a skill description, for meta tags and index tables."""
    first = re.split(r"(?<=[.!?])\s", description, maxsplit=1)[0]
    return first if len(first) <= limit else first[: limit - 1].rstrip() + "…"


def yaml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def collect_skills() -> list[dict[str, str]]:
    skills = []
    for tier in TIERS:
        tier_dir = ROOT / "source" / tier
        if not tier_dir.is_dir():
            continue
        for skill_dir in sorted(p for p in tier_dir.iterdir() if p.is_dir()):
            meta, _ = parse_frontmatter((skill_dir / "SKILL.md").read_text())
            skills.append({
                "name": skill_dir.name,
                "tier": tier,
                "dir": str(skill_dir.relative_to(ROOT)),
                "description": meta.get("description", ""),
            })
    return skills


def build_map(skills: list[dict[str, str]]) -> dict[str, str]:
    """repo-relative path -> site-relative path, for every file the site publishes."""
    mapping: dict[str, str] = {}
    for path in (ROOT / "docs").rglob("*"):
        if path.is_file():
            rel = path.relative_to(ROOT)
            mapping[str(rel)] = str(path.relative_to(ROOT / "docs"))
    for skill in skills:
        skill_root = ROOT / skill["dir"]
        for path in skill_root.rglob("*"):
            if path.is_file():
                inner = path.relative_to(skill_root)
                target = "index.md" if str(inner) == "SKILL.md" else str(inner)
                mapping[str(path.relative_to(ROOT))] = f"skills/{skill['name']}/{target}"
    # MkDocs skips dot-directories, so the sample's .msskills/ files are lifted out of it.
    mapping["sample/README.md"] = "sample/index.md"
    for path in (ROOT / "sample").rglob("*.md"):
        rel = str(path.relative_to(ROOT))
        if rel != "sample/README.md":
            mapping[rel] = f"sample/{path.name}"
    mapping["CONTRIBUTING.md"] = "contributing.md"
    mapping["CHANGELOG.md"] = "changelog.md"
    for path in (ROOT / "agents").glob("*.md"):
        mapping[str(path.relative_to(ROOT))] = f"agents/{path.name}"
    return mapping


def rewrite_links(text: str, repo_path: str, site_path: str, mapping: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith(("#", "/")):
            return match.group(0)
        path, hash_, anchor = target.partition("#")
        resolved = os.path.normpath(os.path.join(os.path.dirname(repo_path), path))
        if resolved in mapping:
            new = os.path.relpath(mapping[resolved], os.path.dirname(site_path) or ".")
        elif (ROOT / resolved).exists() and not resolved.startswith(".."):
            kind = "tree" if (ROOT / resolved).is_dir() else "blob"
            new = f"{REPO_URL}/{kind}/main/{resolved}"
        else:
            return match.group(0)  # genuinely broken; let --strict report it
        return f"{match.group(1)}{new}{hash_}{anchor}{match.group(3)}"

    return LINK_RE.sub(replace, text)


def skill_page(skill: dict[str, str], body: str) -> str:
    name, tier = skill["name"], skill["tier"]
    lines = body.lstrip("\n").splitlines()
    heading = lines[0] if lines and lines[0].startswith("# ") else f"# {name}"
    rest = "\n".join(lines[1:] if lines and lines[0].startswith("# ") else lines)
    if tier == "principles":
        how = "Loads automatically whenever the agent touches code this principle governs."
    else:
        how = f"Invoke it in the AI chat with `/{name}`."
    callout = (
        f'!!! abstract "{TIER_LABEL[tier]} · `{name}`"\n'
        f"    {how} [Install the skills](../../getting-started.md) ·\n"
        f"    [View source]({REPO_URL}/blob/main/{skill['dir']}/SKILL.md)\n"
    )
    front = (
        "---\n"
        f"title: {yaml_str(heading[2:].strip() + ' — AI coding skill')}\n"
        f"description: {yaml_str(summary(skill['description'], 300))}\n"
        "---\n\n"
    )
    return f"{front}{heading}\n\n{callout}{rest}\n"


def skills_index(skills: list[dict[str, str]]) -> str:
    parts = [
        "---",
        "title: All skills",
        'description: "Every microservices skill in the library, by tier: principles that guard '
        'code automatically, workflows you invoke, and profiles that record your stack."',
        "---",
        "",
        "# All skills",
        "",
        "Principles load automatically when the agent touches code they govern. Workflows and "
        "profiles are invoked in the AI chat with a slash command.",
        "",
    ]
    for tier in TIERS:
        group = [s for s in skills if s["tier"] == tier]
        if not group:
            continue
        parts += [f"## {tier.capitalize()}", "", "| Skill | What it does |", "|---|---|"]
        for s in group:
            label = s["name"] if tier == "principles" else f"/{s['name']}"
            parts.append(f"| [`{label}`]({s['name']}/index.md) | {summary(s['description'])} |")
        parts.append("")
    return "\n".join(parts)


def write(site_path: str, content: str | bytes) -> None:
    dest = OUT / site_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        dest.write_bytes(content)
    else:
        dest.write_text(content)


def main() -> int:
    skills = collect_skills()
    if not skills:
        print("error: no skills found under source/", file=sys.stderr)
        return 1
    nav = (ROOT / "mkdocs.yml").read_text()
    missing = [s["name"] for s in skills if f"skills/{s['name']}/index.md" not in nav]
    if missing:
        print("error: skill(s) missing from the nav in mkdocs.yml: " + ", ".join(missing),
              file=sys.stderr)
        return 1
    mapping = build_map(skills)
    by_dir_skill = {f"{s['dir']}/SKILL.md": s for s in skills}

    if OUT.exists():
        shutil.rmtree(OUT)
    for repo_path, site_path in sorted(mapping.items()):
        source = ROOT / repo_path
        if source.suffix != ".md":
            write(site_path, source.read_bytes())
            continue
        text = rewrite_links(source.read_text(), repo_path, site_path, mapping)
        if repo_path in by_dir_skill:
            _, body = parse_frontmatter(text)
            text = skill_page(by_dir_skill[repo_path], body)
        write(site_path, text)
    write("skills/index.md", skills_index(skills))

    print(f"Assembled docs for {len(skills)} skills into {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
