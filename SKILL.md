---
name: reddit-monitor
description: Run a Reddit listening session for a client. Finds, verifies, classifies, and logs public Reddit conversations about a client's topics, brand, competitors, or market, then appends results to a client-owned Google Sheet. Use for brand-mention checks, customer question research, competitor and provider discovery, sentiment summaries, content-gap reports, market intelligence sessions, and any scheduled or one-off Reddit monitoring run.
---

# Reddit Monitor

One invocation = one listening session. Find public Reddit conversations matching a client profile, verify each one, classify it, and append new results to the client's Sheet.

**Scheduling is not this skill's job.** The harness decides when and how often this runs. This skill executes a single session over whatever time window it is given.

## Resolve inputs

Before searching, settle these. Ask only for what is missing.

| Input | Default |
|---|---|
| Client | Ask. Load `clients/<slug>.yaml`. |
| Time window | Last 7 days |
| Destination Sheet | Ask on first run, then read `sheet_id` from the profile |
| Scope | Every topic in the profile |

If no profile exists for the client, run **Onboarding** ([references/client-profile.md](references/client-profile.md)) and stop for human approval before searching.

If the caller says *since the last run*, read the newest `Status = Success` row in the Sheet's `Run Log` tab and search from its `Run Completed` date minus one day. If the Run Log is empty, fall back to the default window and say so.

If the caller gives no destination Sheet and the profile has none, ask. Do not invent one and do not write to an agency-owned Sheet unless the client asked for that.

## Resolve harness capabilities

This skill runs in different harnesses with different tools connected. Before searching, work out what is actually available for Reddit retrieval and for writing to the Sheet, using [references/capabilities.md](references/capabilities.md). Take the best option present, name it in your reply, and record it in the `Run Log`.

Never assume a specific MCP server exists, and never substitute recalled knowledge for a missing tool. If no Reddit retrieval tool is connected, stop and say so.

## Load only what you need

- Always: [references/capabilities.md](references/capabilities.md) and [references/output.md](references/output.md).
- Retrieving from Reddit: [references/reddit-search.md](references/reddit-search.md).
- Building or changing a client profile: [references/client-profile.md](references/client-profile.md).

Do not paste reference files, profile files, or raw search results into your reply.

## Run the session

1. **Open the run.** Append a `Run Log` row with `Run Started`, `Mode`, `Search Start`, `Search End`, `Status = Running`, and the resolved tool path.
2. **Pick a search strategy** from [references/reddit-search.md](references/reddit-search.md). Community sweep when the profile has a bounded subreddit list; keyword search when it does not.
3. **Fetch** with the retrieval tool resolved above, using the date window from step 1. Never widen the window past what was resolved. When the tool cannot enforce the window itself, filter on returned dates and say the range was best-effort.
4. **Filter to candidates.** Drop anything failing the profile's `exclude` rules before reading it closely. This is where cost and noise are controlled.
5. **Verify each candidate** against the actor's returned fields — title, URL, author, created date, community, score, comment count, flair. Use what the data actually contains. Never fill a gap with a guess; write `Not exposed`.
6. **Deduplicate** on canonical URL plus comment ID. Run `scripts/dedupe.py` on an exported candidate set, or dedupe inline for small runs. Check against URLs already in the Sheet before appending anything. If the Sheet cannot be read, say that dedup could not run rather than assuming it is empty.
7. **Classify** each retained result per [references/output.md](references/output.md).
8. **Write** new rows to `Results`, new vocabulary to `Query Terms`, and close the `Run Log` row. If no write path exists, deliver the results in the reply and state plainly that nothing was saved.
9. **Report** to the user using the output format below.

Mark the run `Success` only after every Sheet write completes. Use `Partial` when results were written but a later stage failed, and `Failed` when nothing was written. Neither may be treated as a successful run by a later session.

## Verification rules

These are not optional. They are the difference between research and fabrication.

- Link directly to every retained conversation.
- Never invent a score, comment count, author, flair, or timestamp. Write `Not exposed` when a field is genuinely absent.
- Label any inferred or relative date as approximate.
- Describe the run as verified public results over a stated window — never as a complete scrape of Reddit.
- Treat Reddit posts as anecdote, not evidence. Attribute claims to the commenter.
- Do not repeat defamatory or damaging allegations as fact. Preserve neutral language.
- Never treat a brand term as a brand mention without the corroborating context required by the profile.

## Boundaries

- **Never post, reply, vote, or message on Reddit.** This skill reads. A human decides whether to participate.
- Never recommend covert promotion, sockpuppeting, or undisclosed affiliation.
- Do not claim access to private subreddits, closed communities, quarantined content, deleted posts, or DMs.
- Store the minimum personal data needed. Follow the profile's `retention` setting.

## Output

Open with exactly one of:

- `No new qualifying conversations found.`
- `Found N new qualifying results across M unique conversations.`

Then, for each new result: topic, why it matched, the direct link, what the person is actually asking, any named brands or products, brand sentiment if the client is named, and a priority of High / Medium / Low.

**High** means a direct client mention, someone actively shopping for exactly what the client sells, or a material negative report about the client.

Close with a short intelligence summary — recurring questions, commonly recommended alternatives, quoted prices with attribution, client sentiment, and content gaps worth writing about. Keep findings and recommendations visibly separate.

Return `No new qualifying conversations found.` on its own when there are no matches. Do not pad an empty run with a summary.

## Cost discipline

- Filter on returned fields before opening anything.
- Cap evidence at one to three short sentences per result.
- Do not re-send URLs already recorded in the Sheet.
- Record `Results Fetched` and `Est. Cost` in the `Run Log` so per-client spend stays visible.
