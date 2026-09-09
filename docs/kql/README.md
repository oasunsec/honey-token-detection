# Investigation queries

| Question | Query |
| --- | --- |
| What arrived? | [All hits](canary-hits.kql) |
| Which requests started a window? | [First hits](canary-first-hits.kql) |
| Which callbacks repeated? | [Repeat hits](canary-repeat-hits.kql) |
| Which looked automated? | [Scanner hits](canary-scanner-hits.kql) |
| Which could create a High incident? | [High-severity access](canary-high-severity.kql) |
| What activity shares a source? | [By source](activity-by-source.kql) |
| Which decoys were retrieved? | [By canary](activity-by-canary.kql) |
| When did repeats occur? | [Repeat timeline](repeat-activity-over-time.kql) |
| What happened around one incident? | [Investigate a canary](investigate-canary.kql) |

The Bicep deployment loads the first-access and scanner rules from these files.

`RepeatCount` counts earlier matching requests in the receiver window. Use `countif(IsDuplicate)` to count repeat rows. A scanner-like User-Agent is only a heuristic, and `SourceIp` can be an ingress address rather than a user address.
