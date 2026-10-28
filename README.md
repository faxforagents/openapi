# Fax for Agents OpenAPI document

The machine-readable contract of the [Fax for Agents](https://faxforagents.com) API. Fax for Agents is
a fax API, a hosted MCP server and SDKs built so AI agents can send and receive faxes. It is made by
JSB Holdings LLC.

| File | What it is |
|---|---|
| [`openapi.yaml`](openapi.yaml) | OpenAPI 3.1, 127 operations in 100 paths, 132 schemas, version 1.1.0 |
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
includes operations a customer never calls: the admin routes, the carrier and payment webhook
receivers, and the dashboard's cookie sign-in (magic links, passkeys, OAuth, sessions). This
repository is the curated, public form: every operation an API key can call.

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
is rendered by a headless browser with scripts off and no network: inline CSS and `data:` images
print, external resources are counted as blocked. At most 2 MiB of HTML.

Beyond the send flow the document covers keys, webhooks, events, billing, the sandbox, approvals,
delegated policies, agent identities, the inbox, fax numbers (coverage, inventory, orders, porting,
sender verification), extractions (OCR, fields, classification, summaries, saved schemas) and the
organization with its members.

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

Amounts are integer USD micro-units. `39000` is $0.039. Price card launch-v1 is effective from
2026-10-28. $0.039 per page sent, $0.019 per page received. $2 per number per month, $19 per month
for the Agent workspace. Sandbox pages cost 0. `GET /v1/capabilities` returns the card in force with its
`price_version`.

## Errors

One envelope on every error.

```json
{"error": {"code": "quote_expired", "message": "...", "retryable": false, "correlation_id": "..."}}
```

`429` carries `Retry-After`. Repeat a mutating call with the same `Idempotency-Key` and the same
resource comes back with `Idempotent-Replayed: true`.

## Working on this repository

```bash
python scripts/curate.py              # regenerate openapi.yaml from the live server document
python scripts/build_reference.py     # regenerate docs/reference.html and docs/llms.txt
npx @redocly/cli lint openapi.yaml    # the lint CI runs
sh scripts/truthcheck.sh              # the facts CI pins
```

CI fails when `openapi.yaml`, the reference or `llms.txt` is stale. It fails when an operation lacks an
`operationId` or an `x-llm.scope`. It fails when a tracked file states a price that is not on the card.

## Licence

MIT. See [LICENSE](LICENSE). Security reports go to hello@faxforagents.com, see [SECURITY.md](SECURITY.md).
