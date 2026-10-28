#!/usr/bin/env python3
"""Render ``openapi.yaml`` as plain HTML and as ``llms.txt``, with no JavaScript.

Provenance: livetennisapi-oss/openapi/scripts/build_reference.py (2026-10-28), reduced to what this
API needs. The reason it exists is the same. The interactive reference (Scalar, ``docs/index.html``)
renders on the client, and the crawlers of the answer engines do not run JavaScript. So every
operation, parameter, schema, scope and error code is written out here as text, from the same file
the SDKs are generated from, in CI, so it cannot drift.

Usage::

    python scripts/build_reference.py           # writes docs/reference.html and docs/llms.txt
    python scripts/build_reference.py --check   # fails when the outputs are stale (CI)
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "openapi.yaml"
DOCS = ROOT / "docs"
SITE = "https://faxforagents.com"
REPO = "https://github.com/faxforagents/openapi"

E = html.escape

STYLES = """
:root{--paper:#F4F3EF;--surface:#FFFFFF;--sunken:#ECEAE4;--line:#D9D6CE;--ink:#1A1B1E;--ink-2:#4A4E55;
--ink-3:#60656D;--accent:#1E6B5C;--warn:#9A5B0C;--danger:#B3261E}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 Geist,system-ui,sans-serif}
a{color:var(--accent)}
code,pre,.mono{font-family:"JetBrains Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums;font-size:13px}
code{background:var(--sunken);border-radius:2px;padding:0 3px}
pre{background:var(--sunken);border-radius:4px;padding:12px;overflow-x:auto}
header,main,footer{max-inline-size:960px;margin-inline:auto;padding-inline:16px}
header{display:flex;gap:16px;align-items:center;padding-block:16px;border-block-end:1px solid var(--line)}
header nav a{margin-inline-end:16px}
h1{font-size:28px;line-height:1.2;letter-spacing:-.01em}
h2{font-size:20px;margin-block-start:40px;padding-block-start:16px;border-block-start:1px solid var(--line)}
h3{font-size:16px;font-weight:500;margin-block-end:4px}
table{border-collapse:collapse;inline-size:100%;background:var(--surface);border:1px solid var(--line);font-size:13px}
th{text-align:start;background:var(--sunken);color:var(--ink-3);font-weight:500;font-size:12px;padding:8px;border-block-end:1px solid var(--line)}
td{padding:8px;border-block-end:1px solid var(--line);vertical-align:top}
.op{background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:12px 16px;margin-block:12px}
.method{display:inline-block;min-inline-size:56px;font-weight:500}
.meta{color:var(--ink-3);font-size:14px}
.scope{color:var(--ink-2)}
.wrap{overflow-x:auto}
footer{color:var(--ink-3);font-size:14px;padding-block:32px;border-block-start:1px solid var(--line);margin-block-start:48px}
@media (max-width:768px){header{flex-wrap:wrap}}
"""


def load_spec() -> dict[str, Any]:
    return yaml.safe_load(SPEC.read_text("utf-8"))


def resolve(node: Any, spec: dict[str, Any]) -> Any:
    if isinstance(node, dict) and "$ref" in node:
        name = node["$ref"].rsplit("/", 1)[1]
        return spec["components"]["schemas"][name]
    return node


def ref_name(node: Any) -> str | None:
    if isinstance(node, dict) and "$ref" in node:
        return str(node["$ref"]).rsplit("/", 1)[1]
    return None


def type_of(schema: Any) -> str:
    if not isinstance(schema, dict):
        return "any"
    if "$ref" in schema:
        return ref_name(schema) or "object"
    if "anyOf" in schema:
        return " or ".join(type_of(s) for s in schema["anyOf"])
    if "enum" in schema:
        return " | ".join(str(v) for v in schema["enum"])
    t = schema.get("type")
    if isinstance(t, list):
        return " or ".join(str(x) for x in t)
    if t == "array":
        return f"array of {type_of(schema.get('items', {}))}"
    if t == "object" and "additionalProperties" in schema and schema["additionalProperties"] not in (True, {}):
        return f"map of {type_of(schema['additionalProperties'])}"
    return str(t or "object")


def fields_of(schema: dict[str, Any]) -> list[tuple[str, str, bool, str]]:
    required = set(schema.get("required") or [])
    out = []
    for name, prop in (schema.get("properties") or {}).items():
        desc = prop.get("description", "") if isinstance(prop, dict) else ""
        out.append((name, type_of(prop), name in required, desc))
    return out


def schema_table(name: str, schema: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td><code>{E(n)}</code></td><td>{E(t)}</td><td>{'yes' if r else ''}</td><td>{E(d)}</td></tr>"
        for n, t, r, d in fields_of(schema)
    )
    desc = f"<p class='meta'>{E(schema['description'])}</p>" if schema.get("description") else ""
    if not rows:
        return f"<h3 id='schema-{E(name)}'>{E(name)}</h3>{desc}<p class='meta'>{E(type_of(schema))}</p>"
    return (
        f"<h3 id='schema-{E(name)}'>{E(name)}</h3>{desc}<div class='wrap'><table>"
        f"<thead><tr><th>field</th><th>type</th><th>required</th><th>meaning</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def body_ref(op: dict[str, Any]) -> str | None:
    content = (op.get("requestBody") or {}).get("content") or {}
    schema = (content.get("application/json") or {}).get("schema")
    return ref_name(schema)


def response_ref(op: dict[str, Any]) -> tuple[str, str | None]:
    for code, resp in (op.get("responses") or {}).items():
        if str(code).startswith("2"):
            content = (resp.get("content") or {}).get("application/json") or {}
            return str(code), ref_name(content.get("schema"))
    return "200", None


def render_operation(path: str, method: str, op: dict[str, Any]) -> str:
    llm = op.get("x-llm") or {}
    params = op.get("parameters") or []
    prow = "".join(
        f"<tr><td><code>{E(p['name'])}</code></td><td>{E(p['in'])}</td><td>{E(type_of(p.get('schema')))}</td>"
        f"<td>{'yes' if p.get('required') else ''}</td><td>{E(p.get('description') or (p.get('schema') or {}).get('description') or '')}</td></tr>"
        for p in params
    )
    ptable = (
        "<div class='wrap'><table><thead><tr><th>parameter</th><th>in</th><th>type</th><th>required</th><th>meaning</th></tr></thead>"
        f"<tbody>{prow}</tbody></table></div>"
        if prow
        else ""
    )
    body = body_ref(op)
    code, resp = response_ref(op)
    body_line = f"<p>Request body: <a href='#schema-{E(body)}'><code>{E(body)}</code></a></p>" if body else ""
    resp_line = (
        f"<p>Response {E(code)}: <a href='#schema-{E(resp)}'><code>{E(resp)}</code></a></p>"
        if resp
        else f"<p>Response {E(code)}: bytes</p>"
    )
    errors = ", ".join(c for c in (op.get("responses") or {}) if not str(c).startswith("2"))
    scope = llm.get("scope", "")
    flags = []
    if llm.get("mutating"):
        flags.append("mutating")
    if llm.get("idempotency_key"):
        flags.append("accepts Idempotency-Key")
    if llm.get("agent_key_allowed") is False:
        flags.append("never an agent key")
    hint = f"<p class='meta'>{E(llm['hint'])}</p>" if llm.get("hint") else ""
    desc = f"<p>{E(op['description'])}</p>" if op.get("description") else ""
    return (
        f"<div class='op' id='{E(op['operationId'])}'>"
        f"<h3><span class='method'>{method.upper()}</span> <code>{E(path)}</code></h3>"
        f"<p>{E(op.get('summary', ''))} <span class='meta'>operationId <code>{E(op['operationId'])}</code></span></p>"
        f"<p class='scope'>Scope: <code>{E(scope)}</code>" + (f". {E(', '.join(flags))}" if flags else "") + ".</p>"
        f"{hint}{desc}{ptable}{body_line}{resp_line}<p class='meta'>Errors documented: {E(errors)}.</p></div>"
    )


def build_html(spec: dict[str, Any]) -> str:
    info = spec["info"]
    by_tag: dict[str, list[str]] = {}
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            tag = (op.get("tags") or ["other"])[0]
            by_tag.setdefault(tag, []).append(render_operation(path, method, op))
    tags = [t for t in spec.get("tags", []) if t["name"] in by_tag]
    toc = "".join(f"<li><a href='#tag-{E(t['name'])}'>{E(t['name'])}</a>: {E(t.get('description', ''))}</li>" for t in tags)
    sections = "".join(
        f"<h2 id='tag-{E(t['name'])}'>{E(t['name'])}</h2><p>{E(t.get('description', ''))}</p>" + "".join(by_tag[t["name"]])
        for t in tags
    )
    schemas = "".join(schema_table(n, s) for n, s in spec["components"]["schemas"].items())
    description = "".join(f"<p>{E(par)}</p>" for par in info.get("description", "").split("\n\n"))
    ops = sum(len(v) for v in by_tag.values())
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fax for Agents API reference</title>
<meta name="description" content="{E(info.get('summary', ''))} Every operation, parameter, schema, scope and error code of the Fax for Agents API, version {E(info['version'])}, as plain HTML.">
<link rel="canonical" href="https://faxforagents.github.io/openapi/reference.html">
<style>{STYLES}</style>
</head>
<body>
<header><strong>Fax for Agents</strong><nav><a href="./">Interactive reference</a><a href="./reference.html" aria-current="page">Plain reference</a><a href="./llms.txt">llms.txt</a><a href="{E(SITE)}/docs">Docs</a><a href="{E(REPO)}">Source</a></nav></header>
<main>
<h1>{E(info['title'])} reference</h1>
<p class="meta">Version {E(info['version'])}. Base URL <code>{E(spec['servers'][0]['url'])}</code>. {ops} operations in {len(spec['paths'])} paths, {len(spec['components']['schemas'])} schemas. Generated from <a href="{E(REPO)}/blob/main/openapi.yaml">openapi.yaml</a>, no JavaScript needed.</p>
{description}
<h2>Authentication</h2>
<p>Send the key as <code>Authorization: Bearer ffa_live_...</code>, or in <code>X-API-Key</code>. Every operation below names the scope the key needs. <code>any</code> is any valid key. <code>signed-url</code> is a link the API minted for you, no key.</p>
<h2>Contents</h2>
<ul>{toc}<li><a href="#schemas">Schemas</a></li></ul>
{sections}
<h2 id="schemas">Schemas</h2>
{schemas}
</main>
<footer><p>Fax for Agents is made by JSB Holdings LLC, 8 The Green, Dover, DE 19901, US. <a href="mailto:hello@faxforagents.com">hello@faxforagents.com</a>. <a href="{E(SITE)}/terms">Terms</a>, <a href="{E(SITE)}/privacy">privacy</a>.</p></footer>
</body>
</html>
"""


def build_llms_txt(spec: dict[str, Any]) -> str:
    info = spec["info"]
    lines = [
        "# Fax for Agents API",
        "",
        f"> {info.get('summary', '')}",
        "",
        info.get("description", "").strip(),
        "",
        f"Base URL: {spec['servers'][0]['url']}. Version {info['version']}.",
        "Authentication: `Authorization: Bearer ffa_live_...` or `X-API-Key`. Test keys are `ffa_test_...` and reach the sandbox only.",
        "",
        "## Documents",
        "",
        f"- [OpenAPI 3.1 document]({REPO}/blob/main/openapi.yaml): the source of truth for the SDKs",
        "- [Plain HTML reference](https://faxforagents.github.io/openapi/reference.html): every operation and schema as text",
        f"- [Product documentation]({SITE}/docs): quickstart, webhooks, approvals, the sandbox",
        "- [MCP server](https://mcp.faxforagents.com/mcp/): the same operations as tools, initialize and tools/list work without a key",
        "",
        "## Operations",
        "",
    ]
    for tag in spec.get("tags", []):
        rows = []
        for path, ops in spec["paths"].items():
            for method, op in ops.items():
                if (op.get("tags") or [""])[0] != tag["name"]:
                    continue
                llm = op.get("x-llm") or {}
                extra = []
                if llm.get("idempotency_key"):
                    extra.append("Idempotency-Key")
                if llm.get("agent_key_allowed") is False:
                    extra.append("never an agent key")
                tail = f" ({', '.join(extra)})" if extra else ""
                rows.append(f"- `{method.upper()} {path}` {op.get('summary', '')}. Scope `{llm.get('scope', '')}`{tail}.")
                if llm.get("hint"):
                    rows.append(f"  {llm['hint']}")
        if rows:
            lines.append(f"### {tag['name']}")
            lines.append("")
            lines.append(tag.get("description", ""))
            lines.append("")
            lines.extend(rows)
            lines.append("")
    lines += [
        "## States",
        "",
        "A fax job is `queued`, `active`, `partial`, `failed`, `unknown` or `delivered`. `delivered` is written only",
        "with the carrier's evidence on the attempt. `partial` and `unknown` never retransmit on their own.",
        "",
        "## Sandbox destinations (test keys)",
        "",
        "- `+15550000001` delivered",
        "- `+15550000002` busy on attempt 1, delivered on attempt 2",
        "- `+15550000003` partial",
        "- `+15550000004` no answer, failed after 3 attempts",
        "- `+15550000005` outcome unknown, callback missing",
        "- `+15550000006` provider timeout, unknown",
        "- `+15550000007` invalid number, failed at once",
        "- any other `+1` number: delivered",
        "",
        "## Prices",
        "",
        "Price card launch-v1 is effective from 2026-10-28. $0.039 per page sent, $0.019 per page received.",
        "$2 per number per month, $19 per month for the Agent workspace. Amounts in the API are USD micro-units",
        "(39000 = $0.039). Sandbox pages cost 0.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    spec = load_spec()
    outputs = {DOCS / "reference.html": build_html(spec), DOCS / "llms.txt": build_llms_txt(spec)}
    if args.check:
        stale = [p.name for p, text in outputs.items() if not p.exists() or p.read_text("utf-8") != text]
        if stale:
            print(f"stale: {', '.join(stale)}. Run scripts/build_reference.py", file=sys.stderr)
            return 1
        print("docs/reference.html and docs/llms.txt are current")
        return 0
    DOCS.mkdir(exist_ok=True)
    for p, text in outputs.items():
        p.write_text(text, "utf-8")
        print(f"wrote {p.relative_to(ROOT)} ({len(text):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
