#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema_lite import audit_schema, validate_file

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
    'AGENTS.md',
    'config/kapelle.config.schema.json',
    'dispatcher/task-context.schema.json',
    'dispatcher/task-plan.schema.json',
    'dispatcher/decomposition-review.schema.json',
    'dispatcher/surface-plan.schema.json',
    'dispatcher/architecture-guidance.schema.json',
    'dispatcher/execution-contract.md',
    'dispatcher/execution-verdict.schema.json',
    'dispatcher/execution-telemetry.schema.json',
    'dispatcher/validation-decision.schema.json',
    'dispatcher/change-request.schema.json',
    'dispatcher/change-revision.schema.json',
    'dispatcher/change-state.schema.json',
    'dispatcher/artifact-state.schema.json',
    'dispatcher/reconciliation.schema.json',
    'dispatcher/implementation-plan.schema.json',
    'dispatcher/artifact-dependencies.json',
    'dispatcher/schema-lifecycle.json',
    'dispatcher/feature-manifest.schema.json',
    'dispatcher/feature-state.schema.json',
    'dispatcher/recovery-report.schema.json',
    'dispatcher/size.schema.json',
    'dispatcher/vocabulary.json',
    'dispatcher/role-profiles.json',
    'dispatcher/workflow-state.schema.json',
    'dispatcher/reconstruction.schema.json',
    'dispatcher/reconstruction-coverage.schema.json',
    'dispatcher/review-gate.schema.json',
    'dispatcher/base-functional-tests.schema.json',
    'dispatcher/unit-test-run.schema.json',
    'dispatcher/verification.schema.json',
    'dispatcher/release.schema.json',
    'references/agent-orchestration.md',
    'references/utility-contract.md',
    'references/project-capabilities.md',
    'references/architecture-guidance.md',
    'references/execution-depth.md',
    'references/validation-execution.md',
    'references/task-decomposition.md',
    'references/feature-layout.md',
    'references/artifact-presentation.md',
    'references/human-control.md',
    'references/fast-lane.md',
    'references/interview-depth.md',
    'references/design-template.md',
    'references/design-execution.md',
    'references/progressive-artifacts.md',
    'references/reconstruction.md',
    'references/deprecated-legacy-stages.md',
    'references/repository-context.md',
    'config/shapes/architecture-rules-agent.shape.md',
    'references/change-lifecycle.md',
    'references/developer-questions.md',
    'references/json-schema-validation.md',
    'references/script-execution.md',
    'scripts/artifact_fingerprint.py',
    'scripts/jsonschema_lite.py',
    'scripts/validate_json.py',
    'scripts/test_jsonschema_lite.py',
    'scripts/validate_task_plan.py',
    'scripts/test_validate_task_plan.py',
    'scripts/feature_state.py',
    'scripts/build_feature_status.py',
    'scripts/rebuild_feature_state.py',
    'scripts/record_verification.py',
    'scripts/validate_feature_state.py',
    'scripts/migrate_feature_layout.py',
    'scripts/test_feature_state.py',
    'scripts/validate_design.py',
    'scripts/test_validate_design.py',
    'scripts/validate_progressive_docs.py',
    'scripts/test_validate_progressive_docs.py',
    'scripts/validate_architecture_package.py',
    'scripts/test_validate_architecture_package.py',
    'scripts/review_gate.py',
    'scripts/test_review_gate.py',
    'scripts/migrate_workflow.py',
    'scripts/test_migrate_workflow.py',
]:
    check((ROOT / rel).exists(), f"missing {rel}")

