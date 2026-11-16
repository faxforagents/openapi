# Changelog

All notable changes to the public OpenAPI document are listed here. The version is the API's
`info.version` as served at `https://api.faxforagents.com/openapi.json`.

## 1.21.2 (2026-11-16)

API version 1.21.2, curated from the server document at that release. 132 paths, 165 operations and
175 schemas, the same as 1.21.0. No operation or schema is new. This document skips 1.21.1, which
changed only `info.version` here.

- `Subscription` gains `cancel_at` and `ends_at`. Both are required and nullable. `cancel_at` is
  when Stripe is set to end the subscription. A cancel in the billing portal sets it to the end of the
  period and leaves `cancel_at_period_end` false.
- `ends_at` is when the plan ends without another charge. It is `cancel_at` when that comes no later
  than `current_period_end`, or `current_period_end` after a cancel at the period's end. It is null
  while the plan renews.
- `create_subscription_checkout` gains a description. It answers the address of Stripe's payment page
  for the plan.
- Its 409 has its own text, written by the server. `error.code` is `conflict` and
  `error.details.reason` says why. `plan_active` means the plan is active, here or at Stripe right
  after a payment. `checkout_open` means a Checkout of the plan is still open. Then `error.details.url`
  is its page and `error.details.expires_at` is when it closes. The same 409 names
  `idempotency_key_conflict`.
- `OneTimeConfirmSummary.state` gains `link_canceled`, for an order that was canceled with its hold
  released. The description of the schema names it.
- The descriptions of `get_fax_history_csv` and of its 403 name both scopes. `x-required-scope` is
  `fax:read`, and the export needs `inbox:read` as well.
- The description of `OneTimeOrder` is split into shorter sentences. Its fields do not change.

## 1.21.0 (2026-11-16)

API version 1.21.0, curated from the server document at that release. 132 paths, 165 operations and
175 schemas. 1.20.11 had 130, 163 and 174. This document skips 1.20.12, which changed only
`info.version` here.

- New operations `get_fax_history_csv`, `GET /v1/records/faxes.csv`, and `get_audit_csv`,
  `GET /v1/records/audit.csv`. They are the records export of the Agent workspace plan. Each answers
  CSV text for a range of UTC days, `from` and `to`, both included. A range of more than 20000 lines
  answers 422.
- The export answers while the plan is active and for 30 days after it ended. Otherwise it is 403
  `workspace_required`, with `details.ended_at` and `details.closed_at`. The fax history needs `fax:read`
  and `inbox:read`. The audit trail needs `org:admin` and refuses an agent. `scripts/curate.py` gives
  both a scope and an `x-llm.hint`.
- `list_faxes` takes `created_after`, included, and `created_before`, left out. Both are ISO 8601 times,
  read as UTC when they carry no offset. A range that starts after it ends answers 422
  `invalid_request`. The operation gains a description.
- `Quote.live_amount_micro` says what the same fax costs with a live key. A test quote is free, so this
  is what it would cost live. On a live quote it equals `amount_micro`. It is null when the rate card in
  force is not the one the quote was priced on, or no longer serves the destination.
- New schema `WorkspacePlan`, the required `plan` of `SubscriptionList`. It says whether the plan is
  active and what it gives. That is the fax credit, how long records are kept, the request limits and
  the included number. It also says when the plan ended, when the cleanup runs and whether the export is
  open.
- `Number.included_with_workspace` is true while the Agent workspace pays that number's monthly charge.
  `NumberOrder.first_month_hold_micro` is 0 then, and for a test number.
- `Capabilities.limits` gains a description. `requests_per_minute` is the limit of the calling
  credential: 3000 while the Agent workspace is active, 600 otherwise. The `RateLimit-Limit` header says
  the same.
- One-time orders have three new statuses, set by a person at Fax for Agents: `refunding`, `refunded` and
  `canceled`. They are in `OneTimeOrder`, `OneTimeOrderCreated`, `OneTimeConfirmSummary` and `OneTimeJob`,
  and in the `status` filter of `list_one_time_orders`.
- `OneTimeOrder` and `OneTimeOrderCreated` gain `refund_pending_micro`, a refund the payment provider has
  not confirmed yet.
- Descriptions say test where they said sandbox. These are `Capabilities.extraction_pricing` and the
  `amount_micro` of `InboxItem`, `InboxItemDetail` and `InboxItemSummary`.
