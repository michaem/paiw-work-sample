# Shared review policy

Start every review with `Review policy: v1`.

Report only actionable defects supported by the code and the project's README.
Do not invent a defect just to produce a finding. If none are supported, say so.

For each finding, use these fields:

1. **Location**: repository-relative file path and line number.
2. **Failure**: concrete input, actual result, and expected result.
3. **Check**: a small reproducible test or command. Say whether you ran it.

Keep the report concise. Review only; do not fix or rewrite the code.
