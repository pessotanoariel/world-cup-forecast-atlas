# FIFA Group Tiebreak Implementation

Status: Implemented in v1.0

## Head-to-Head Mini-Table Approach

FIFA group ordering first applies overall points, overall goal difference, and overall goals scored. When teams remain tied after those overall criteria, the implementation applies head-to-head criteria using only matches played between the tied teams.

The implementation builds a mini-table for the tied teams and computes:

1. Head-to-head points
2. Head-to-head goal difference
3. Head-to-head goals scored

These values are calculated only from matches where both teams are part of the tied set.

## Criteria Order Implemented

The group ordering now follows this sequence:

1. Overall group points
2. Overall goal difference
3. Overall goals scored
4. Head-to-head points among the tied teams
5. Head-to-head goal difference among the tied teams
6. Head-to-head goals scored among the tied teams
7. If this resolves some teams but leaves others tied, rebuild the mini-table only among the remaining tied teams and reapply the head-to-head criteria
8. If teams are still tied after every modeled FIFA football criterion, use a simulator-specific deterministic fallback using Elo rating

Fair Play points and drawing of lots are not modeled in this project.

## Final Deterministic Fallback Using Elo Rating

Fair Play points and drawing of lots are not currently modeled in the project. To avoid unstable ordering when all implemented football criteria are tied, the standings builder uses Elo rating as a final deterministic fallback.

This is not labeled as FIFA Ranking and should not be interpreted as a replacement for the official FIFA criteria. It is only used after:

1. Overall group points
2. Overall goal difference
3. Overall goals scored
4. Head-to-head or tied-team mini-table criteria

If Elo ratings are also tied or unavailable, team name is used as the final stable ordering key so exports remain deterministic.

## Test Coverage

The test suite covers:

- A three-team tie fully resolved by head-to-head points
- A three-team tie resolved by head-to-head goal difference
- A three-team tie resolved by head-to-head goals scored
- A partial resolution where remaining tied teams require head-to-head criteria to be reapplied
- A regression case proving overall goal difference is applied before head-to-head
- A two-team tie resolved by direct head-to-head after overall criteria remain tied
- A tie that remains unresolved after all football criteria and is resolved by Elo rating
- Deterministic ordering when Elo ratings also match
- A regression case proving overall goal difference remains ahead of the Elo fallback

The tests use synthetic standings and match results so the tiebreak behavior is isolated from the current tournament data.

This implementation is considered complete for Version 1.
Future versions may add Fair Play if disciplinary data becomes available.
