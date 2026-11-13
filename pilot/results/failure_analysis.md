# Failure analysis (automated; qualitative cases not yet curated)

Not done: the protocol's 3 strong + 3 failure examples per source need human review with provenance links. Failure modes observed in the automated pass:

- **Execution issues (fixed, not data failures):** the GitLab `/notes` API returns 401 without auth, so notes come from the public `discussions.json` endpoint; the Wikimedia API rate-limited (429) on the first pass and was retried with backoff. Final fetch: 300/300.
- **GitLab:** (1) 94/100 incidents have no runbooks link; (2) linked "runbooks" are often config files (e.g. `rules/gitaly.yml`, `metrics-catalog/*.jsonnet`), i.e. wrong target type; (3) no link-bearing case was retrospective-only by timestamp.
- **Wikimedia:** (1) only 3 cases link any keyword-matching operational page, all to `MariaDB/troubleshooting`; (2) only 2/100 explicitly say no runbook existed, most simply cite none; (3) timelines are retrospective (grade <= 1).
- **MANtIS:** (1) 45/100 not troubleshooting by the crude keyword proxy; (2) 79/100 lack three substantive seeker turns; (3) accepted-answer labels are absent from the JSON release; (4) answer links often point to non-guide resources (unverified).
