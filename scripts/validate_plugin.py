#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []
checks = 0
RESOURCE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')

def check(ok: bool, msg: str):
    global checks
    checks += 1
    if not ok:
        errors.append(msg)


def load_json(rel: str):
    p = ROOT / rel
    check(p.exists(), f"missing {rel}")
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        errors.append(f"{rel} invalid JSON: {exc}")
        return None

for rel in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json']:
    data = load_json(rel)
    if data:
        check(data.get('name') == 'kapelle', f"{rel}: name must be kapelle")
        check(bool(re.match(r'^\d+\.\d+\.\d+$', data.get('version', ''))), f"{rel}: version must be semver")
        check(bool(data.get('description')), f"{rel}: missing description")

marketplace = load_json('.claude-plugin/marketplace.json')
if marketplace:
    check(marketplace.get('name') == 'kapelle-marketplace', 'marketplace name must be kapelle-marketplace')
    check(bool(marketplace.get('description')), 'marketplace description missing')
    entries = marketplace.get('plugins', [])
    check(len(entries) == 1, 'marketplace must contain exactly one plugin')
    if entries:
        check(entries[0].get('name') == 'kapelle', 'marketplace plugin name must be kapelle')
        check(entries[0].get('source') == './', 'marketplace plugin source must be ./')

for rel in ['README.md', 'CLAUDE.md', 'config/kapelle.config.schema.json', 'config/pack.manifest.schema.json', 'dispatcher/task-context.schema.json', 'scripts/install_project_pack.py']:
    check((ROOT / rel).exists(), f"missing {rel}")

skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
check(bool(skills), 'no Claude skills found')
for skill in skills:
    txt = skill.read_text()
    name = skill.parent.name
    check(txt.startswith('---'), f'{skill}: missing frontmatter')
    check(f'name: {name}' in txt, f'{skill}: frontmatter name mismatch')
    check('description:' in txt, f'{skill}: missing description')
    check('stage-handoff block' in txt or name in {'tasks', 'implement', 'contracts'}, f'{skill}: missing handoff wording')

agent_names = {p.stem for p in (ROOT / 'agents').glob('*.md')}
for skill in skills:
    txt = skill.read_text()
    m = re.search(r'^agents:\s*\[(.*?)\]', txt, re.M)
    if m:
        for raw in m.group(1).split(','):
            a = raw.strip()
            if a:
                check(a in agent_names, f'{skill}: unknown agent {a}')

for pack in sorted((ROOT / 'packs').glob('*/pack.manifest.json')):
    data = load_json(str(pack.relative_to(ROOT)))
    if not data:
        continue
    for key in ['id', 'version']:
        check(key in data, f'{pack}: missing {key}')
    check(not (set(data) - {'id', 'version', 'description'}), f'{pack}: runtime metadata is forbidden')
    check(bool(RESOURCE_NAME.fullmatch(data.get('id', ''))), f'{pack}: invalid id')
    check(bool(re.match(r'^\d+\.\d+\.\d+$', data.get('version', ''))), f'{pack}: invalid version')
    pack_skills = sorted((pack.parent / 'skills').glob('*.md'))
    check(bool(pack_skills), f'{pack}: no installable skills')
    for source_template in pack_skills:
        skill_name = source_template.stem
        source_text = source_template.read_text()
        check(source_text.startswith('---'), f'{source_template}: missing native skill frontmatter')
        check(f'name: {skill_name}' in source_text, f'{source_template}: native skill name mismatch')
    for agent in sorted((pack.parent / 'agents').glob('*.md')):
        check(agent.read_text().startswith('---'), f'{agent}: missing native agent frontmatter')

for rel in ['config/kapelle.config.schema.json', 'dispatcher/task-context.schema.json']:
    data = load_json(rel)
    if data:
        text = json.dumps(data)
        check('"spec"' not in text, f'{rel}: stale phase spec present')

for forbidden in [
    'rule_query',
    'must_rules',
    'surface_bindings',
    'ai-mcp docs search',
    'routing-tag.schema.json',
]:
    offenders = [
        str(path.relative_to(ROOT))
        for path in ROOT.rglob('*')
        if path.is_file()
        and path != Path(__file__).resolve()
        and forbidden in path.read_text(errors='ignore')
    ]
    check(not offenders, f'forbidden runtime coupling {forbidden!r} in {offenders}')

if errors:
    print(f'FAILED: {len(errors)} error(s) out of {checks} checks')
    for e in errors:
        print(f'- {e}')
    sys.exit(1)
print(f'PASSED: {checks} checks; {len(skills)} skills; {len(agent_names)} agents; {len(list((ROOT/"packs").glob("*/pack.manifest.json")))} packs')