dispatcher_schemas = sorted((ROOT / 'dispatcher').glob('*.schema.json'))
schema_lifecycle = load_json('dispatcher/schema-lifecycle.json')
schema_names = {path.name for path in dispatcher_schemas}
expected_schema_groups = {
    'core-runtime',
    'optional-agent-runtime',
    'reconstruction',
    'migration-compatibility',
}
classified_schema_names: list[str] = []
if schema_lifecycle:
    check(schema_lifecycle.get('version') == 1,
          'schema lifecycle: version must be 1')
    schema_groups = schema_lifecycle.get('groups', {})
    check(set(schema_groups) == expected_schema_groups,
          'schema lifecycle: groups must match the canonical lifecycle groups')
    for group_name in sorted(expected_schema_groups):
        group = schema_groups.get(group_name, [])
        check(isinstance(group, list) and bool(group),
              f'schema lifecycle: {group_name} must be a non-empty array')
        if isinstance(group, list):
            classified_schema_names.extend(group)
    check(len(classified_schema_names) == len(set(classified_schema_names)),
          'schema lifecycle: a schema may belong to only one group')
    check(set(classified_schema_names) == schema_names,
          'schema lifecycle: every dispatcher schema must be classified exactly once')
    policy = schema_lifecycle.get('policy', {})
    check(set(policy) == expected_schema_groups,
          'schema lifecycle: every group must have a policy')

compatibility_schemas = set()
if schema_lifecycle:
    compatibility_schemas = set(
        schema_lifecycle.get('groups', {}).get('migration-compatibility', [])
    )
backbone_text = '\n'.join(
    (ROOT / 'skills' / name / 'SKILL.md').read_text()
    for name in ('start', 'implement', 'verify', 'amend', 'status')
)
for schema_name in sorted(compatibility_schemas):
    check(schema_name not in backbone_text,
          f'schema lifecycle: lightweight backbone must not require compatibility schema {schema_name}')
for schema_path in dispatcher_schemas:
    for schema_error in audit_schema(schema_path):
        check(False, f'{schema_path.relative_to(ROOT)}: unsupported schema: {schema_error}')

for instance_name, schema_name in [
    ('surface-plan.json', 'surface-plan.schema.json'),
    ('architecture-guidance.json', 'architecture-guidance.schema.json'),
    ('task-plan.json', 'task-plan.schema.json'),
]:
    for schema_error in validate_file(
        ROOT / 'examples' / instance_name,
        ROOT / 'dispatcher' / schema_name,
    ):
        check(
            False,
            f'examples/{instance_name}: structural validation failed: {schema_error}',
        )

skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
check(bool(skills), 'no Claude skills found')
script_skills: list[Path] = []
for skill in skills:
    txt = skill.read_text()
    name = skill.parent.name
    check(txt.startswith('---'), f'{skill}: missing frontmatter')
    check(f'name: {name}' in txt, f'{skill}: frontmatter name mismatch')
    check('description:' in txt, f'{skill}: missing description')
    check(
        'handoff' in txt.lower()
        or '# Deprecated:' in txt
        or name in {'decompose', 'implement', 'contracts', 'status'},
        f'{skill}: missing handoff wording',
    )
    check(not re.search(r'^agents:', txt, re.M), f'{skill}: unsupported agents frontmatter')
    if re.search(r'\$\{CLAUDE_PLUGIN_ROOT\}/scripts/[A-Za-z0-9_.-]+\.py', txt):
        script_skills.append(skill)
        check(
            'script-execution.md' in txt,
            f'{skill}: bundled helpers must reference the canonical execution contract',
        )
        check(
            'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/' in txt,
            f'{skill}: bundled helpers must use a direct python3 invocation',
        )

check(bool(script_skills), 'skills: no canonical bundled-script invocations found')
for backbone_name in ['start', 'implement', 'amend', 'verify']:
    backbone_text = (ROOT / 'skills' / backbone_name / 'SKILL.md').read_text()
    for required in [
        '## Mandatory command shape',
        'one direct executable invocation',
        'Never add `cd`, shell operators, redirection',
        'Never append `echo`, `wc`',
        'Never run Git, including through `rtk proxy`',
        'Read/Glob/Search on the current worktree',
    ]:
        check(
            required in backbone_text,
            f'skills/{backbone_name}: mandatory command guard missing {required!r}',
        )
