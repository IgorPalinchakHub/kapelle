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

manifest_versions = []
for rel in ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json']:
    data = load_json(rel)
    if data:
        check(data.get('name') == 'kapelle', f"{rel}: name must be kapelle")
        check(bool(re.match(r'^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$',
                            data.get('version', ''))),
              f"{rel}: version must be semver")
        check(bool(data.get('description')), f"{rel}: missing description")
        manifest_versions.append(data.get('version'))
base_manifest_versions = [version.split('+', 1)[0] for version in manifest_versions if version]
check(len(set(base_manifest_versions)) == 1,
      'Claude and Codex manifest base versions must match')

marketplace = load_json('.claude-plugin/marketplace.json')
if marketplace:
    check(marketplace.get('name') == 'kapelle-marketplace', 'marketplace name must be kapelle-marketplace')
    check(bool(marketplace.get('description')), 'marketplace description missing')
    entries = marketplace.get('plugins', [])
    check(len(entries) == 1, 'marketplace must contain exactly one plugin')
    if entries:
        check(entries[0].get('name') == 'kapelle', 'marketplace plugin name must be kapelle')
        check(entries[0].get('source') == './', 'marketplace plugin source must be ./')

for rel in [
    'README.md',
    'CLAUDE.md',
    'config/kapelle.config.schema.json',
    'dispatcher/task-context.schema.json',
    'dispatcher/surface-plan.schema.json',
    'dispatcher/architecture-guidance.schema.json',
    'dispatcher/execution-contract.md',
    'dispatcher/execution-verdict.schema.json',
    'dispatcher/test-strategy.schema.json',
    'dispatcher/execution-telemetry.schema.json',
    'dispatcher/change-request.schema.json',
    'dispatcher/change-revision.schema.json',
    'dispatcher/change-state.schema.json',
    'dispatcher/artifact-state.schema.json',
    'dispatcher/reconciliation.schema.json',
    'dispatcher/implementation-plan.schema.json',
    'dispatcher/artifact-dependencies.json',
    'references/agent-orchestration.md',
    'references/project-capabilities.md',
    'references/architecture-guidance.md',
    'references/execution-depth.md',
    'config/shapes/architecture-rules-agent.shape.md',
    'references/change-lifecycle.md',
    'scripts/artifact_fingerprint.py',
]:
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
    check(not re.search(r'^agents:', txt, re.M), f'{skill}: unsupported agents frontmatter')

agent_names = {p.stem for p in (ROOT / 'agents').glob('*.md')}
orchestration_text = '\n'.join(
    path.read_text()
    for path in [
        ROOT / 'references/agent-orchestration.md',
        ROOT / 'dispatcher/execution-contract.md',
    ]
)
for agent in sorted(agent_names):
    check(f'`{agent}`' in orchestration_text or f'kapelle:{agent}' in orchestration_text,
          f'agent {agent}: missing orchestration contract')

for rel in [
    'config/kapelle.config.schema.json',
    'dispatcher/task-context.schema.json',
    'dispatcher/surface-plan.schema.json',
    'dispatcher/architecture-guidance.schema.json',
    'dispatcher/execution-verdict.schema.json',
    'dispatcher/test-strategy.schema.json',
    'dispatcher/execution-telemetry.schema.json',
]:
    data = load_json(rel)
    if data:
        text = json.dumps(data)
        check('"spec"' not in text, f'{rel}: stale phase spec present')

load_json('dispatcher/change-request.schema.json')
for rel in [
    'dispatcher/change-revision.schema.json',
    'dispatcher/change-state.schema.json',
    'dispatcher/artifact-state.schema.json',
    'dispatcher/reconciliation.schema.json',
    'dispatcher/implementation-plan.schema.json',
    'dispatcher/artifact-dependencies.json',
]:
    load_json(rel)

config = load_json('config/kapelle.config.schema.json')
if config:
    implementation = config.get('properties', {}).get('implementation', {})
    mode = implementation.get('properties', {}).get('mode', {})
    check(mode.get('enum') == ['sequential', 'agent-team'],
          'config: implementation.mode must support sequential and agent-team only')
    props = implementation.get('properties', {})
    check(props.get('approval_policy', {}).get('enum') == ['always', 'risk-based', 'never'],
          'config: invalid implementation.approval_policy')
    check(props.get('max_task_attempts', {}).get('default') == 3,
          'config: max_task_attempts default must be 3')
    check(props.get('max_agent_runs_per_task', {}).get('default') == 8,
          'config: max_agent_runs_per_task default must be 8')

