# Access and licensing (preliminary, not legal advice)

| Source | Access method | Notes |
|---|---|---|
| GitLab production tracker | Public REST API (issue list/detail) and public `discussions.json` web endpoint; no authentication | Terms for issue comments not reviewed. Raw text kept out of git (`pilot/raw/` is gitignored). |
| Wikitech | MediaWiki API, anonymous | Wikimedia text is generally CC BY-SA, but wikitech page licensing was not checked. |
| MANtIS | `json_dataset.7z` (77 MB) from the Google Drive link on github.com/Guzpenha/MANtIS | Content derives from Stack Exchange (CC BY-SA, attribution required). SHA-256 of the downloaded archive is in `source_versions.json`. |

Raw text is not committed. Only derived flags, counts and IDs are in the repo.