script_execution = (ROOT / 'references/script-execution.md').read_text()
for required in [
    'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py"',
    '`Bash(python3:*)`',
    'Never prefix a helper with `cd`',
    'environment-variable assignment',
    '`;`, `&&`, `||`, or a pipe',
    'Project-native read-only commands',
    'standard tool result',
    '`echo $?`',
    'redirect stdout or stderr to a scratchpad',
    '`Bash(<project-read-cli> *)`',
    'Never launch the CLI in the',
    'follow-up polling command',
    "provider's native continuation/wait mechanism",
    'Filesystem and repository inspection',
    'Start the provider session at the project',
    'Never generate a shell program containing `for`, `while`, `if`',
    'Kapelle performs no Git operations',
    'Git hidden behind `rtk proxy`',
    'Do not count commits per file',
]:
    check(required in script_execution,
          f'script execution: missing command-shape guard {required!r}')
for forbidden in [
    r'(?m)^\s*cd\s+',
    r'(?m)^\s*[A-Z][A-Z0-9_]*=.*scripts/',
]:
    for skill in script_skills:
        check(
            not re.search(forbidden, skill.read_text()),
            f'{skill}: compound bundled-script setup is forbidden',
        )

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
    'dispatcher/size.schema.json',
    'dispatcher/workflow-state.schema.json',
    'dispatcher/reconstruction.schema.json',
    'dispatcher/reconstruction-coverage.schema.json',
    'dispatcher/review-gate.schema.json',
    'dispatcher/base-functional-tests.schema.json',
    'dispatcher/unit-test-run.schema.json',
    'dispatcher/verification.schema.json',
    'dispatcher/release.schema.json',
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
    check(props.get('checkpoint', {}).get('enum') == ['task', 'workstream', 'none'],
          'config: invalid implementation.checkpoint')
    check(props.get('checkpoint', {}).get('default') == 'workstream',
          'config: implementation.checkpoint default must be workstream')
    check(props.get('max_task_attempts', {}).get('default') == 3,
          'config: max_task_attempts default must be 3')
    check(props.get('max_agent_runs_per_task', {}).get('default') == 3,
          'config: max_agent_runs_per_task default must be 3')
    check(props.get('telemetry', {}).get('default') is False,
          'config: telemetry default must be false')
    validation = config.get('properties', {}).get('validation', {})
    validation_policy = validation.get('properties', {}).get('development_policy', {})
    check(validation_policy.get('enum') == ['ask', 'allow', 'skip'],
          'config: validation.development_policy must support ask, allow, and skip')
    check(validation_policy.get('default') == 'ask',
          'config: validation.development_policy default must be ask')

implementation_skill = (ROOT / 'skills/implement/SKILL.md').read_text()
for required in [
    '--validation=ask|allow|skip',
    '--checkpoint=workstream|task|none',
    'Default to `--checkpoint=workstream`',
    'Do not write unit tests',
    '/kapelle:verify',
    'Do not create per-task run narratives',
    'Do not dispatch planner and implementer subagents by default',
]:
    check(required in implementation_skill, f'implement: missing orchestration guard {required!r}')
check('dispatch `kapelle:test-author`' not in implementation_skill,
      'implement: must not dispatch test-author during production implementation')
for required in [
    'next business or technical requirement',
    'when the developer considers the current scope complete',
]:
    check(required in implementation_skill,
          f'implement: missing incremental-slice handoff {required!r}')

amend_skill = (ROOT / 'skills/amend/SKILL.md').read_text()
for required in [
    'next feature increment',
    'developer-requested capability',
    'one smallest coherent vertical slice',
]:
    check(required in amend_skill,
          f'amend: missing incremental-slice guard {required!r}')

for rel in [
    'skills/start/SKILL.md',
    'skills/implement/SKILL.md',
    'skills/verify/SKILL.md',
    'skills/amend/SKILL.md',
]:
    check((ROOT / rel).exists(), f'human-controlled workflow: missing {rel}')

human_control = (ROOT / 'references/human-control.md').read_text().lower()
for required in [
    'human-controlled development workflow',
    'production implementation',
    'all unit tests',
    'complete verification',
    '--checkpoint=workstream',
]:
    check(required in human_control, f'human control: missing {required!r}')