implementation_skill = (ROOT / 'skills/implement/SKILL.md').read_text()
for required in [
    'kapelle:test-author',
    'kapelle:implementation-planner',
    'kapelle:implementer',
    'kapelle:reviewer',
    'TEST-STRATEGY',
    'PLAN -> APPROVE',
    'max_task_attempts',
    'max_agent_runs_per_task',
    'explicit user approval',
    'unofficial `Workflow`',
]:
    check(required in implementation_skill, f'implement: missing orchestration guard {required!r}')

change_skill = (ROOT / 'skills/change/SKILL.md').read_text()
for required in [
    'bugfix',
    'enhancement',
    'refactor',
    'kapelle:explorer',
    'kapelle:critic',
    'change-request.schema.json',
    'approve',
    'progress.jsonl',
    '--revise',
    'change-reconciler',
    'reconciliation.schema.json',
]:
    check(required in change_skill, f'change: missing lifecycle contract {required!r}')

fix_skill = (ROOT / 'skills/fix/SKILL.md').read_text()
check('mode: bugfix' in fix_skill, 'fix: must be a bugfix change-lifecycle shorthand')

resume_skill = (ROOT / 'skills/resume/SKILL.md').read_text()
for required in [
    'resumable',
    'artifact_fingerprint.py',
    'reconciliation',
    'needs-rework',
    'kapelle:implement',
]:
    check(required in resume_skill, f'resume: missing revision guard {required!r}')

task_schema = load_json('dispatcher/task-context.schema.json')
if task_schema:
    statuses = task_schema.get('properties', {}).get('status', {}).get('enum', [])
    for required in ['stale', 'needs-rework', 'superseded']:
        check(required in statuses, f'tasks: missing reconciliation status {required}')
    required_fields = task_schema.get('required', [])
    check('aspects' in required_fields, 'tasks: aspects must be required')
    check('surface_hint' not in task_schema.get('properties', {}),
          'tasks: stale single surface_hint must be removed')

surface_schema = load_json('dispatcher/surface-plan.schema.json')
if surface_schema:
    required_fields = surface_schema.get('required', [])
    for required in ['aspects', 'contracts', 'integration_checks']:
        check(required in required_fields, f'surface plan: missing required field {required}')

architecture_schema = load_json('dispatcher/architecture-guidance.schema.json')
if architecture_schema:
    statuses = architecture_schema.get('properties', {}).get('status', {}).get('enum', [])
    check('ARCHITECTURE_GUIDANCE_READY' in statuses,
          'architecture guidance: missing ready status')
    capability_kind = (
        architecture_schema.get('properties', {})
        .get('capability', {})
        .get('properties', {})
        .get('kind', {})
        .get('const')
    )
    check(capability_kind == 'project-subagent',
          'architecture guidance: capability must be a project subagent')

surface_example = load_json('examples/surface-plan.json')
if surface_example:
    aspect_ids = {item.get('id') for item in surface_example.get('aspects', [])}
    check(bool(aspect_ids), 'surface example: no aspects')
    for aspect in surface_example.get('aspects', []):
        check(set(aspect.get('depends_on', [])).issubset(aspect_ids),
              f"surface example: unknown dependency in {aspect.get('id')}")
    for contract in surface_example.get('contracts', []):
        participants = {contract.get('provider_aspect'), *contract.get('consumer_aspects', [])}
        check(participants.issubset(aspect_ids),
              f"surface example: unknown contract participant in {contract.get('id')}")
    for integration in surface_example.get('integration_checks', []):
        check(set(integration.get('aspects', [])).issubset(aspect_ids),
              f"surface example: unknown integration participant in {integration.get('id')}")

architecture_example = load_json('examples/architecture-guidance.json')
if architecture_example:
    check(architecture_example.get('status') == 'ARCHITECTURE_GUIDANCE_READY',
          'architecture example: must be ready')
    check(not architecture_example.get('gaps'), 'architecture example: must have no gaps')

dependencies = load_json('dispatcher/artifact-dependencies.json')
if dependencies:
    check('surface-plan.json' in dependencies, 'artifact graph: missing surface-plan.json')
    check('sequences.md' in dependencies, 'artifact graph: missing sequences.md')
    check('sequences' not in dependencies, 'artifact graph: stale logical sequences key')

design_skill = (ROOT / 'skills/design/SKILL.md').read_text()
for required in [
    'architecture-rules subagent',
    'architecture-guidance.schema.json',
    'surface-plan.schema.json',
    'execution-depth.md',
]:
    check(required in design_skill, f'design: missing scoped architecture/surface guard {required!r}')

for rel in [
    'skills/implement/SKILL.md',
    'dispatcher/dispatcher.md',
    'dispatcher/execution-contract.md',
]:
    text = (ROOT / rel).read_text()
    check('architecture-rules subagent' in text,
          f'{rel}: missing project architecture-rules capability')
    check('surface-plan' in text, f'{rel}: missing multi-aspect coordination')

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
