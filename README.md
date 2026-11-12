<p align="center">
  <a href="https://faxforagents.com"><img src="https://faxforagents.com/brand/logo-512.png" width="88" alt="Fax for Agents"></a>
</p>

<h1 align="center">Fax for Agents OpenAPI document</h1>

<p align="center">The machine-readable contract of <a href="https://faxforagents.com">Fax for Agents</a>, the fax API built for AI agents.</p>

<p align="center">
  <a href="https://faxforagents.com">Website</a> ·
  <a href="https://faxforagents.com/docs/quickstart/">Quickstart</a> ·
  <a href="https://faxforagents.com/docs/api/">API reference</a> ·
  <a href="https://faxforagents.com/docs/sdks/">SDKs</a> ·
  <a href="https://faxforagents.com/mcp/">MCP</a> ·
  <a href="https://app.faxforagents.com">Dashboard</a> ·
  <a href="https://faxforagents.com/pricing/">Pricing</a> ·
  <a href="https://faxforagents.com/changelog/">Changelog</a> ·
  <a href="https://gitlab.com/faxforagents/openapi">GitLab</a>
</p>

<p align="center">
  <a href="https://github.com/faxforagents/openapi/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/faxforagents/openapi/ci.yml?branch=main&label=ci" alt="CI"></a>
  <a href="https://github.com/faxforagents/openapi/actions/workflows/lint.yml"><img src="https://img.shields.io/github/actions/workflow/status/faxforagents/openapi/lint.yml?branch=main&label=lint" alt="Lint"></a>
  <a href="https://github.com/faxforagents/openapi/blob/main/openapi.yaml"><img src="https://img.shields.io/badge/OpenAPI-3.1-6ba539" alt="OpenAPI 3.1"></a>
  <a href="https://github.com/faxforagents/openapi/blob/main/LICENSE"><img src="https://img.shields.io/badge/licence-MIT-1f6feb" alt="MIT licence"></a>
</p>