developer_questions = (ROOT / 'references/developer-questions.md').read_text()
developer_questions_lower = developer_questions.lower()
for required in [
    'what Kapelle intends to implement',
    'at most three real options',
]:
    check(required in developer_questions,
          f'developer questions: missing contract guard {required!r}')
for required in [
    'raw critic, planner, validator, or subagent output',
    'trade-offs',
    'vague prompts',
]:
    check(required in developer_questions_lower,
          f'developer questions: missing contract guard {required!r}')
for rel in [
    'skills/start/SKILL.md',
    'skills/implement/SKILL.md',
    'skills/amend/SKILL.md',
]:
    check(
        'developer-questions.md' in (ROOT / rel).read_text(),
        f'{rel}: missing developer-question translation contract',
    )
for rel in [
    'agents/implementation-planner.md',
    'agents/critic.md',
    'agents/change-reconciler.md',
]:
    text = (ROOT / rel).read_text()
    check(
        'internal' in text.lower() and 'question' in text.lower(),
        f'{rel}: must keep decision findings internal to the coordinator',
    )
check('<!-- kapelle-workflow: lightweight-v1 -->' in
      (ROOT / 'skills/start/SKILL.md').read_text(),
      'start: missing durable workflow recovery marker')

verify_skill = (ROOT / 'skills/verify/SKILL.md').read_text()
check('write all unit tests now' in verify_skill,
      'verify: must enforce end-of-implementation unit-test timing')
check("developer's explicit statement" in verify_skill,
      'verify: invocation must explicitly close the evolving feature scope')
for required in [
    'functional',
    'unit',
    'integration',
    'contract',
    'static-analysis',
    'lint',
    'build',
    '--developer-verified',
    'developer-attested',
    'record_verification.py',
]:
    check(required in verify_skill, f'verify: missing category {required!r}')

validation_execution = (ROOT / 'references/validation-execution.md').read_text()
for required in [
    'ask` (default)',
    '`allow`',
    '`skip`',
    '`run-selected`',
    '`developer-verified`',
    '`cancelled`',
    '`validation-deferred`',
    '`developer-attested`',
    'REFUSED-validation-incomplete',
]:
    check(required in validation_execution,
          f'validation execution: missing policy guarantee {required!r}')

schema_validated_stages = {
    'skills/start/SKILL.md': [
        'workflow-state.schema.json',
        'architecture-guidance.schema.json',
    ],
    'skills/verify/SKILL.md': ['verification.schema.json'],
    'skills/amend/SKILL.md': [
        'change-request',
        'change-revision',
        'change-state',
        'artifact-state',
        'reconciliation',
    ],
    'skills/reconstruct/SKILL.md': [
        'workflow-state.schema.json',
        'reconstruction.schema.json',
        'reconstruction-coverage.schema.json',
    ],
}
for rel, schema_names in schema_validated_stages.items():
    text = (ROOT / rel).read_text()
    check('validate_json.py' in text,
          f'{rel}: machine artifacts must use deterministic JSON validation')
    for schema_name in schema_names:
        check(schema_name in text,
              f'{rel}: missing deterministic validation for {schema_name}')

