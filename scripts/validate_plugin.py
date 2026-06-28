#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []
checks = 0

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

for rel in ['README.md', 'CLAUDE.md', 'config/kapelle.config.schema.json', 'dispatcher/task-context.schema.json']:
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
print(f'PASSED: {checks} checks; {len(skills)} skills; {len(agent_names)} agents')
