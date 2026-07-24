# Deprecated legacy command wrappers

Kapelle has one human-controlled pipeline. Deprecated command names never execute their former
stage protocol.

On invocation:

1. If the feature lacks a human-controlled marker, return `Status: DEPRECATED` and
   `/kapelle:migrate <slug>`.
2. Otherwise return `Status: DEPRECATED` and the replacement command named by the wrapper.
3. Write no feature or project files and run no agent, validation, git, or migration action.

Wrappers exist for one compatibility release and may be removed afterward.
