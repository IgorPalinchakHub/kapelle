#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import subprocess
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
    'docs/USAGE.md',
    'docs/COMMAND_EXECUTION_UK.md',
    'CLAUDE.md',
    'config/kapelle.config.schema.json',
    'dispatcher/task-context.schema.json',
    'dispatcher/task-plan.schema.json',
    'dispatcher/decomposition-review.schema.json',
    'dispatcher/surface-plan.schema.json',
    'dispatcher/architecture-guidance.schema.json',
    'dispatcher/execution-contract.md',
    'dispatcher/execution-verdict.schema.json',
    'dispatcher/test-strategy.schema.json',
    'dispatcher/execution-telemetry.schema.json',
    'dispatcher/validation-decision.schema.json',
    'dispatcher/change-request.schema.json',
    'dispatcher/change-revision.schema.json',
    'dispatcher/change-state.schema.json',
    'dispatcher/artifact-state.schema.json',
    'dispatcher/reconciliation.schema.json',
    'dispatcher/implementation-plan.schema.json',
    'dispatcher/artifact-dependencies.json',
    'dispatcher/feature-manifest.schema.json',
    'dispatcher/feature-state.schema.json',
    'dispatcher/recovery-report.schema.json',
    'dispatcher/documentation-convergence.schema.json',
    'dispatcher/size.schema.json',
    'dispatcher/feature-review.schema.json',
    'dispatcher/vocabulary.json',
    'dispatcher/role-profiles.json',
    'references/agent-orchestration.md',
    'references/project-capabilities.md',
    'references/architecture-guidance.md',
    'references/execution-depth.md',
    'references/validation-execution.md',
    'references/task-decomposition.md',
    'references/feature-layout.md',
    'references/artifact-presentation.md',
    'references/repository-context.md',
    'config/shapes/architecture-rules-agent.shape.md',
    'references/change-lifecycle.md',
    'scripts/artifact_fingerprint.py',
    'scripts/validate_task_plan.py',
    'scripts/test_validate_task_plan.py',
    'scripts/feature_state.py',
    'scripts/build_feature_status.py',
    'scripts/rebuild_feature_state.py',
    'scripts/validate_feature_state.py',
    'scripts/migrate_feature_layout.py',
    'scripts/test_feature_state.py',
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
    check(
        'handoff' in txt.lower() or name in {'decompose', 'implement', 'contracts', 'status'},
        f'{skill}: missing handoff wording',
    )
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
    'dispatcher/task-plan.schema.json',
    'dispatcher/decomposition-review.schema.json',
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
    'dispatcher/task-plan.schema.json',
    'dispatcher/decomposition-review.schema.json',
    'dispatcher/validation-decision.schema.json',
    'dispatcher/feature-manifest.schema.json',
    'dispatcher/feature-state.schema.json',
    'dispatcher/recovery-report.schema.json',
    'dispatcher/documentation-convergence.schema.json',
    'dispatcher/size.schema.json',
    'dispatcher/feature-review.schema.json',
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
    validation = config.get('properties', {}).get('validation', {})
    validation_policy = validation.get('properties', {}).get('development_policy', {})
    check(validation_policy.get('enum') == ['ask', 'allow', 'skip'],
          'config: validation.development_policy must support ask, allow, and skip')
    check(validation_policy.get('default') == 'ask',
          'config: validation.development_policy default must be ask')

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
    '--validation=ask|allow|skip',
    'validation-deferred',
    'validation-decision.schema.json',
    'tests, static analysis such as PHPStan, linters',
    'explicit user approval',
    'unofficial `Workflow`',
]:
    check(required in implementation_skill, f'implement: missing orchestration guard {required!r}')

validation_execution = (ROOT / 'references/validation-execution.md').read_text()
for required in [
    'ask` (default)',
    '`allow`',
    '`skip`',
    '`run-selected`',
    '`cancelled`',
    '`validation-deferred`',
    'REFUSED-validation-incomplete',
]:
    check(required in validation_execution,
          f'validation execution: missing policy guarantee {required!r}')

review_skill = (ROOT / 'skills/feature-review/SKILL.md').read_text()
check('BLOCKED-validation-deferred' in review_skill,
      'review: deferred validation must block PASS')
ship_skill = (ROOT / 'skills/ship/SKILL.md').read_text()
check('REFUSED-validation-incomplete' in ship_skill,
      'ship: incomplete validation must refuse readiness')

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

resume_skill = (ROOT / 'skills/resume-change/SKILL.md').read_text()
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
    for required in [
        'workstream_id',
        'primary_aspect',
        'aspects',
        'provides_contracts',
        'consumes_contracts',
        'integration_checks',
        'validation',
        'risk',
        'parallel_candidate',
        'ownership_status',
        'files_hint',
    ]:
        check(required in required_fields, f'tasks: {required} must be required')
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

