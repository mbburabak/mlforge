#!/usr/bin/env python3
"""Validate plugin structure, manifests, frontmatter, and cross-references."""
import json
import glob
import os
import re
import sys

errors = []
warnings = []
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def check_manifests():
    pj = json.load(open(".claude-plugin/plugin.json"))
    mp = json.load(open(".claude-plugin/marketplace.json"))
    if not KEBAB.match(pj["name"]):
        errors.append("plugin.json name not kebab-case")
    if not KEBAB.match(mp["name"]):
        errors.append("marketplace.json name not kebab-case")
    entry = mp["plugins"][0]
    if entry["name"] != pj["name"]:
        errors.append("marketplace plugin name != plugin.json name")
    if entry.get("version") != pj.get("version"):
        errors.append(f"version mismatch: marketplace {entry.get('version')} vs plugin {pj.get('version')}")
    if not entry["source"].startswith("./"):
        errors.append("plugin source must be a relative path starting with ./")
    return pj


def parse_frontmatter(path):
    text = open(path).read()
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


def check_skills():
    names = set()
    for path in sorted(glob.glob("skills/*/SKILL.md")):
        d = os.path.basename(os.path.dirname(path))
        fm = parse_frontmatter(path)
        if fm is None:
            errors.append(f"{path}: missing/malformed frontmatter")
            continue
        m = re.search(r"^name:\s*(\S+)", fm, re.M)
        if not m:
            errors.append(f"{path}: no name in frontmatter")
            continue
        name = m.group(1)
        names.add(name)
        if name != d:
            errors.append(f"{path}: name '{name}' != directory '{d}'")
        if not KEBAB.match(name):
            errors.append(f"{path}: name not kebab-case")
        if "description:" not in fm:
            errors.append(f"{path}: no description in frontmatter")
        body = open(path).read().split("---", 2)[2]
        wc = len(body.split())
        if wc > 3000:
            warnings.append(f"{path}: body {wc} words (>3000 — consider references/)")
    return names


def check_agents():
    names = set()
    for path in sorted(glob.glob("agents/*.md")):
        fm = parse_frontmatter(path)
        if fm is None:
            errors.append(f"{path}: missing/malformed frontmatter")
            continue
        for field in ("name:", "description:", "model:", "color:"):
            if field not in fm:
                errors.append(f"{path}: missing '{field}' in frontmatter")
        m = re.search(r"^name:\s*(\S+)", fm, re.M)
        if m:
            names.add(m.group(1))
    return names


def check_cross_references(skill_names, agent_names):
    known = skill_names | agent_names
    ref_pat = re.compile(r"`(ml-[a-z-]+|experiment-design|model-evaluation|tech-leadership|llm-engineering)`")
    for path in sorted(glob.glob("skills/*/SKILL.md")) + sorted(glob.glob("agents/*.md")):
        body = open(path).read()
        for ref in set(ref_pat.findall(body)):
            if ref not in known:
                errors.append(f"{path}: references unknown skill/agent `{ref}`")


def check_reference_files():
    for path in sorted(glob.glob("skills/*/SKILL.md")):
        body = open(path).read()
        for ref in re.findall(r"`references/([\w.-]+)`", body):
            full = os.path.join(os.path.dirname(path), "references", ref)
            if not os.path.exists(full):
                errors.append(f"{path}: references/{ref} does not exist")


def check_hooks():
    path = "hooks/hooks.json"
    if not os.path.exists(path):
        return
    try:
        cfg = json.load(open(path))
    except json.JSONDecodeError as e:
        errors.append(f"{path}: invalid JSON — {e}")
        return
    for event, matchers in cfg.items():
        for m in matchers:
            for h in m.get("hooks", []):
                cmd = h.get("command", "")
                for token in cmd.split():
                    if "${CLAUDE_PLUGIN_ROOT}" in token:
                        rel = token.replace("${CLAUDE_PLUGIN_ROOT}/", "")
                        if not os.path.exists(rel):
                            errors.append(f"{path}: {event} references missing script {rel}")


pj = check_manifests()
check_hooks()
skill_names = check_skills()
agent_names = check_agents()
check_cross_references(skill_names, agent_names)
check_reference_files()

print(f"mlforge {pj.get('version')}: {len(skill_names)} skills, {len(agent_names)} agents")
for w in warnings:
    print(f"  WARN  {w}")
for e in errors:
    print(f"  ERROR {e}")
print("FAIL" if errors else "OK")
sys.exit(1 if errors else 0)
