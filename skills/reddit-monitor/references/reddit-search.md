# Reddit search

This file details the preferred retrieval path. [capabilities.md](capabilities.md) decides which path is actually available — check there first. The strategy, field selection, and cost discipline below apply whichever tool you end up using.

## Actor

`harshmaur/reddit-scraper` on Apify. Pay per result (~$0.002 on the free tier, less on paid). Call it with `call-actor`, then read results with `get-dataset-items`.

Prefer it over web search. Google ranks by relevance rather than recency, indexes Reddit partially and late, and gives no dependable date filter — which makes an incremental window unenforceable. The actor returns real timestamps, real comment IDs, and real community names.

If Apify is unavailable, drop to the next option in [capabilities.md](capabilities.md) and be explicit in your reply that the date window is best-effort.

## Pick a strategy

**Community sweep** — use when the profile has a bounded `subreddits` list (local and regional clients).

Pull everything posted in those subreddits inside the window, then filter locally against the profile vocabulary. Local subreddits are low volume, so this is cheap and it does not depend on Reddit's search index at all. It is the only approach that reliably catches a post whose wording never matches your keywords.

```json
{
  "subredditUrls": ["londonontario", "kitchener", "Hamilton"],
  "postedAfter": "2026-09-01",
  "postedBefore": "2026-09-08",
  "crawlCommentsPerPost": true,
  "commentedAfter": "2026-09-01",
  "maxPostsCount": 500,
  "maxCommentsPerPost": 50
}
```

**Keyword search** — use when the profile has no subreddit list, or `geography.mode` is `national` or `none`.

```json
{
  "searchTerms": ["\"brand name\"", "topic phrase"],
  "searchSort": "new",
  "postedAfter": "2026-09-01",
  "searchComments": true,
  "maxPostsCount": 200
}
```

Both can run together. Sweep the known communities, and keyword-search Reddit-wide for brand terms that could surface anywhere.

## Constraints that shape the call

- **`withinCommunity` accepts one subreddit only.** For several communities use `subredditUrls` (an array) or filter results on `communityName` afterwards. Do not loop one run per subreddit unless the list is tiny — it multiplies the start fee.
- **Dates are `YYYY-MM-DD`, UTC, whole days.** There is no hour precision, so any incremental run carries at least a one-day overlap by design. Dedupe absorbs it.
- **`postedAfter` overrides `searchTime`** and forces newest-first ordering.
- **Reddit caps any listing near 1,000 posts.** A wide query over a busy window may be partly unreachable. Narrow the window rather than raising the cap.
- **Free Apify plans process the first 40 `searchTerms` per run.** Extra terms are silently skipped.
- **Comments need `crawlCommentsPerPost: true`**, and `commentedAfter` only filters once comments are actually being collected. Without it you will never find a new comment on an older post.

## Fields worth keeping

From each result: `id`, `postId`, `postUrl`, `title`, `body`, `authorName`, `createdAt`, `commentCreatedAt`, `communityName`, `score`, `commentsCount`, `flair`, `dataType`.

`dataType` distinguishes a post from a comment — it drives `Match Type` and decides whether `Comment ID` gets filled.

Everything else in the payload (media, awards, engagement ratios, subreddit rules) is noise for this purpose. Do not carry it into the Sheet or into your reply.

## Do not enable

- **`aiAnalysis` / `customLabels`** — the actor's own sentiment and intent taxonomy will not match the client profile, and classification is the part of this job worth doing carefully. Bill for it only if a client specifically wants the actor's scoring alongside ours.
- **`mcpConnector`** — it can write straight to a Sheet, but that skips verification and classification entirely and would put raw scrape output in front of a client.
- **`includeNSFW`** — leave off unless a profile explicitly needs it.

## Cost

Roughly: `results × $0.002 + $0.02 per run start per GB`.

A bounded local sweep over one day is usually a few hundred results at most. Record the actual count in the `Run Log` rather than estimating from memory — the first few runs are how you learn what a client actually costs.

If a run is about to exceed a few thousand results, stop and narrow the window or the subreddit list first. Say so rather than silently spending.

## Fallback

If Apify is unavailable, web search with `site:reddit.com/r/<sub>/comments/` still works for a one-off targeted look. Do not use it for incremental monitoring — state plainly that the date window could not be enforced and that results may repeat or be missed.