- `PolicyEvaluation.approval_required` says it is false for a signed-in owner's own live send, which
  needs no approval.
- A new route of the dashboard sign-in, `leave_organization` (`POST /v1/auth/leave-organization`, tag
  `auth`), stays out, as every `auth` route does. Its schemas `LeaveOrganization` and `LeftOrganization`
  stay out with it, and so does its 409 `last_owner`.

## 1.20.11 (2026-11-15)

API version 1.20.11, curated from the server document at that release. 130 paths, 163 operations and
174 schemas, the same as 1.20.10. No operation or schema is new.

- `replay_webhook_delivery` has a 409 of its own, written by the server. A replay of a delivery whose
  webhook was deleted answers `conflict` with `details.reason` `webhook_deleted`. Nothing can be sent to
  that webhook again. The same 409 names `idempotency_key_conflict`. In 1.20.10 the route had the shared
  409, which does not name `webhook_deleted`.
- `TopupSession.checkout_status` is also null for a top-up that is not open. Stripe is asked about an
  open top-up only.
- A new route of the dashboard sign-in, `confirm_reauth_link` (`POST /v1/auth/reauth/confirm`, tag
  `auth`), stays out, as every `auth` route does. Its schemas `ReauthConfirm` and `ReauthConfirmed` stay
  out with it. So does `ReauthLinkSent`, the new 202 answer of `POST /v1/auth/reauth`.

## 1.20.10 (2026-11-15)

API version 1.20.10, curated from the server document at that release. 130 paths, 163 operations and
174 schemas, the same as 1.20.9. No operation or schema is new.

- `get_topup_session` takes `check_checkout`, a boolean that defaults to false. With true, the server
  asks Stripe about the hosted Checkout of an open top-up. The answer is the new field
  `TopupSession.checkout_status`: `open`, `complete`, `processing` or `expired`. It is null when not
  asked, or when Stripe could not be read. Only Stripe's event credits the wallet.
- Every `Delivery` carries `webhook_deleted`, which only `DeliveryDetail` had. It is true when the
  webhook was deleted since. The deliveries that were waiting are not sent, and none can be replayed.
- The 409 of `rotate_api_key` and of `cancel_topup_session` is now written by the server. The first
  names `details.reason` `key_expired` and `details.expires_at`. The second names `details.status`,
  and `details.reason` `paid` when the payment came in first. `scripts/curate.py` no longer writes
  either.
- The shared 409 no longer says that `error.code` names the state. A state with a code of its own, such
  as `quote_expired`, is named by `error.code`. Otherwise the code is `conflict` and `error.message`
  says what is in the way.
- The shared 410 is `organization_deleted` alone. Six document routes name `document_expired` on their
  410, and five inbox routes name `inbox_item_expired`. The signed links `get_document_content` and
  `get_inbox_content` name only the expiry.
- Eight billing routes name `environment_not_billable` on their 403, the refusal of a test key. They
  are `create_topup_session`, `cancel_topup_session`, `create_auto_topup`, `list_invoices`,
  `get_invoice`, `get_invoice_receipt`, `create_subscription_checkout` and `create_portal_session`.
- `OneTimeCoverCheck` declares the limits of the create. `to_name` is at most 120 characters, `subject`
  200 and `message` 2,000, where the schema said 1000, 1000 and 8000. A longer field answers 422
  `invalid_request`, as on the create. The three fields gain a description.
- The four counters of `PolicyUsage` gain a description. So do `policy_name` and `version` of
  `PolicyVerdict` and `PolicyEvaluation`.
- `NumberUpdate.email_pdf` says a PDF over 15 MiB is not attached, where it said 15 MB.
- Not visible in the document: deleting a webhook ends the deliveries that were waiting for it. They
  read `failed` with `error` "the webhook was deleted" and no `next_attempt_at`. A replay of any delivery
  to a deleted webhook answers 409 `conflict` with `details.reason` `webhook_deleted`.

## 1.20.9 (2026-11-15)

API version 1.20.9, curated from the server document at that release. 130 paths, 163 operations and
174 schemas. 1.20.6 had 128, 161 and 170. The changes came with 1.20.8, and 1.20.9 changed the wording
of one description.

