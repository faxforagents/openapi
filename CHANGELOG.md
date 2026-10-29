# Changelog

All notable changes to the public OpenAPI document are listed here. The version is the API's
`info.version` as served at `https://api.faxforagents.com/openapi.json`.

## 1.2.3 (2026-10-29)

API version 1.2.3, taken from the live server document. The same 100 paths, 127 operations and 132
schemas as 1.1.0: the server's 1.2.x releases changed what happens behind the operations (a production
server without a carrier refuses live operations, the readiness probe watches the HTML renderer) and
the dashboard's sign-in, and none of that changes the shape of a public operation.

- Every operation that reaches the carrier with a live key documents `503 live_provider_unavailable`:
  `create_fax_quote`, `create_fax`, `cancel_fax`, `get_number_inventory`, `create_number_order`,
  `create_release_request`, `create_portability_check` and `create_port_order`. A production server with
  no carrier configured refuses them before any approval is consumed or any hold is placed, with
  `retryable` false. Test keys reach the sandbox and are never refused this way. The server document
  does not declare the response; `scripts/curate.py` adds it (`LIVE_CARRIER`).
- `ErrorEnvelope.error.code` names `live_provider_unavailable` among the stable codes.

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