Fax for Agents is a fax API, a hosted MCP server and SDKs built so AI agents can send and receive
faxes. It is made by JSB Holdings LLC and built by [Synapse](https://synapsereality.io/). This
repository holds the public OpenAPI document of the API.

| File | What it is |
|---|---|
| [`openapi.yaml`](openapi.yaml) | OpenAPI 3.1, 145 operations in 115 paths, 152 schemas, version 1.17.0 |
| [`docs/`](docs/) | The rendered reference, published at <https://faxforagents.github.io/openapi/> |
| [`docs/llms.txt`](docs/llms.txt) | The same contract written for a model |
| [`scripts/curate.py`](scripts/curate.py) | Produces `openapi.yaml` from the server's own document |

The official SDKs are generated from this document. [Python](https://github.com/faxforagents/sdk-python),
[TypeScript](https://github.com/faxforagents/sdk-typescript) and the [MCP server](https://github.com/faxforagents/mcp).
When the document and an SDK disagree, the document is right and the SDK has a bug.

## Use it

Point any OpenAPI tool at the raw file.

```
https://raw.githubusercontent.com/faxforagents/openapi/main/openapi.yaml
```

The server also serves its own document at `https://api.faxforagents.com/openapi.json`. That one
includes operations a customer never calls. Those are the admin routes, the affiliate area of the
dashboard, the carrier and payment webhook receivers, and the dashboard's cookie sign-in. This repository is the curated, public form: every operation an API key can call,
and the one-time send. Whole path prefixes that stay out are in `EXCLUDED_PATHS` in
`scripts/curate.py`. Single operations left out are named in `EXCLUDED`, each with its reason.

## Base URL and keys

Base URL `https://api.faxforagents.com`. Send the key as `Authorization: Bearer ffa_live_...`, or in
`X-API-Key`. Keys are created in the dashboard at <https://app.faxforagents.com> or with
`POST /v1/api-keys`.

A test key (`ffa_test_...`) reaches the sandbox provider only. No carrier, no cost, nothing leaves the
box. A live key (`ffa_live_...`) reaches the carrier and spends the prepaid wallet.

Every operation carries an `x-llm` block naming the scope the call needs, whether the call mutates and
whether it honours `Idempotency-Key`. A key is minted with the scopes it needs. An agent's own API key
can never carry `approval:decide`, `key:admin`, `policy:admin`, `agent:admin`, `billing:write` or
`webhook:admin`.

## The send flow

```
POST /v1/documents            text, markdown, html or an upload     ->  doc_..., sha256, page_count
POST /v1/fax-quotes           document_id + to                      ->  quote_..., amount_micro, expires_at
POST /v1/faxes                quote_id (+ Idempotency-Key)          ->  fax_..., state queued
GET  /v1/faxes/{fax_id}       poll                                  ->  state, evidence once delivered
```

A file goes through `POST /v1/uploads` with its `content_type`, a `PUT` of the bytes to the signed
`upload_url`, `POST /v1/uploads/{id}/complete` with the sha256, then `POST /v1/documents` with the
`upload_id`. The file is a PDF or an image: `application/pdf`, `image/png`, `image/jpeg` or
`image/tiff`. An image becomes gray letter pages, every TIFF frame is a page. HTML passed as `html`
is rendered by a headless browser with scripts off and no network. Inline CSS and `data:` images
print, external resources are counted as blocked. At most 2 MiB of HTML.

Beyond the send flow the document covers keys, webhooks, events, billing, the sandbox, approvals,
delegated policies, agent identities and the inbox. It covers fax numbers: coverage, inventory, orders,
porting and sender verification. It covers extractions: OCR, fields, classification, summaries and
saved schemas. It covers the organization with its members, the auto-send setting and connected apps.

## One fax by card

A person with one fax to send needs no wallet. The `one-time-sends` operations make an order, open a
hosted card payment and release the fax when the sender clicks the link mailed to them.

```
GET  /v1/one-time-sends/config                 open here? the card, the limits      ->  enabled, routes
POST /v1/one-time-sends                        a file or text, to, email, accept_aup ->  oto_..., status_token
POST /v1/one-time-sends/{id}/checkout          open the hosted payment page         ->  checkout_url
POST /v1/one-time-sends/{id}/confirm           the token of the mailed link         ->  the order, fax released
GET  /v1/one-time-sends/{id}                   poll                                 ->  status, next, fax
GET  /v1/one-time-sends/{id}/receipt.pdf       once the fax ended                   ->  a one-page PDF
```

The create takes no key. It answers a status token once. Send the token as `X-FFA-Order-Token`, or as
`?t=`, to read the order, open its checkout and have the confirmation mailed again. A live key with
`fax:send` may create an order for its organization, and `POST /v1/one-time-sends/from-quote` turns
a live quote the wallet does not cover into an order. Paying by card does not replace approval. With a
key, the send must have an approval or a delegated policy, as a wallet send does. Pass the approval as
`approval_id` on the from-quote body. A test key is refused: an order is always live. The card is
authorized at checkout and charged only when the carrier confirms delivery.

The person who pays accepts the acceptable use policy and the terms, never a key. With a key, the
order starts with `aup_accepted` false and carries a `status_url`, the order's page. Hand that link to
the person who pays. They accept the terms there and the checkout opens. `queue` on the config and on the order says whether a
fax would wait for a carrier line, with `jobs_ahead` and `estimated_wait_minutes`. The confirm page
reads a mailed link with `POST /v1/one-time-sends/by-token` and the token in the body. The older
`GET /v1/one-time-sends/by-token/{token}` is deprecated.

## States

A fax job is in exactly one of six states.

| State | Meaning | Money |
|---|---|---|
| `queued` | accepted, waiting for the worker | held |
| `active` | at the carrier | held |
| `delivered` | every page arrived, the carrier's evidence is on the attempt | captured |
| `partial` | the call dropped after some pages, `pages_sent` says how many | those pages captured, the rest released |
| `failed` | nothing arrived, `failure_code` says why | released |
| `unknown` | the carrier gave no outcome, so nobody knows whether it arrived | held until a person reconciles |

`delivered` is never written without evidence. `partial` and `unknown` never retransmit on their own.
Whether to resend is a human decision.

## Sandbox destinations

With a test key, the destination number picks the outcome.

| Destination | Outcome |
|---|---|
| `+15550000001` | `delivered` on the first attempt |
| `+15550000002` | busy on attempt 1, `delivered` on attempt 2 |
| `+15550000003` | `partial` after 3 pages |
| `+15550000004` | no answer on all 3 attempts, `failed` |
| `+15550000005` | accepted, no outcome reported, `unknown` with `callback_missing` |
| `+15550000006` | the provider does not answer the send call, `unknown` with `provider_timeout` |
| `+15550000007` | rejected at once, `failed` with `invalid_number` |
| any other `+1` number | `delivered` |

`POST /v1/sandbox/scenarios` pins a scenario to a destination for 24 hours. `DELETE /v1/sandbox/data`
resets the organization's test data and reseeds the test wallet.

## Money

Amounts are integer USD micro-units. `39000` is $0.039. Price card launch-v2 is effective from
2026-10-31. $0.039 per page sent, $0.019 per page received. $2 per number per month, $19 per month
for the Agent workspace. Sandbox pages cost 0. `GET /v1/capabilities` returns the card in force with its
`price_version`.

One fax by card costs $2.49 for a document of up to 5 pages to a US or Canadian number, cover page
included. Each extra page is $0.49, up to 20 pages. These one-time prices were published on 2026-11-11.
`GET /v1/one-time-sends/config` returns them in micro-units while the product is open.

## Errors

One envelope on every error.

```json
{"error": {"code": "quote_expired", "message": "...", "retryable": false, "correlation_id": "..."}}
```

`402 insufficient_balance` on `POST /v1/faxes` has its own schema, `InsufficientBalance`: `details`
carries `available_micro`, `needed_micro` and `top_up_url`, the page where a person adds funds. It
carries `one_time_offer` too when the same send can be paid by card. `413 payload_too_large` answers a
request body over the limit of its route: 1 MB by default and 4 MB on `POST /v1/documents`. The bytes
of an upload and the one-time create form have their own larger limits. `429` carries `Retry-After`.
Repeat a mutating call with the same `Idempotency-Key` and the same resource comes back with
`Idempotent-Replayed: true`.

## Working on this repository

```bash
python scripts/curate.py              # regenerate openapi.yaml from the live server document
python scripts/curate.py --vendor     # the same, and keep the source in scripts/server-openapi.json
python scripts/build_reference.py     # regenerate docs/reference.html and docs/llms.txt
npx @redocly/cli lint openapi.yaml    # the lint CI runs
sh scripts/truthcheck.sh              # the facts CI pins
```

CI fails when `openapi.yaml`, the reference or `llms.txt` is stale. It fails when an operation lacks an
`operationId` or an `x-llm.scope`. It fails when a tracked file states a price that is not on the card.

## Licence

MIT. See [LICENSE](LICENSE). Security reports go to hello@faxforagents.com, see [SECURITY.md](SECURITY.md).
