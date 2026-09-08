# Harness capabilities

This skill runs in different harnesses with different tools connected. Do not assume any specific MCP server exists. Resolve what is actually available first, pick the best option present, and say which one you used.

Run this check once at the start of a session, before searching.

## How to resolve

1. Look at the tools actually available in this harness. Where the harness defers tool schemas, search for them by name before concluding something is missing.
2. For each function below, walk the list top to bottom and take the first option that is present and authorized.
3. If a server is listed but unauthorized, treat it as absent and note it — the human may need to connect it.
4. Record the chosen path in the `Run Log` `Notes` column. When a run finds nothing, the tool path is the first thing worth checking.

State the resolved path in your reply, briefly: `Reddit via Apify, Sheet via Zapier.`

## Function 1 — Reddit retrieval

Required. Without one of these the session cannot run.

| Preference | Tool | Notes |
|---|---|---|
| 1 | **Apify** actor (`call-actor` + `get-dataset-items`) | Real date windows, real comment ids, structured fields. See [reddit-search.md](reddit-search.md). |
| 2 | **Firecrawl** (`firecrawl_search`, `firecrawl_scrape`) | Can search and read Reddit pages. No native comment-level date filter — verify dates yourself from page content. |
| 3 | **Tavily** (`tavily_search`, `tavily_extract`) | Supports recency filtering. Search-index based, so coverage is partial. |
| 4 | **DataForSEO** (`serp_organic_live_advanced`) | SERP data for `site:reddit.com` queries. Discovery only. |
| 5 | **Built-in web search / fetch** | Last resort. |

Anything below rank 1 cannot enforce an exact incremental window. When using one, say so plainly in the reply: results may repeat or be missed, and the date range is best-effort rather than guaranteed.

If none are available, stop. Report that no Reddit retrieval tool is connected and name the options. Do not answer from memory and do not present recalled examples as findings.

## Function 2 — Sheet writing

| Preference | Tool | Notes |
|---|---|---|
| 1 | **Zapier** (`discover_zapier_actions` → Google Sheets → `execute_zapier_write_action`) | Real row appends. Enable the "Create Spreadsheet Row" action once per account. |
| 2 | **Composio** (`COMPOSIO_SEARCH_TOOLS` → Google Sheets → `COMPOSIO_MULTI_EXECUTE_TOOL`) | Same capability, different provider. |
| 3 | **Google Drive MCP** | Can create the Sheet and read it. It has no row-append tool, so appending means a read-modify-write of the whole file — acceptable for small Sheets, risky once they grow or if anything else is editing. Warn the human when falling back to this. |
| 4 | **Notion** (`notion-create-pages` into a database) | A legitimate destination when the client uses Notion instead of Sheets. Map the schema in [output.md](output.md) to database properties. |
| 5 | **Local CSV** | Write the file, report the path, tell the human to import it. |

Never silently skip the write. If no write path exists, deliver the full results in the reply, say clearly that nothing was saved, and name what needs connecting.

## Function 3 — Reading existing rows

Deduplication needs the canonical URLs and comment ids already recorded, and the incremental cursor needs the newest successful `Run Log` row.

Use whatever read path the write tool offers — Google Drive MCP's `read_file_content`, a Zapier or Composio lookup, or a Notion query. If the Sheet cannot be read, do not assume it is empty: report that dedup could not run and that the appended rows may repeat existing ones.

## Function 4 — Delivery (optional)

Only when the client or the caller asked for it.

Gmail for an email digest, Slack for a channel post, Notion for a written summary page. Never enable a delivery channel on your own initiative — a monitoring run that starts emailing people unprompted is a bug.

## Function 5 — Community discovery (onboarding only)

Finding candidate subreddits for a new client profile. Apify's community search (`searchCommunities: true`) is the direct route; a plain web search works too. Verify every proposed subreddit exists and is active before it goes in a profile.

## Degrading honestly

The rule throughout: use the best tool present, tell the user which one, and be explicit about what that choice cannot guarantee. A run on rank-4 tools is still useful research. A run on rank-4 tools described as if it were rank 1 is a fabrication.
