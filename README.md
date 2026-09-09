# reddit-monitor

A Claude/ChatGPT Skill that runs a Reddit listening session for a client: find public conversations matching a client profile, verify them, classify them, and append the new ones to a client-owned Google Sheet.

Built by Redding Designs to run across multiple clients from one engine.

## How it splits

**The skill** does one session over one time window. It does not know or care about scheduling.

**The harness** — cron, a scheduled task, or a person typing — decides when it runs and how far back it looks.

**The client profile** (`skills/reddit-monitor/clients/<slug>.yaml`) holds everything client-specific: topics, vocabulary, subreddits, brand terms, exclusions, geography. Adding a client means adding a YAML file, not editing the skill.

## Layout

```
.claude-plugin/
  plugin.json                 plugin manifest
  marketplace.json            marketplace manifest (lets this repo be added as a plugin source)
skills/reddit-monitor/
  SKILL.md                    the session: inputs, workflow, rules, output
  references/
    capabilities.md           which MCP tools to use for each function
    reddit-search.md          Apify actor usage, search strategy, cost
    output.md                 result schema, classification, Sheet structure
    client-profile.md         profile format and client onboarding
  clients/
    _template.yaml            start here for a new client
  scripts/
    dedupe.py                 canonicalize URLs, drop repeat results
```

## Portability

The skill resolves what the harness actually has before it runs. Reddit retrieval prefers Apify, then Firecrawl, Tavily, DataForSEO, and plain web search. Writing prefers Zapier or Composio for real row appends, then Google Drive, Notion, or a local CSV.

It always names the path it used and states what that choice cannot guarantee — only the top retrieval option can enforce an exact date window. Nothing is ever answered from memory when a tool is missing.

## Adding a client

1. Copy `skills/reddit-monitor/clients/_template.yaml` to `skills/reddit-monitor/clients/<slug>.yaml`.
2. Run the onboarding steps in `skills/reddit-monitor/references/client-profile.md` — the skill will propose subreddits, vocabulary, and exclusions from a brief.
3. Have a human approve the draft.
4. Do a short calibration run and review the output together. Nearly every correction belongs in `exclude`.
5. Record the Sheet id in the profile.

## Data source

Reddit data comes from the `harshmaur/reddit-scraper` Apify actor, roughly $0.002 per result. It is used instead of web search because it enforces a real date window and returns real comment ids — neither of which `site:reddit.com` searching can do.

Actual result counts and cost go in the Sheet's `Run Log`, per run, per client.

## Ground rules

- The skill reads. It never posts, replies, votes, or messages.
- No covert promotion, ever.
- Nothing is invented — an absent field is written as `Not exposed`.
- Sheets are client-owned.
- Profiles carry a retention setting. Results tie usernames to whatever they were discussing; do not keep them forever.

## Verify the script

```sh
python skills/reddit-monitor/scripts/dedupe.py --selfcheck
```
