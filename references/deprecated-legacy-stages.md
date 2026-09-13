# Removed command migration
The compatibility wrappers are no longer bundled or advertised as commands. There is one workflow.

| Removed commands | Current route |
|---|---|
| spec, specify, clarify, classify-size, design, plan, plan-tests, decompose | start (use --revise for feedback) |
| change, fix | amend |
| base-functional-tests | implement |
| unit-tests, feature-review | verify |
| finalize, ship | verify --approve |
| resume-change | status |

For an existing feature without a current workflow marker, use `/kapelle:migrate <slug>` first.
Removal affects command discovery, not durable feature documents or historical evidence.