dispatcher_text = (ROOT / 'dispatcher/dispatcher.md').read_text()
for required in ['--pointer', '--jsonl', 'Structural failure blocks dispatch']:
    check(required in dispatcher_text,
          f'dispatcher: missing deterministic runtime validation guard {required!r}')

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
        'tasks.md',
        '_kapelle/approvals/plan.json',
        '_kapelle/verification.json',
        '_kapelle/state.json',
        'STATUS.md',
    ]:
        check(required in dependencies, f'artifact graph: missing {required}')
    check(
        dependencies.get('_kapelle/approvals/outline.json')
        == ['proposal.md', '_context/architecture.md'],
        'artifact graph: outline gate must fingerprint stable proposal/context only',
    )
    check(
        dependencies.get('_kapelle/approvals/business-spec.json')
        == ['proposal.md', 'spec.md', 'specs'],
        'artifact graph: business-spec gate artifacts drifted',
    )
    check(
        '_kapelle/architecture-guidance/design.json'
        in dependencies.get('_kapelle/approvals/architecture.json', []),
        'artifact graph: architecture approval must fingerprint scoped guidance',
    )
    plan_dependencies = dependencies.get('_kapelle/approvals/plan.json', [])
    check('tasks.md#structural' in plan_dependencies,
          'artifact graph: plan must use structural tasks fingerprint')
    check('_kapelle/architecture-guidance/design.json' in plan_dependencies,
          'artifact graph: plan must fingerprint architecture guidance')
    for legacy in ['sad.md', 'surface-plan.json', 'tasks.json', 'ship.md']:
        check(legacy not in dependencies, f'artifact graph: legacy key {legacy}')

feature_manifest_schema = load_json('dispatcher/feature-manifest.schema.json')
feature_state_schema = load_json('dispatcher/feature-state.schema.json')
recovery_schema = load_json('dispatcher/recovery-report.schema.json')
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

review_gate_text = (ROOT / 'scripts/review_gate.py').read_text()
check(
    'validate_architecture_package(feature_dir)' in review_gate_text,
    'review gate: architecture package validation must be runtime-enforced',
)
check(
    'validate_progressive_docs(feature_dir)' in review_gate_text,
    'review gate: progressive documents must be runtime-enforced',
)

start_skill = (ROOT / 'skills/start/SKILL.md').read_text()
for required in [
    'walking-skeleton workstream',
    'at most three checkboxes',
    'candidate capabilities',
    'progressive-map-v1',
    'validate_progressive_docs.py',
    'design/domain-model.md',
    'production-shaped',
    'default business-analyst/critic/devil',
    '_kapelle/architecture-guidance/design.json',
    'pure gate action',
]:
    check(required in start_skill, f'start: missing lightweight-planning guard {required!r}')
check(
    'review_gate.py approve' in start_skill or 'review_gate.py" approve' in start_skill,
    "start: missing lightweight-planning guard 'review_gate.py approve'",
)

for rel in [
    'skills/start/SKILL.md',
    'skills/implement/SKILL.md',
    'dispatcher/dispatcher.md',
    'dispatcher/execution-contract.md',
]:
    text = (ROOT / rel).read_text()
    check('architecture-rules' in text,
          f'{rel}: missing project architecture-rules capability')

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

reconstruct_skill = (ROOT / 'skills/reconstruct/SKILL.md').read_text()
for required in [
    '<!-- kapelle-workflow: reconstruction-v1 -->',
    'observed',
    'inferred',
    'declared',
    'unknown',
    'architecture-rules subagent',
    'kapelle:business-analyst',
    'kapelle:explorer',
    'kapelle:critic',
    'kapelle:reviewer',
    'reconstruction-coverage.schema.json',
    'at least one independently useful `specs/*.md`',
    'at least one independently useful `design/*.md`',
    'Never hand off to development',
]:
    check(required in reconstruct_skill,
          f'reconstruct: missing evidence/workflow guard {required!r}')
for rel in ['AGENTS.md', 'CLAUDE.md']:
    runtime_instructions = (ROOT / rel).read_text()
    for required in [
        'Existing-code reconstruction is documentation-only',
        '`observed | inferred | declared | unknown`',
        '`documented` never means ship-ready',
    ]:
        check(required in runtime_instructions,
              f'{rel}: missing reconstruction invariant {required!r}')

usage = (ROOT / 'docs/USAGE.md').read_text()
for required in [
    '/kapelle:start <slug>',
    '/kapelle:implement <slug>',
    '/kapelle:verify',
    '/kapelle:verify <slug> --approve',
    '/kapelle:migrate',
    '/kapelle:status <slug>',
    '/kapelle:reconstruct <slug>',
]:
    check(required in usage, f'usage guide: missing workflow detail {required!r}')

