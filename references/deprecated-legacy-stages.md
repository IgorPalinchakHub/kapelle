# Removed commands
The compatibility wrappers are no longer bundled or advertised as commands. There is one workflow.

| Removed commands | Current route |
|---|---|
| spec, specify, clarify, classify-size, design, plan, plan-tests, decompose | start (use --revise for feedback) |
| change, fix | amend |
| base-functional-tests | implement |
| unit-tests, feature-review | verify |
| finalize, ship | verify --approve |
| resume-change | status |

The migrate command and migration scripts are also removed. For an older feature, read its specs
and docs as context and start a new change with a new slug through the full current workflow.
Removal affects command discovery, not durable feature documents or historical evidence.