- New operation `cancel_topup_session`, `POST /v1/topup-sessions/{topup_session_id}/cancel`. It closes
  the hosted Checkout of an open manual or setup top-up and answers the session with status `canceled`.
  Canceling a setup payment also turns off the auto top-up that waited on it. A top-up that was paid,
  declined or charged off session answers 409. Scope `billing:write`.
- New operation `create_one_time_cover_check`, `POST /v1/one-time-sends/cover-checks`. It lays out the
  cover sheet of a one-time order from the fields typed so far (`OneTimeCoverCheck`). It answers whether
  the message fits and how many more lines fit (`OneTimeCoverRoom`). It needs no credential and stores
  nothing, so `x-llm` marks it as a read.
- `get_statement` and `get_statement_csv` take `type`, the type each line shows. `kind` is the same
  filter by its older name. Both at once answer 422 unless they name the same type.
- `StatementLine.ref_type` names what a hold or its release was for: `fax_job`, `extraction` or
  `number_order`. `GET /v1/ledger` keeps `fax_job` for every hold.
- `Quote.pricing` is `per_page` for a quote paid from the wallet and `one_time` for the quote of a
  one-time order. `Quote.policy_evaluation` is the dry run of the policies that bind the caller, made
  with the quote (new schema `PolicyVerdict`).
- `FaxJob.approval_id` and `FaxJob.policy_version_id` say what authorized a send. `FaxJob.route_paused`
  says an operator paused sends on the fax's route.
- `PolicyEvaluation` declares `managed` and `usage` (new schema `PolicyUsage`). Its `decision` is
  `allow` or `deny`.
- `rotate_api_key` answers 409 for a key that expired. Its 409 names `details.reason` `key_expired` and
  says to create a new key. `cancel_topup_session` names `details.status` on its 409. In both,
  `error.code` is `conflict`.
- `PaymentReceipt.pdf_url` is null for a charge without an invoice, such as an automatic top-up. `url`
  opens the receipt in every case.
- The card of a one-time order is held, not authorized, in the descriptions of
  `create_one_time_checkout`, `OneTimeJob` and `Receipt.one_time`, and in the `x-llm` hint of
  `create_one_time_checkout`.
- `create_one_time_checkout` and its `x-llm` hint state the payment rule of 1.20.9. A failed fax costs
  nothing. A fax that stops part way is charged the price of the pages the carrier confirms.
- 14 schemas gain a description, among them `StatementLine`, `Delivery` and `PolicyEvaluation`. Six
  one-time schemas have theirs reworded. Fields of 17 schemas gain or change a description, among them
  `ErrorBody.retryable`, `Delivery.status`, `Capabilities.one_time` and `Document.received`.
- Not visible in the document: an adjustment line of the statement reads the note support wrote for the
  customer. The refusals of the dashboard sign-in carry `retry_after_s`, and every `auth` route stays out.

## 1.20.6 (2026-11-15)

API version 1.20.6, curated from the server document at that release. 128 paths, 161 operations and
170 schemas. 1.20.5 had 117, 147 and 152.

- New operation `get_statement`, `GET /v1/statement`. The wallet statement, newest first: one line per
  event with the balance after it. It filters by `kind`, `from` and `to`. New schemas `StatementPage`
  and `StatementLine`. Scope `billing:read`.
- New operation `get_statement_csv`, `GET /v1/statement.csv`. Every line the same filters select, as
  CSV. Scope `billing:read`.
- New operation `rename_document`, `PATCH /v1/documents/{document_id}`, with the body `DocumentUpdate`.
  A name without `.pdf` gets it added. Scope `document:write`.
- New operation `get_webhook_delivery`, `GET /v1/webhook-deliveries/{delivery_id}`. One delivery with
  the headers and the JSON body that were sent, never a secret (`DeliveryDetail`). Scope `webhook:admin`.
- New operation `delete_budget`, `DELETE /v1/budgets/{budget_id}`. A budget that never charged a hold
  is deleted. One with history is archived (`BudgetRemoved`). Scope `billing:write`.
- New operation `archive_agent`, `DELETE /v1/agents/{agent_id}`. The agent's keys are revoked and it
  leaves the list (`AgentArchived`). Scope `agent:admin`.
- New operation `dismiss_number_order`, `POST /v1/number-orders/{order_id}/dismissals`. It sets
  `dismissed_at` on a failed order. Any other order answers 409. Scope `number:buy`.
