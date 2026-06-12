# Contributing

Thanks for considering a contribution to `ci-failure-triage`.

## Local setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Guidelines

- Add or update tests for behavior changes.
- Add or update `samples/` logs when introducing a failure signature.
- Prefer transparent rules with clear evidence before adding complex heuristics.
- Keep command output machine-readable where possible.
- Document new failure categories in the README.
