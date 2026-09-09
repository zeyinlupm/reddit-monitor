# Client profiles

A profile is what makes this skill client-specific. Everything else — searching, verification, classification, Sheet writing — is identical for every client.

Profiles live in `clients/<slug>.yaml`. Start from `clients/_template.yaml`.

## Onboarding a new client

Never invent a profile and start scraping. Draft it, get a human to approve it, then run.

1. **Collect the brief.** What the client sells, who buys it, where they operate, their brand and staff names, their competitors, and what a genuinely useful result would look like.
2. **Propose subreddits.** Use the actor's community search (`searchCommunities: true`) to find candidates. For local clients, city and regional subs. For national or niche clients, interest and profession subs. Verify each one exists and is active — a dead subreddit costs a request on every run forever.
3. **Draft the vocabulary.** For each topic, collect formal terms, everyday phrasing, abbreviations, common misspellings, and product or brand names. Include how customers actually talk, not only industry language.
4. **Draft the exclusions.** This is the real work. What looks like a match but is not? Adjacent products the client does not sell, a brand name that is also an ordinary phrase, competitor-only discussion with no opportunity in it.
5. **Set the brand rules.** For any brand term that is also a common word, list what else must appear before it counts as a mention.
6. **Write the draft and stop.** Show the human the proposed subreddits, vocabulary, and exclusions for approval before the first real run.
7. **Do a calibration run** over a short window. Review the output together. Almost every fix belongs in `exclude`.

## Profile fields

**`client`** — slug, display name, and the destination `sheet_id` once it exists.

**`geography.mode`** — one of:

- `local` — a named city and region list. Results must connect to it.
- `regional` — a broader area, looser matching.
- `national` — country-level; ignore city signals.
- `none` — geography is irrelevant. Do not filter on it and write `n/a` in the Location column.

Geography is optional. Do not assume a client has one.

**`subreddits`** — the bounded list that drives a community sweep. Leave empty to force keyword search instead.

**`topics`** — a keyed map. Each topic carries `terms` (what to match) and optionally its own `exclude`.

**`brand`** — the client's own names, domains, and staff names, plus `requires_context` for any term that is also an ordinary phrase.

**`competitors`** — tracked so their mentions get captured too. Often the most useful column in the whole Sheet.

**`exclude`** — global rejection rules applied before anything else.

**`retention`** — how long results stay in the Sheet before purging. Set it. These rows tie real usernames to whatever they were discussing.

## Brand terms that are ordinary words

A brand called "Bright Path Dental" will collide with every use of the phrase "bright path." Handle it in the profile, not by hand:

```yaml
brand:
  terms: ["Bright Path Dental", "brightpathdental.com"]
  requires_context:
    - term: "bright path"
      needs_any: ["dental", "dentist", "clinic", "City A", "Dr. Example"]
```

A bare term matches on its own. A `requires_context` term counts only when at least one supporting signal appears nearby. When neither holds, it is not a brand mention — no matter how much you would like it to be.

## Keeping a profile healthy

- New vocabulary arrives through `Query Terms` in the Sheet, marked `Pending`. A human approves it. Approved terms get folded back into the profile.
- Every false positive is a missing `exclude` rule. Add it once instead of filtering it forever.
- Bump `profile_version` on any change so a run can be traced to the config that produced it.
- Once three clients in one industry share most of a profile, pull the common part into a shared base and have each profile extend it. Not before — guessing at shared structure with one or two clients produces the wrong abstraction.