- New operation `create_policy_rule_check`, `POST /v1/policy-rule-checks`. It names the numbers of
  `allowed_destinations` that a listed country or prefix already allows. It stores nothing. Scope
  `policy:read`.
- New operations `resend_invitation` and `link_invitation`, `POST /v1/invitations/{invitation_id}/resend`
  and `.../link`. Both replace the link of an open invitation. The first mails it, the second answers
  it once (`InvitationLink`). Scope `member:admin`.
- New operation `list_data_requests`, `GET /v1/organizations/current/data-requests`, scope
  `account:read`. New operation `withdraw_data_deletion`,
  `DELETE /v1/organizations/current/deletion-requests/{request_id}`, scope `org:admin`. New schemas
  `DataRequest` and `DataRequestList`.
- New operation `preview_one_time_document`, `POST /v1/one-time-sends/preview`. It counts the pages of a
  file and draws its first page before any order exists (`OneTimeInspection`). It needs no credential
  and stores nothing.
- New operation `get_one_time_order_page`, `GET /v1/one-time-sends/{one_time_order_id}/pages/{page_number}`.
  One page of an order as a PNG, page 1 being the cover sheet. A key with `fax:read` or the order's
  status token reads it.
- New query parameters. `q` on `list_faxes` finds a destination or the start of a job id. `source`,
  `exclude_source` and `q` on `list_documents`. `archived` on `list_inbox`. `include_archived` on
  `list_agents` and `list_budgets`.
- `list_approval_requests` describes `status=used`: the approvals a send consumed. Their status reads
  `approved` and `consumed_by_job_id` names the fax.
- New fields. `DocumentPage.total` counts every document the filters match. `InboxPage.unread` counts
  the received faxes nobody opened yet, whatever the filters. `Balance.held_jobs`, `Quote.route_paused`,
  `OneTimeQueue.paused`, `Webhook.failing` and `Delivery.webhook_url`.
- More new fields. `Receipt.seller` (new schema `Seller`), `Receipt.provider_ref` and
  `Receipt.sender_name`. `Document.converted_from` and `Document.received` (new schema
  `DocumentReceived`). `InventoryNumber.owned` and `NumberOrder.dismissed_at`.
- `InboxItem.file_deleted_at` and `InboxItemDetail.file_deleted_at` say when the file of a received fax
  was deleted. `media_status` then reads `deleted`.
- Names in place of ids. `ApprovalRequest.requested_by_name` and `decided_by_name`,
  `PolicyVersion.created_by_name` and `AgentActivity.actor_label`. `ApprovalRequest.document` (new
  schema `ApprovalDocument`) is the document a send request binds.
- `Agent.archived_at`, `Budget.archived_at`, `OrganizationSummary.suspended_at`,
  `Capabilities.default_scopes` and `Capabilities.admin_scopes`. `Requested` carries `id` and
  `created_at`. `OneTimeOrder` carries `attempts` and `preview` (new schemas `OneTimeAttempts` and
  `OneTimePreview`). `OneTimeJob` carries six receipt fields.
- `PolicyEvaluationCreate` takes `key_id`, `agent_id` or `connection_id`, to evaluate as another caller
  of the organization. `PolicyEvaluation` answers `subject`, `under_policy` and `approval_required`.
- `OrganizationPatch.name` is at most 80 characters, down from 200. A longer name answers 422.
- `list_agents` and `list_budgets` declare 422. `delete_inbox_item`, `create_policy_evaluation` and
  `create_agent_key` have new summaries. `reject_request` says a help request closes without a reason.
  `Inventory.locality` is null in test.
- `preview_one_time_document` and `create_policy_rule_check` are marked as reads in `x-llm`. The server
  accepts an `Idempotency-Key` on them and ignores it.
- Three new routes of the dashboard sign-in (`preview_invitation`, `dismiss_notices` and
  `rename_passkey`, tag `auth`) stay out, as every `auth` route does.
- Not visible in the document: a one-page fax to the sandbox number `+15550000003` ends `failed` with
  `partial_delivery`, because a partial delivery keeps at least one page.

## 1.20.5 (2026-11-14)

API version 1.20.5, curated from the server document at that release. 117 paths, 147 operations and
152 schemas. 1.20.3 had 115, 145 and 151.