command_guide = (ROOT / 'docs/COMMAND_EXECUTION_UK.md').read_text()
for required in [
    '/kapelle:start <slug>',
    '/kapelle:implement <slug>',
    '/kapelle:verify <slug>',
    '/kapelle:amend <slug>',
    '/kapelle:migrate <slug>',
    '/kapelle:status <slug>',
    '/kapelle:reconstruct <slug>',
    'Що задати',
    'Результат',
]:
    check(required in command_guide, f'command guide: missing detail {required!r}')

vocabulary = load_json('dispatcher/vocabulary.json')
if vocabulary:
    task_states = vocabulary.get('task_states', [])
    dispositions = vocabulary.get('reconciliation_dispositions', [])
    change_states = vocabulary.get('change_states', [])
    skill_names = {skill.parent.name for skill in skills}
    check('legacy_backbone_stages' not in vocabulary,
          'vocabulary: legacy backbone must not exist')
    check(vocabulary.get('backbone_stages') == [
        'start',
        'implement',
        'verify',
    ], 'vocabulary: human-controlled backbone drifted')

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

deprecated_skills = {
    'classify-size',
    'spec',
    'design',
    'plan',
    'base-functional-tests',
    'unit-tests',
    'finalize',
    'specify',
    'clarify',
    'decompose',
    'plan-tests',
    'feature-review',
    'ship',
    'change',
    'fix',
    'resume-change',
}
for deprecated in sorted(deprecated_skills):
    text = (ROOT / 'skills' / deprecated / 'SKILL.md').read_text()
    check('# Deprecated:' in text and 'Write nothing' in text,
          f'{deprecated}: legacy wrapper must be non-executing')

workflow_schema = load_json('dispatcher/workflow-state.schema.json')
if workflow_schema:
    workflow_variants = workflow_schema.get('oneOf', [])
    human_variant = next(
        (
            item for item in workflow_variants
            if item.get('properties', {}).get('workflow', {}).get('const')
            == 'human-controlled'
            and item.get('properties', {}).get('version', {}).get('const') == 2
        ),
        {},
    )
    reconstruction_variant = next(
        (
            item for item in workflow_variants
            if item.get('properties', {}).get('workflow', {}).get('const')
            == 'reconstruction'
        ),
        {},
    )
    check(human_variant.get('properties', {}).get('profile', {}).get('const')
          == 'lightweight',
          'workflow state: version 2 profile must be lightweight')
    check(
        reconstruction_variant.get('properties', {})
        .get('created_from', {})
        .get('const') == 'existing-code',
        'workflow state: reconstruction must originate from existing-code',
    )
size_schema = load_json('dispatcher/size.schema.json')
if size_schema:
    required = set(size_schema.get('required', []))
    check({'interview_depth', 'lane'} <= required,
          'size state: interview_depth and lane must be required')

review_gate_schema = load_json('dispatcher/review-gate.schema.json')
if review_gate_schema:
    gates = (
        review_gate_schema.get('properties', {})
        .get('gate', {})
        .get('enum', [])
    )
    for required in [
        'plan',
        'outline',
        'business-spec',
        'architecture',
        'delivery-plan',
        'feature-plan',
        'final',
        'reconstruction-scope',
        'reconstruction-spec',
        'reconstruction-design',
        'reconstruction',
    ]:
        check(required in gates, f'review gate schema: missing {required}')

for rel in [
    'skills/start/SKILL.md',
    'skills/verify/SKILL.md',
    'skills/reconstruct/SKILL.md',
]:
    text = (ROOT / rel).read_text()
    check(
        'review_gate.py' in text,
        f'{rel}: approval-capable stage must use deterministic review gate helper',
    )
    check(
        bool(re.search(r'(?:construct (?:gate|approval)\s+JSON|approval JSON manually)', text)),
        f'{rel}: must forbid hand-written review gate JSON',
    )

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
    check(set(profile_stages) == skill_names - deprecated_skills,
          'role profiles: stages must exactly cover executable bundled skills')
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
