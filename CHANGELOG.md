# Changelog

All notable changes to the public OpenAPI document are listed here. The version is the API's
`info.version` as served at `https://api.faxforagents.com/openapi.json`.

## 1.18.0 (2026-11-12)

API version 1.18.0, curated from the server document at that release. 115 paths, 145 operations and
151 schemas. No path, operation id, request body or success response changed.

- The server now declares how each operation is authorized, and this document follows it. Every
  operation has its own `security`. 130 take an API key (`bearerAuth` or `apiKeyHeader`). 4 take a key
  or the `orderToken` of a one-time order. 1 takes a key or nothing. 4 take nothing. 6 take a
  `signedUrl`.
- New security scheme `signedUrl`: `sig` in the query of a link the API handed out. The six content
  links carried an empty `security` before.
- New extension `x-required-scope` on 131 operations, the scope the key needs. It agrees with
  `x-llm.scope`. The two connected-app operations get it from this repository's scope table, because
  the server checks `key:admin` inside the route.
- Errors are declared as shared responses in `components.responses`: `Unauthorized` (401),
  `PaymentRequired` (402), `Forbidden` (403), `NotFound` (404), `Conflict` (409), `PayloadTooLarge`
  (413), `UnprocessableContent` (422), `TooManyRequests` (429) and `ServiceUnavailable` (503). Each is
  the error envelope. Operations now name 409, 413, 402 and 503 where they answer them.
- Removed schemas: `HTTPValidationError` and `ValidationError`. The server never sent that shape. A
  422 is the error envelope with `invalid_request`.
- `ErrorEnvelope` is now the server's own schema and points at the new schema `ErrorBody`.
  `correlation_id` may be null and is no longer listed as required.
- `create_one_time_order` documents its 429: `details.cap` names the limit, and `upload_queue` means
  too many files are being read at once.
- Left out, as before: the dashboard session. The server names a `sessionCookie` scheme and 16
  operations that take it alone. None of them is in this document. `scripts/curate.py` now fails when
  such an operation is not excluded, and when the server's credentials or scopes differ from its tables.

## 1.17.2 (2026-11-12)

API version 1.17.2, curated from the server document at that release. 115 paths, 145 operations and
152 schemas, the same counts as 1.17.0. No path, operation, schema or field was added or removed.

- `sender_name` on the send body has a new description. It is the name that identifies the sender.
  The carrier gets it as the caller name for its header line. Omit it and the organization's name is
  used. Until 1.17.0 an omitted name showed the number alone.
- Not visible in a schema: a fax without a cover sheet prints one line at the top of page one. The
  line gives the sender, the sending number and the time in UTC. The page count does not change. A
  fax with a cover sheet gets no line.
- 1.17.1 changed no path and no schema. It moved the price card to launch-v3, effective 2026-11-12.

## 1.17.0 (2026-11-12)

API version 1.17.0, curated from the server document at that release. 115 paths, 145 operations and
152 schemas. The document a production server serves at 1.17.0 is the same source, byte for byte.

- `read_one_time_order_by_token` joins the document: `POST /v1/one-time-sends/by-token` reads what a
  mailed confirmation link is for, with the token in the body. It changes nothing, so `x-llm.mutating`
  is false. `get_one_time_order_by_token`, the same read with the token in the path, is deprecated: a
  token in a path reaches access logs.
- `OneTimeFromQuote` documents `approval_id`, and `accept_aup` is no longer required there. A key's
  value is not recorded. The person who pays accepts the acceptable use policy and the terms on the
  order's page.
- `create_one_time_checkout` takes an optional body, `{"accept_aup": true}`. An order whose
  `aup_accepted` is false needs it once, from the status token or a session, never from a key.
- `OneTimeOrder` and `OneTimeOrderCreated` carry `aup_accepted`, `status_url` and `queue`.
  `OneTimeConfig` carries `queue`. New schema `OneTimeQueue` with `queued`, `jobs_ahead` and
  `estimated_wait_minutes`: the wait for a carrier line. A queued order is kept and sent in turn.
- `Balance` carries `top_up_url`, the dashboard page where a person adds funds. `Capabilities` carries
  `extraction_pricing`.
- `InsufficientBalance` documents `details.top_up_url` and `details.one_time_offer`. The server sends
  both since 1.17.0. The offer is present when the same send can be paid by card. It names the
  one-time price, the page counts and the `approval_id` that authorizes the order.
- Not visible in a schema: a premium-rate or personal-number range is refused as an unsupported
  destination. A request body over the limit of its route answers `413 payload_too_large` in the
  usual envelope. The limit is 1 MB by default and 4 MB on `POST /v1/documents`. The bytes of an upload
  and the one-time create form keep their own larger limits.
- `scripts/curate.py` gains `READS`, the operations sent with a mutating method that change nothing,
  and `TOP_UP_MARKER`, which adds `details.top_up_url` only when the source carries the field.
- The price card is still launch-v2, effective 2026-10-31. `docs/llms.txt` named launch-v1 and now
  names the card in force.

## 1.16.1 (2026-11-12)

API version 1.16.1, curated from the server document at that release. 114 paths, 144 operations and
151 schemas. The document a production server serves at 1.16.1 is the same source, byte for byte.