- New operation `get_invoice_receipt`, `GET /v1/invoices/{invoice_id}/receipt`. It returns the payment
  receipt of a paid invoice. Scope `billing:read`.
- New operation `get_topup_receipt`, `GET /v1/topup-sessions/{topup_session_id}/receipt`. It returns
  the payment receipt of a paid top-up, an automatic one included. Scope `billing:read`.
- New schema `PaymentReceipt`, the answer of both. `url` is the hosted receipt and `pdf_url` the same
  receipt as a PDF. Both operations answer 409 while the payment has no receipt yet.
- `UploadCreate.content_type` is optional and nullable. Left out, the type is read from the filename.
  A filename of an unsupported format is refused by `POST /v1/uploads` with 422 `unsupported_format`.
- `UploadCreate.size_bytes` is described as the exact byte count of the file.
- `AutoTopupCreate.threshold_micro` has a maximum of 1000000000, which is 1000 USD. A larger value
  answers 422.
- `AgentCreate.contact_email` and `AgentUpdate.contact_email` have the format `email`. A value that is
  not an address answers 422. An empty string still clears it.
- `POST /v1/approval-requests` declares 200 beside 201. A repeated request returns the open one.
- 413 is declared on every operation with a request body. 410 is declared on 138 operations, with the
  new shared response `Gone`: a document or a received fax past its retention date, or an organization
  that is being deleted.
- 16 schemas of the quickstart path carry `examples`: `Balance`, `Document`, `DocumentCreate`,
  `FaxCreate`, `FaxJob`, `InboxItemDetail`, `InboxPage`, `Quote`, `QuoteCreate`, `Receipt`,
  `SandboxInboundCreate`, `UploadCreate`, `UploadSession`, `Webhook`, `WebhookCreate` and
  `WebhookWithSecret`.
- `Capabilities.scopes` is described as every scope the platform defines. `GET /v1/me` returns the
  scopes of the calling credential.
- Not visible in the document: the 404 of `POST /v1/fax-quotes` carries `details.field`, and the 409 of
  a receipt asked for too early carries `details.state`. The 401 message names both prefixes,
  `ffa_test_` and `ffa_live_`. A sandbox scenario replaces the earlier one of the same destination, and
  an extraction on the sandbox engine costs 0.

## 1.20.3 (2026-11-14)

API version 1.20.3, curated from the server document at that release. 115 paths, 145 operations and
151 schemas, the same counts as 1.20.0. Only `info.version` changed in the document.

- 1.20.1, 1.20.2 and 1.20.3 changed no path, no operation and no schema. Since 1.20.1 a Canadian
  number answers `country` as `CA`. Before, it answered `US`.
- Fixed: `scripts/curate.py --vendor` dropped `ErrorEnvelope` and `ErrorBody` from
  `scripts/server-openapi.json`, because only the shared responses point at them. Curating the kept
  source then stopped with `KeyError: 'ErrorEnvelope'`. The kept source now holds every schema a shared
  response reaches. `--vendor` refuses a kept source that curates to a different document.
  `scripts/truthcheck.sh` curates the kept source in CI.

## 1.20.0 (2026-11-13)

API version 1.20.0, curated from the server document at that release. 115 paths, 145 operations and
151 schemas, the same counts as 1.18.0. No path, operation or schema was added or removed.

- New field `email_pdf` on `Number`, a boolean that is false by default. When true, the notice mail of
  a fax received on the number carries the PDF as an attachment. Live numbers only.
- New field `email_pdf` on `NumberUpdate`, the body of `PATCH /v1/numbers/{number_id}`. It needs the
  scope `number:buy`. An agent, an OAuth connection and a connected app are refused. The mail goes to
  the verified address of an owner. A PDF over 15 MB is not attached.
- The summary of `update_number` is now "Label, inbound route and PDF by mail of a number".
- Removed field: `provider_cost_micro` on `Extraction`, from its properties and its required list.
  The server stopped sending it at 1.19.0. A typed client that requires the field must drop it.
- Not visible in a schema: since 1.19.0 each item of `pages` on an extraction has no `cost_micro`, and
  `GET /v1/ledger` leaves out the entries of the `provider_cost` account. `price_micro` is unchanged.
- 1.18.1, 1.19.1 and 1.19.2 changed no path and no schema.

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