task_plan_schema = load_json('dispatcher/task-plan.schema.json')
if task_plan_schema:
    required_fields = task_plan_schema.get('required', [])
    for required in ['decomposition_depth', 'architecture_guidance_path', 'workstreams', 'tasks']:
        check(required in required_fields, f'task plan: missing required field {required}')

decomposition_review_schema = load_json('dispatcher/decomposition-review.schema.json')
if decomposition_review_schema:
    statuses = decomposition_review_schema.get('properties', {}).get('status', {}).get('enum', [])
    check(statuses == ['PASS', 'CHANGES_REQUESTED', 'BLOCKED'],
          'decomposition review: invalid statuses')

task_plan_example = load_json('examples/task-plan.json')
check((ROOT / 'examples/task-plan-spec.md').exists(), 'missing examples/task-plan-spec.md')
if task_plan_example:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / 'scripts/validate_task_plan.py'),
            '--tasks',
            str(ROOT / 'examples/task-plan.json'),
            '--surface-plan',
            str(ROOT / 'examples/surface-plan.json'),
            '--spec',
            str(ROOT / 'examples/task-plan-spec.md'),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    check(result.returncode == 0,
          f"task plan fixture failed semantic validation: {result.stdout}{result.stderr}")
    unit_result = subprocess.run(
        [
            sys.executable,
            '-m',
            'unittest',
            'discover',
            '-s',
            str(ROOT / 'scripts'),
            '-p',
            'test_*.py',
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    check(unit_result.returncode == 0,
          f"task plan validator tests failed: {unit_result.stdout}{unit_result.stderr}")

dependencies = load_json('dispatcher/artifact-dependencies.json')
if dependencies:
    for required in [
        'proposal.md',
        'spec.md',
        'design.md',
        '_kapelle/surface-plan.json',
        'tasks.md',
        '_kapelle/task-plan.json',
        'test-plan.md',
        '_kapelle/validation',
        '_kapelle/reviews/documentation-convergence.json',
        '_kapelle/reviews/feature-review.json',
        '_kapelle/state.json',
        'STATUS.md',
    ]:
        check(required in dependencies, f'artifact graph: missing {required}')
    for legacy in ['sad.md', 'surface-plan.json', 'tasks.json', 'ship.md']:
        check(legacy not in dependencies, f'artifact graph: legacy key {legacy}')

feature_manifest_schema = load_json('dispatcher/feature-manifest.schema.json')
feature_state_schema = load_json('dispatcher/feature-state.schema.json')
recovery_schema = load_json('dispatcher/recovery-report.schema.json')
convergence_schema = load_json('dispatcher/documentation-convergence.schema.json')
if feature_manifest_schema:
    check(feature_manifest_schema.get('properties', {}).get('layout_version', {}).get('const') == 2,
          'feature manifest: layout_version must be 2')
if feature_state_schema:
    feature_state_enum = (
        feature_state_schema.get('properties', {}).get('feature_state', {}).get('enum', [])
    )
    for required in [
        'recovered',
        'recovered-with-gaps',
        'external-development',
        'externally-implemented-unverified',
    ]:
        check(required in feature_state_enum, f'feature state: missing {required}')
if recovery_schema:
    dispositions = (
        recovery_schema.get('properties', {})
        .get('task_dispositions', {})
        .get('additionalProperties', {})
        .get('enum', [])
    )
    check('implemented-unverified' in dispositions,
          'recovery report: missing implemented-unverified disposition')
if convergence_schema:
    statuses = convergence_schema.get('properties', {}).get('status', {}).get('enum', [])
    check(statuses == ['PASS', 'CHANGES_REQUIRED', 'BLOCKED'],
          'documentation convergence: invalid statuses')

for required in [
    'references/feature-layout.md',
    'references/artifact-presentation.md',
    'skills/status/SKILL.md',
]:
    check((ROOT / required).exists(), f'layout-v2: missing {required}')

for skill in skills:
    if skill.parent.name == 'status':
        continue
    text = skill.read_text()
    check('_audit/' not in text and '_review/' not in text,
          f'{skill.relative_to(ROOT)}: writes legacy internal path')
    check('docs/features/<slug>/changes/' not in text,
          f'{skill.relative_to(ROOT)}: writes legacy change path')

design_skill = (ROOT / 'skills/design/SKILL.md').read_text()
for required in [
    'architecture-rules subagent',
    'architecture-guidance.schema.json',
    'surface-plan.schema.json',
    'execution-depth.md',
]:
    check(required in design_skill, f'design: missing scoped architecture/surface guard {required!r}')

specify_skill = (ROOT / 'skills/specify/SKILL.md').read_text()
for required in [
    'bounded input preflight',
    'authoritative slug/ticket',
    'consolidated interaction',
    'Status: NEEDS-INPUT',
    'do not run git/shell discovery',
    'dispatch subagents',
    'Do not create `docs/features/<slug>/`',
    'Broad code mapping',
]:
    check(required in specify_skill, f'specify: missing input-efficiency guard {required!r}')

tasks_skill = (ROOT / 'skills/decompose/SKILL.md').read_text()
for required in [
    'task-decomposition.md',
    'architecture-rules subagent',
    'BLOCKED-split-required',
    'workstreams',
    'one primary aspect',
    'validate_task_plan.py',
    'decomposition-review.schema.json',
    'exactly one fresh `kapelle:critic`',
    'one correction pass',
]:
    check(required in tasks_skill, f'tasks: missing decomposition guard {required!r}')

for rel in [
    'skills/implement/SKILL.md',
    'dispatcher/dispatcher.md',
    'dispatcher/execution-contract.md',
]:
    text = (ROOT / rel).read_text()
    check('architecture-rules subagent' in text,
          f'{rel}: missing project architecture-rules capability')
    check('surface-plan' in text, f'{rel}: missing multi-aspect coordination')

survey_skill = (ROOT / 'skills/survey/SKILL.md').read_text()
for required in [
    'reflects_commit',
    'provenance only',
    '_context/architecture.md',
    '--refresh-baseline',
    'never create or update',
    'even when the shared baseline is missing',
]:
    check(required in survey_skill, f'survey: missing worktree-safety guard {required!r}')

usage = (ROOT / 'docs/USAGE.md').read_text()
for required in [
    '/kapelle:survey <slug>',
    '/kapelle:survey --refresh-baseline',
    '/kapelle:specify <slug>',
    '/kapelle:change',
    '--mode=enhancement',
    '--mode=bugfix',
    '--mode=refactor',
    '--revise',
    '/kapelle:resume-change',
    '_kapelle/surface-plan.json',
    '/kapelle:status <slug>',
    'REFUSED-missing-project-capability',
]:
    check(required in usage, f'usage guide: missing workflow detail {required!r}')

command_guide = (ROOT / 'docs/COMMAND_EXECUTION_UK.md').read_text()
for required in [
    '/kapelle:survey',
    '/kapelle:specify <slug>',
    '/kapelle:clarify <slug>',
    '/kapelle:design <slug>',
    '/kapelle:sequences <slug>',
    '/kapelle:data-model <slug>',
    '/kapelle:contracts <slug>',
    '/kapelle:decompose <slug>',
    '/kapelle:plan-tests <slug>',
    '/kapelle:implement <slug>',
    '/kapelle:feature-review <slug>',
    '/kapelle:ship <slug>',
    '/kapelle:change',
    '/kapelle:fix',
    '/kapelle:resume-change',
    '/kapelle:classify-size <slug>',
    '/kapelle:glossary <slug>',
    '/kapelle:decide-adr <slug>',
    '/kapelle:roadmap <slug>',
    '/kapelle:status <slug>',
    'Що задати на вході',
    'Що отримуємо',
]:
    check(required in command_guide, f'command guide: missing detail {required!r}')

vocabulary = load_json('dispatcher/vocabulary.json')
if vocabulary:
    task_states = vocabulary.get('task_states', [])
    dispositions = vocabulary.get('reconciliation_dispositions', [])
    change_states = vocabulary.get('change_states', [])
    skill_names = {skill.parent.name for skill in skills}

    if task_schema:
        check(task_schema.get('properties', {}).get('status', {}).get('enum') == task_states,
              'vocabulary: task-context status enum drifted from task_states')
    if feature_state_schema:
        check(
            feature_state_schema.get('properties', {}).get('feature_state', {}).get('enum')
            == vocabulary.get('feature_states'),
            'vocabulary: feature-state enum drifted from feature_states',
        )
    if recovery_schema:
        check(
            recovery_schema.get('properties', {})
            .get('task_dispositions', {})
            .get('additionalProperties', {})
            .get('enum')
            == vocabulary.get('recovery_task_dispositions'),
            'vocabulary: recovery dispositions drifted from recovery_task_dispositions',
        )
    artifact_state_schema = load_json('dispatcher/artifact-state.schema.json')
    if artifact_state_schema:
        check(artifact_state_schema.get('properties', {}).get('status', {}).get('enum')
              == vocabulary.get('artifact_states'),
              'vocabulary: artifact-state status enum drifted from artifact_states')
    implementation_plan_schema = load_json('dispatcher/implementation-plan.schema.json')
    if implementation_plan_schema:
        check(implementation_plan_schema.get('properties', {}).get('status', {}).get('enum')
              == vocabulary.get('implementation_plan_states'),
              'vocabulary: implementation-plan status enum drifted from implementation_plan_states')
    change_state_schema = load_json('dispatcher/change-state.schema.json')
    if change_state_schema:
        check(change_state_schema.get('properties', {}).get('state', {}).get('enum') == change_states,
              'vocabulary: change-state enum drifted from change_states')
    reconciliation_schema = load_json('dispatcher/reconciliation.schema.json')
    if reconciliation_schema:
        schema_dispositions = (
            reconciliation_schema.get('properties', {})
            .get('tasks', {})
            .get('additionalProperties', {})
            .get('properties', {})
            .get('disposition', {})
            .get('enum')
        )
        check(schema_dispositions == dispositions,
              'vocabulary: reconciliation disposition enum drifted from reconciliation_dispositions')
    change_request_schema = load_json('dispatcher/change-request.schema.json')
    if change_request_schema:
        route_stages = (
            change_request_schema.get('properties', {})
            .get('route', {})
            .get('items', {})
            .get('enum')
        )
        check(route_stages == vocabulary.get('change_route_stages'),
              'vocabulary: change-request route enum drifted from change_route_stages')

    mapping = vocabulary.get('disposition_to_task_state', {})
    check(list(mapping) == dispositions,
          'vocabulary: disposition_to_task_state keys must equal reconciliation_dispositions')
    check(set(mapping.values()) <= set(task_states),
          'vocabulary: disposition_to_task_state values must be task states')
    transitions = vocabulary.get('change_state_transitions', {})
    check(list(transitions) == change_states,
          'vocabulary: change_state_transitions must cover every change state')
    for source, targets in transitions.items():
        check(set(targets) <= set(change_states),
              f'vocabulary: unknown transition target from {source}')
    check(set(vocabulary.get('backbone_stages', [])) <= skill_names,
          'vocabulary: every backbone stage must be a bundled skill')
    check(set(vocabulary.get('change_route_stages', [])) <= skill_names,
          'vocabulary: every change route stage must be a bundled skill')

    state_only_terms = ['needs-rework', 'superseded']
    for path in sorted(ROOT.rglob('*.md')):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in {'.git', '.idea'}:
            continue
        for line_number, line in enumerate(path.read_text(errors='ignore').splitlines(), 1):
            if 'disposition' not in line.lower():
                continue
            for term in state_only_terms:
                check(term not in line,
                      f'{rel}:{line_number}: task state {term!r} used in disposition context')

role_profiles = load_json('dispatcher/role-profiles.json')
if role_profiles:
    reasoning_levels = set(role_profiles.get('reasoning_levels', []))
    cost_tiers = set(role_profiles.get('cost_tiers', []))
    skill_names = {skill.parent.name for skill in skills}
    profile_agents = role_profiles.get('agents', {})
    profile_stages = role_profiles.get('stages', {})
    check(set(profile_agents) == agent_names,
          'role profiles: agents must exactly cover bundled agents')
    check(set(profile_stages) == skill_names,
          'role profiles: stages must exactly cover bundled skills')
    for name, profile in {**profile_agents, **profile_stages}.items():
        check(profile.get('reasoning') in reasoning_levels,
              f'role profiles: {name} has invalid reasoning level')
        check(profile.get('cost') in cost_tiers,
              f'role profiles: {name} has invalid cost tier')

for path in sorted((ROOT / 'agents').glob('*.md')) + skills:
    txt = path.read_text()
    check(not re.search(r'^(model|effort):', txt, re.M),
          f'{path.relative_to(ROOT)}: provider-specific model/effort pin in core definition')

stage_contract = (ROOT / 'references/stage-contract.md').read_text()
for required in [
    'single canonical stage contract',
    '`requires`',
    '`produces`',
    'REFUSED-missing-input',
    'SKIPPED-confirmed',
    '--change=<change-id>',
]:
    check(required in stage_contract, f'stage contract: missing {required!r}')
stage_contract_pointer = (ROOT / 'stages/_stage-contract.md').read_text()
check('references/stage-contract.md' in stage_contract_pointer,
      'stages/_stage-contract.md must point to the canonical stage contract')
check('REFUSED-missing-input' not in stage_contract_pointer
      and len(stage_contract_pointer.splitlines()) <= 10,
      'stages/_stage-contract.md must remain a pointer, not a second contract')

if config:
    check('providers' in config.get('properties', {}),
          'config: missing providers adapter section')
    role_binding = config.get('$defs', {}).get('role_binding', {})
    check(set(role_binding.get('properties', {})) == {'//', 'model', 'effort'},
          'config: role_binding must allow only model and effort')
example_config = load_json('examples/kapelle.config.json')
if example_config and role_profiles:
    skill_names = {skill.parent.name for skill in skills}
    for provider_name, provider in example_config.get('providers', {}).items():
        check(set(provider.get('roles', {})) <= agent_names,
              f'example config: provider {provider_name} binds unknown role')
        check(set(provider.get('stages', {})) <= skill_names,
              f'example config: provider {provider_name} binds unknown stage')

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
