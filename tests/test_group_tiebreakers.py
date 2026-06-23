import pandas as pd

from src.simulation.build_group_standings import sort_group_standings


def _standings(rows):
    return pd.DataFrame(
        [
            {
                "team": team,
                "PJ": 3,
                "PG": 0,
                "PE": 0,
                "PP": 0,
                "GF": gf,
                "GC": 0,
                "DG": dg,
                "PTS": pts,
                "H2H_PTS": 0,
                "H2H_DG": 0,
                "H2H_GF": 0,
                "group": "A",
            }
            for team, pts, dg, gf in rows
        ]
    )


def _predictions(matches):
    return pd.DataFrame(
        [
            {
                "team_1": team_1,
                "team_2": team_2,
                "team_1_goals": goals_1,
                "team_2_goals": goals_2,
            }
            for team_1, team_2, goals_1, goals_2 in matches
        ]
    )


def _ordered_teams(standings_df, predictions_df):
    return sort_group_standings(
        standings_df,
        predictions_df
    )["team"].tolist()


def test_three_team_tie_resolved_by_head_to_head_points():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 0, 4),
            ("C", 6, 0, 4),
            ("D", 0, -6, 0),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 1, 0),
            ("A", "C", 1, 0),
            ("B", "C", 1, 0),
        ]
    )

    assert _ordered_teams(standings_df, predictions_df)[:3] == [
        "A",
        "B",
        "C",
    ]


def test_three_team_tie_resolved_by_head_to_head_goal_difference():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 0, 4),
            ("C", 6, 0, 4),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 3, 0),
            ("B", "C", 1, 0),
            ("C", "A", 1, 0),
        ]
    )

    assert _ordered_teams(standings_df, predictions_df) == [
        "A",
        "C",
        "B",
    ]


def test_three_team_tie_resolved_by_head_to_head_goals_scored():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 0, 4),
            ("C", 6, 0, 4),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 3, 1),
            ("B", "C", 4, 2),
            ("C", "A", 2, 0),
        ]
    )

    assert _ordered_teams(standings_df, predictions_df) == [
        "B",
        "C",
        "A",
    ]


def test_partial_resolution_reapplies_head_to_head_to_remaining_tie():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 0, 4),
            ("C", 6, 0, 4),
            ("D", 6, 0, 4),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 2, 0),
            ("A", "C", 0, 0),
            ("A", "D", 2, 0),
            ("B", "C", 2, 0),
            ("B", "D", 0, 0),
            ("C", "D", 2, 0),
        ]
    )

    assert _ordered_teams(standings_df, predictions_df) == [
        "A",
        "B",
        "C",
        "D",
    ]


def test_overall_goal_difference_is_applied_before_head_to_head():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 10, 10),
            ("C", 3, 0, 3),
            ("D", 0, -10, 0),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 1, 0),
        ]
    )

    assert _ordered_teams(standings_df, predictions_df)[:2] == [
        "B",
        "A",
    ]


def test_head_to_head_is_applied_after_overall_points_goal_difference_and_goals():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 0, 4),
            ("C", 3, 0, 3),
            ("D", 0, -10, 0),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 1, 0),
        ]
    )

    assert _ordered_teams(standings_df, predictions_df)[:2] == [
        "A",
        "B",
    ]


def test_elo_resolves_tie_after_all_football_criteria_fail():
    standings_df = _standings(
        [
            ("A", 6, 0, 4),
            ("B", 6, 0, 4),
            ("C", 3, -2, 2),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 1, 1),
        ]
    )

    ordered_df = sort_group_standings(
        standings_df,
        predictions_df,
        {
            "A": 1800,
            "B": 1900,
        }
    )

    assert ordered_df["team"].tolist()[:2] == [
        "B",
        "A",
    ]


def test_elo_fallback_preserves_deterministic_ordering_when_ratings_match():
    standings_df = _standings(
        [
            ("B", 6, 0, 4),
            ("A", 6, 0, 4),
            ("C", 3, -2, 2),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 1, 1),
        ]
    )

    ordered_df = sort_group_standings(
        standings_df,
        predictions_df,
        {
            "A": 1900,
            "B": 1900,
        }
    )

    assert ordered_df["team"].tolist()[:2] == [
        "A",
        "B",
    ]


def test_overall_goal_difference_remains_before_elo_fallback():
    standings_df = _standings(
        [
            ("A", 6, 1, 4),
            ("B", 6, 0, 4),
            ("C", 3, -2, 2),
        ]
    )
    predictions_df = _predictions(
        [
            ("A", "B", 1, 1),
        ]
    )

    ordered_df = sort_group_standings(
        standings_df,
        predictions_df,
        {
            "A": 1800,
            "B": 1900,
        }
    )

    assert ordered_df["team"].tolist()[:2] == [
        "A",
        "B",
    ]
