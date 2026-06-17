# Security Evidence

`test_vulnerable.py` is **not** part of the running application. It is kept on
purpose as the "before hardening" reference: a single file containing
deliberately bad patterns (hardcoded secret, `eval()`, `pickle.loads()`, MD5,
`shell=True`, string-concatenated SQL, etc.) so a SAST tool like Bandit has
something to flag in the *before* scan that goes into Section 4 of the report.

It is excluded from the *after hardening* Bandit run via `.bandit` at the
repo root, e.g.:

```bash
bandit -r . -x ./venv,./security_evidence,./staticfiles
```

Do not import this file from application code, and do not modify the patterns
in place — its value is as a fixed reference point for the before/after
comparison in the technical report.
