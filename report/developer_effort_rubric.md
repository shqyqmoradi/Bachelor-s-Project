# Developer-effort rubric

Score 1 means least effort and 5 greatest effort. Criteria and anchors are fixed
before collecting scores; the assessor must cite repository evidence in every row.

| Criterion | Weight | 1 | 3 | 5 |
|---|---:|---|---|---|
| Setup | 15% | one automated command | 3–5 manual steps | >8 steps or OS-specific repair |
| Schema/model | 15% | direct constraints/model | moderate duplication | extensive app-enforced integrity |
| Benchmark queries | 15% | simple native expressions | several joins/stages | complex workaround/multi-pass |
| Relations/integrity | 15% | server-enforced | mixed | mostly application-enforced |
| Migration | 10% | transactional/simple | tool-assisted | risky data rewrite/manual rollout |
| Index management | 10% | obvious few indexes | workload analysis needed | many special/duplicated indexes |
| Backup/restore | 10% | one command each | flags/validation needed | multi-component coordination |
| Debugging/observability | 10% | unified explain/logs | several tools | limited edition/tool visibility |

Scores 2 and 4 are used when evidence lies between adjacent anchors. Weighted
score is `sum(score × weight)` and therefore remains in [1,5]. Code line count is
reported separately as an observable proxy, not silently converted to ease. The
final assessment should be performed after following README from a clean machine,
with time and problems recorded in a lab diary.