- New tag `one-time-sends`: one fax paid by card, with no wallet. Ten operations join the document.
  `get_one_time_config` reads whether the product is open, with the card and the limits.
  `create_one_time_order` takes a file as `multipart/form-data` or text as JSON.
  `create_one_time_order_from_quote` turns a live quote the wallet does not cover into an order.
  `list_one_time_orders` and `get_one_time_order` read orders. `create_one_time_checkout` opens the
  hosted card payment. `get_one_time_order_by_token` and `confirm_one_time_order` serve the mailed
  confirmation link. `resend_one_time_confirmation` mails it again. `get_one_time_receipt_pdf` returns
  the receipt. `get_one_time_config` leaves `EXCLUDED`.
- New security scheme `orderToken`, the `X-FFA-Order-Token` header. The status token of an order reads
  it, opens its checkout and mails its confirmation again, with no key. `x-llm.scope` gains the value
  `none` for a call that takes no credential. `x-llm.key_optional` and `x-llm.order_token` mark the
  one-time operations a key is optional for and the ones the token opens.
- New schemas: `OneTimeConfig`, `OneTimeRoute`, `OneTimeOrder`, `OneTimeOrderCreated`,
  `OneTimeOrderPage`, `OneTimeFromQuote`, `OneTimeCheckout`, `OneTimeConfirm`, `OneTimeConfirmSummary`,
  `OneTimeConfirmed`, `OneTimeCard`, `OneTimePrice`, `OneTimeJob` and `InsufficientBalance`. `FaxJob`
  and `Receipt` carry `one_time`, the order's block on a fax that a card paid for.
- `create_fax` documents `402 insufficient_balance` with its own schema, `InsufficientBalance`, whose
  `details` carries `available_micro` and `needed_micro`. It documents `403 approval_required` and the
  `409` codes too. The one-time operations document their `403`, `404`, `409`, `422` and `503` answers.
  The server does not declare these in its own document. They are added by `DOCUMENTED_ERRORS` in
  `scripts/curate.py`, read from the server's routes.
- `details.one_time_offer` on `402 insufficient_balance` is not in this version: server 1.16.1 does not
  send it. `scripts/curate.py` adds it to `InsufficientBalance` by itself once the source document
  carries the release that sends it.
- `scripts/curate.py` gains `EXCLUDED_PATHS`: nothing under `/v1/admin`, `/v1/affiliate` or `/webhooks`
  reaches the document, whatever its tag. The affiliate, payout and leave operations are named in
  `EXCLUDED` as well, and the tag `affiliate` is dropped. `--vendor` keeps the source in
  `scripts/server-openapi.json` without those paths and the schemas only they use.
- Price card launch-v2, effective 2026-10-31. The four wallet prices are the same as on launch-v1. One
  fax by card, published 2026-11-11: $2.49 for up to 5 pages to a US or Canadian number with the cover
  page included, $0.49 for each extra page, 20 pages at most. `scripts/truthcheck.sh` accepts the two
  one-time amounts only in a file that states 2026-11-11.
- The README has the brand header. The reference pages link to the website, the docs, the dashboard,
  the pricing page and the changelog.

## 1.13.2 (2026-11-10)

API version 1.13.2, taken from the live server document. The same 105 paths, 134 operations and 137
schemas as 1.13.1. Only `info.version` changes: no operation, parameter, schema or description differs.
The server's 1.13.2 release changed nothing in the shape of a public operation.

## 1.13.1 (2026-11-10)

API version 1.13.1, taken from the live server document. The same 105 paths, 134 operations and 137
schemas as 1.12.0. Only `info.version` changes: no operation, parameter, schema or description differs.
The server's 1.13.x releases changed nothing in the shape of a public operation.

## 1.12.0 (2026-11-10)

API version 1.12.0, taken from the live server document. 105 paths, 134 operations, 137 schemas.

- Seven operations join the document. `get_fax_receipt_pdf` returns the receipt as a one-page PDF.
  `list_number_orders` lists number orders. `download_export_archive` serves an organization archive
  from a signed link that lives 72 hours. `get_auto_send` and `put_auto_send` read and set the auto-send
  setting for connected apps. `list_oauth_grants` and `revoke_oauth_grant` list and revoke connected apps.
- New tag `oauth` for connected apps. New schemas `AutoSendSetting`, `AutoSendUpdate`, `Grant`,
  `GrantList` and `NumberOrderList`.
- Every mutating operation declares the `Idempotency-Key` header as a parameter.
- `QuoteCreate`, `Quote` and `FaxJob` carry `quality`, `sender_name` and `delete_after_send`.
  `ApiKey`, `ApiKeyCreate` and `ApiKeyWithSecret` carry `connected_app`. `Policy` carries `managed`.
  `EffectivePolicies` carries `requires_human_approval`. `Capabilities` carries `extraction` and `one_time`.
- `get_effective_policies` takes `key_id`, `agent_id` and `connection_id`. `list_faxes` filters by
  `idempotency_key`.
- `scripts/curate.py` gains `EXCLUDED`, the operations left out by name with the reason for each:
  `get_integration_review`, `get_oauth_authorization`, `approve_oauth_authorization` and
  `deny_oauth_authorization` need a dashboard session, and `get_one_time_config` serves the public
  one-time send page. `SIGNED_LINK_LIFETIME` states a signed link's life where it is not ten minutes.

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
