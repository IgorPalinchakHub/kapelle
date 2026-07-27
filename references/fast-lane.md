# Deprecated lane model

Fast and standard lanes were removed from the public development workflow. Their separate stage
chains created more routing and review overhead than value.

All new features use the lightweight route and begin with one high-level feature/system map plus one
walking skeleton. Larger features accumulate developer-requested vertical slices through `amend`;
they do not add mandatory stages or receive detailed up-front use-case designs or a complete
workstream plan.

Existing `human-controlled-v1; lane: fast|standard` features route to `/kapelle:migrate <slug>`.
