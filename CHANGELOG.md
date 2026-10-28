# Changelog

All notable changes to the public OpenAPI document are listed here. The version is the API's
`info.version` as served at `https://api.faxforagents.com/openapi.json`.

## 1.1.0 (2026-10-28)

API version 1.1.0, taken from the live server document the same day. 100 paths, 127 operations,
132 schemas.

- `POST /v1/documents` takes `html`: rendered by a headless browser with scripts off and no network,
  US letter unless `@page` says otherwise, at most 2 MiB.
- `POST /v1/uploads` takes `image/png`, `image/jpeg` and `image/tiff` beside `application/pdf`. An
  image becomes gray letter pages, every TIFF frame is a page.
- New tags: `numbers` (coverage, inventory, orders, your numbers, porting, sender verification),
  `extractions` (OCR, field extraction, classification, summaries, saved schemas), `organizations`
  and `members`. The inbox gains update, delete, a signed download and its content route.
- `Quote` carries `per_page_micro` and `route_label`. `ApprovalRequest` carries `notified`.
  `InboxItem` carries the number, project, media status and read state of a received fax. The
  summary form a sandbox inbound fax returns is `InboxItemSummary`.
- The scope table names `number:read`, `number:buy`, `inbox:write`, `document:extract`,
  `member:admin` and `org:admin`. An agent's key can never carry `number:buy`, `member:admin` or
  `org:admin`.
- The dashboard's cookie sign-in operations (tag `auth`) are left out, like the admin routes.
- Fixed: the "No API key" sentence about signed links was on every keyed operation instead of the
  signed-URL ones.

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
