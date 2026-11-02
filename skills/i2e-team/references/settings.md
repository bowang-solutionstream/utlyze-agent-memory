# Persistent storage settings

Before creating operational records, read `~/.config/i2e-team/runtime.json` if it exists. This private operator file lets a fresh session find the same ledger and canonical failure store. It is outside source and installed skills. It contains exactly these fields:

```json
{
  "schema": "i2e-team-settings-v1",
  "db": "/PRIVATE/i2e/runs.sqlite",
  "case_store": "/PRIVATE/existing-canonical-cases",
  "case_helper": "/Users/bow/.codex/skills/i2e-failure-cases/scripts/shared_cases.py",
  "case_helper_sha256": "OBSERVED_HELPER_SHA256"
}
```

This is a schema example, not operational evidence. Validate the field set, schema, absolute canonical paths, private file permissions and actual helper digest before use. Refuse a settings symlink, extra hard link, traversal spelling, malformed content or changed dependency. Keep the ledger, its derived evidence directory and case store outside the source checkout and installed skills. The runtime performs its own path and dependency checks as well.

Supply `db` explicitly to the CLI's `--db` option. Supply `case_store`, `case_helper` and `case_helper_sha256` in the new run's intake. Settings do not initialize SQLite or a case store, invoke a command, import a corpus, enable sharing, set a budget, select a project, approve work or grant authority. Establish the actual task's project, owned paths, instructions, contributors, classification and allowed actions separately.

If the file is absent, report storage as unconfigured and provision persistent private paths within the task's actual authority. Initialize a new canonical store only through its existing helper when authorized. An unavailable or unconfigured store is a visible gap, not an empty search result. Do not silently select a temporary store. Preserve any preexisting settings; conflicting values require an explicit, source-backed configuration change rather than replacement during installation.

Captured cases remain in their original canonical store and project scope. Carry applicable known digests when continuing the same task, including ranking misses. Do not import another project's private cases or treat a shared storage location as permission to read across client boundaries. Corrections and withdrawals in the ledger remain visible after restart.
