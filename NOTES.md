# Assumptions, decisions, and future improvements

## Assumptions and decisions

1. One group runs one payout cycle. Each member receives the pot exactly once.
2. Members receive payouts in the order they were added: the first member receives week 1's pot, the second member receives week 2's pot, and so on.
3. Members may be added only before the first contribution is recorded. This avoids changing the pot size or payout order after a cycle has started.
4. Member names/IDs are trimmed and compared case-insensitively for duplicate detection and payment lookup.
5. A member's weekly contribution can be split across multiple positive payments. The total cannot exceed the fixed weekly contribution.
6. A week only closes when every member has paid the full contribution. A failed close records no payout and does not advance the week.
7. The pot equals the fixed weekly contribution multiplied by the number of members. The tracker records the payout; it does not transfer real money.
8. Money is stored as integer pesewas to avoid floating-point rounding errors. Inputs with more than two decimal places are rejected.
9. Once every member has received one payout, the cycle is complete and no further weeks can be closed.
10. The program is in-memory only. Data is lost when the program exits.

## What I would improve with more time

- Persist group state to a database or validated JSON file.
- Add transaction IDs, timestamps, and a contribution ledger for auditing.
- Separate member IDs from display names and support names that are not unique.
- Add richer CLI input handling and exportable reports.
- Add integration tests for the command-line interface and test persistence/recovery if added.
- Consider a configurable rule for missed contributions and a new cycle, if the product requirements define those behaviours.
