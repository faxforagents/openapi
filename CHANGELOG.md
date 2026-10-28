# Changelog

All notable changes to the public OpenAPI document are listed here. The version is the API's
`info.version` as served at `https://api.faxforagents.com/openapi.json`.

## 0.1.0 (2026-10-28)

First public document. 69 paths, 85 operations, 91 schemas, curated from the live server document by
`scripts/curate.py`.

- Keys, uploads, documents, quotes, faxes, webhooks, events, billing, platform, sandbox, approvals,
  policies, agents and the inbox.
- `x-llm` on every operation names the scope the call needs, whether the call mutates and whether it
  honours `Idempotency-Key`.
- Error responses documented on every operation with the one error envelope.
- Price card launch-v1, effective from 2026-10-28. $0.039 per page sent, $0.019 per page received.
  $2 per number per month, $19 per month for the Agent workspace.
