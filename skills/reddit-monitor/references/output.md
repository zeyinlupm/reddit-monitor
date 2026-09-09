# Classification and output

This file is the single source of truth for the result schema. The Sheet, the dedupe script, and the chat report all use the columns defined here. Do not define a competing column set anywhere else.

## Result schema

One row per unique qualifying post or comment.

| Column | Value |
|---|---|
| Found At | Timestamp of this run |
| Conversation Date | `createdAt`, or `commentCreatedAt` for a comment. Mark approximate dates as approximate. |
| Topic | A topic key from the client profile |
| Title | Original post title |
| Community | `r/<name>` |
| Location | Relevant city or region, or `n/a` when the profile has no geography |
| Intent | One value from the Intent list below |
| Match Type | Direct, Related, Comment-only, Brand mention, or Duplicate |
| Summary | One to three sentences. What the person is actually asking or reporting. |
| Key Mentions | Named brands, competitors, products, providers, and quoted prices |
| Sentiment | Positive, Negative, Mixed, or Neutral |
| Priority | High, Medium, or Low |
| Canonical URL | `https://www.reddit.com/r/<sub>/comments/<postid>/` |
| Comment ID | Reddit comment `id`, blank for a post |
| Response Status | New, Reviewing, Responded, Content Planned, or Closed. Always `New` on write. |
| Content Opportunity | Suggested article, FAQ, or video angle, or blank |
| Source | `reddit` |

**Deduplication key is `Canonical URL` + `Comment ID`.** Two comments on the same post are two different results, not duplicates. Only that pair together identifies a row.

The chat report shows a readable subset of these columns. It never introduces new ones.

## Keep

Retain a result only when all four hold:

1. It is publicly verifiable at a working link.
2. The topic match is substantive, not incidental.
3. It satisfies the profile's geography mode.
4. Its date falls inside the requested window.

## Reject

Drop it when any of these apply:

- It matches an `exclude` rule in the client profile.
- A brand term appears without the corroborating context the profile requires.
- The post is deleted, removed, or the body is gone.
- It is a bot post, a mod announcement, or automated boilerplate.
- It is the client's own marketing or a known affiliate.
- The topic drifted from what the client actually sells.

Exclusions are the load-bearing part of a profile. Keywords find noise; exclusions make the output usable. When a false positive gets through, fix the profile rather than filtering it by hand next time.

## Match Type

- **Direct** — explicitly discusses a monitored topic, product, or brand.
- **Related** — the language strongly implies the topic without naming it.
- **Comment-only** — the post predates the window but a qualifying comment falls inside it.
- **Brand mention** — the client or a tracked competitor is named.
- **Duplicate** — a cross-post or repeat submission of something already retained.

## Intent

Pick one primary intent. Profiles may add their own; these are the defaults.

Recommendation request · Product or service comparison · Price or cost · Problem or symptom · Outcome or review · Complaint · General discussion

## Sentiment

- **Positive** — clear recommendation, praise, or good outcome.
- **Negative** — dissatisfaction, warning, or an allegation of harm.
- **Mixed** — meaningful positives and negatives together.
- **Neutral** — a question, a factual mention, or no stated position.

Classify brand sentiment only from text that actually refers to the brand. Attribute experiences; do not endorse them as fact.

## Priority

- **High** — the client is named, someone is actively shopping for what the client sells, or there is a material negative report about the client.
- **Medium** — an on-topic question that fits the client's services and geography.
- **Low** — general discussion, weak geography, or background education.

## Sheet structure

Create the Sheet on the first run if it does not exist. Four tabs, headers in row 1, no pre-filled data rows.

**Results** — the columns above.

**Run Log** — Run Started · Run Completed · Mode · Search Start · Search End · Status · Results Fetched · New Results · Est. Cost · Notes

**Query Terms** — Term · Topic · Status · First Seen · Last Validated · Notes

**Setup** — Client · Timezone · Geography · Subreddits · Retention · Profile Version

Add data validation on Sentiment, Priority, Match Type, and Response Status. Apply it to the whole column rather than a fixed row range, so it never runs out.

`Run Log` is the run history and the incremental cursor. Read the newest `Status = Success` row to find where the last complete session ended. Never derive the next window from the newest `Conversation Date` — a late-indexed older post would silently open a gap.

## Reporting counts

Always separate:

- qualifying results (rows written);
- unique conversations (distinct canonical URLs);
- direct brand mentions;
- older posts carrying a new qualifying comment.

## Discovered terms

When a run surfaces genuinely new topic vocabulary, append it to `Query Terms` with `Status = Pending` and list it in the reply:

```text
Discovered terms:
- [term] → [topic] → [why it is worth keeping]
```

Only a human promotes a term to `Approved`. Quarantine any term that keeps dragging in false positives.
