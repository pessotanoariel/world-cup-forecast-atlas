from itertools import combinations
from pathlib import Path

import pandas as pd

from src.predictor.generate_predictions import generate_predictions
from src.simulation import build_group_standings as standings_module
from src.simulation.build_group_standings import (
    build_group_match_results,
    load_completed_group_results,
)


def _current_group_matches():
    predictions_df = pd.read_csv("data/output/predictions.csv")
    groups_df = pd.read_csv("data/raw/world_cup_groups.csv")

    return build_group_match_results(predictions_df, groups_df)


def test_group_match_results_cover_72_matches():
    group_matches_df = _current_group_matches()

    assert len(group_matches_df) == 72


def test_each_group_has_four_teams():
    groups_df = pd.read_csv("data/raw/world_cup_groups.csv")

    assert groups_df.groupby("group")["country"].nunique().eq(4).all()


def test_each_team_has_three_group_matches():
    group_matches_df = _current_group_matches()
    appearances = pd.concat(
        [
            group_matches_df[["team_1"]].rename(columns={"team_1": "team"}),
            group_matches_df[["team_2"]].rename(columns={"team_2": "team"}),
        ],
        ignore_index=True
    )

    assert appearances.value_counts("team").eq(3).all()


def test_prediction_probabilities_are_normalized():
    predictions_df = pd.read_csv("data/output/predictions.csv")
    probability_sum = (
        predictions_df["team_1_win_probability"]
        + predictions_df["draw_probability"]
        + predictions_df["team_2_win_probability"]
    )

    assert probability_sum.between(0.999, 1.001).all()


def test_generate_predictions_normalizes_extreme_probabilities():
    input_df = pd.DataFrame(
        [
            {
                "match_date": "2026-06-01",
                "team_1_name": "A",
                "team_2_name": "B",
                "team_1_win_expectancy": 0.99,
                "draw_probability": 0.80,
                "form_score_difference": 1.0,
            }
        ]
    )

    predictions_df = generate_predictions(input_df)
    row = predictions_df.iloc[0]

    assert (
        row["team_1_win_probability"]
        + row["draw_probability"]
        + row["team_2_win_probability"]
    ) == 1.0


def test_completed_group_results_replace_predictions_in_standings(
    tmp_path,
    monkeypatch,
):
    groups_df = pd.DataFrame(
        {
            "group": ["A", "A", "A", "A"],
            "country": ["A", "B", "C", "D"],
            "country_code": ["AAA", "BBB", "CCC", "DDD"],
            "host": [0, 0, 0, 0],
        }
    )
    predictions_df = pd.DataFrame(
        [
            ("2026-06-01", "A", "B", "0-5"),
            ("2026-06-01", "C", "D", "1-0"),
            ("2026-06-02", "A", "C", "1-0"),
            ("2026-06-02", "B", "D", "1-0"),
            ("2026-06-03", "A", "D", "1-0"),
            ("2026-06-03", "B", "C", "1-0"),
        ],
        columns=["match_date", "team_1", "team_2", "predicted_score"],
    )
    predictions_df["team_1_win_probability"] = 0.5
    predictions_df["draw_probability"] = 0.2
    predictions_df["team_2_win_probability"] = 0.3
    predictions_df["predicted_winner"] = "A"
    predictions_df["confidence"] = "Medium"
    predictions_df["upset_risk"] = "LOW"

    completed_df = pd.DataFrame(
        [
            {
                "match_date": "2026-06-01",
                "team_1": "A",
                "team_2": "B",
                "team_1_goals": 2,
                "team_2_goals": 0,
                "result_source": "actual",
            }
        ]
    )

    predictions_path = tmp_path / "predictions.csv"
    groups_path = tmp_path / "groups.csv"
    output_path = tmp_path / "group_standings.csv"
    qualified_path = tmp_path / "qualified_teams.csv"
    predictions_df.to_csv(predictions_path, index=False)
    groups_df.to_csv(groups_path, index=False)

    monkeypatch.setattr(standings_module, "PREDICTIONS_PATH", predictions_path)
    monkeypatch.setattr(standings_module, "GROUPS_PATH", groups_path)
    monkeypatch.setattr(standings_module, "OUTPUT_PATH", output_path)
    monkeypatch.setattr(standings_module, "QUALIFIED_PATH", qualified_path)
    monkeypatch.setattr(standings_module, "load_elo_ratings", lambda: {})
    monkeypatch.setattr(
        standings_module,
        "load_completed_group_results",
        lambda groups: completed_df,
    )

    match_results_df = build_group_match_results(predictions_df, groups_df)
    standings_df = standings_module.build_group_standings()

    actual_match = match_results_df[
        (match_results_df["team_1"] == "A")
        & (match_results_df["team_2"] == "B")
    ].iloc[0]
    team_a = standings_df[standings_df["team"] == "A"].iloc[0]
    team_b = standings_df[standings_df["team"] == "B"].iloc[0]

    assert len(match_results_df) == 6
    assert actual_match["result_source"] == "actual"
    assert actual_match["team_1_goals"] == 2
    assert actual_match["team_2_goals"] == 0
    assert team_a["PTS"] == 9
    assert team_b["PTS"] == 6
    assert Path(output_path).exists()


def test_valid_group_stage_results_are_accepted(tmp_path):
    groups_df = pd.DataFrame(
        {
            "group": ["A", "A", "A", "A"],
            "country": ["A", "B", "C", "D"],
        }
    )
    teams_df = pd.DataFrame(
        {
            "country_code": ["AAA", "BBB", "CCC", "DDD"],
            "team_name": ["A", "B", "C", "D"],
        }
    )
    results_df = pd.DataFrame(
        [
            {
                "match_date": "2026-06-01",
                "tournament_code": "WC",
                "team_1_code": "AAA",
                "team_2_code": "BBB",
                "team_1_goals": 2,
                "team_2_goals": 1,
            }
        ]
    )
    latest_results_path = tmp_path / "latest_results.csv"
    teams_lookup_path = tmp_path / "teams_lookup.csv"
    results_df.to_csv(latest_results_path, index=False)
    teams_df.to_csv(teams_lookup_path, index=False)

    completed_df = load_completed_group_results(
        groups_df,
        latest_results_path=latest_results_path,
        teams_lookup_path=teams_lookup_path,
    )

    assert len(completed_df) == 1
    assert completed_df.iloc[0]["team_1"] == "A"
    assert completed_df.iloc[0]["team_2"] == "B"


def test_cross_group_knockout_results_are_ignored(tmp_path, caplog):
    groups_df = pd.DataFrame(
        {
            "group": ["A", "A", "B", "B"],
            "country": ["A", "B", "C", "D"],
        }
    )
    teams_df = pd.DataFrame(
        {
            "country_code": ["AAA", "BBB", "CCC", "DDD"],
            "team_name": ["A", "B", "C", "D"],
        }
    )
    results_df = pd.DataFrame(
        [
            {
                "match_date": "2026-06-01",
                "tournament_code": "WC",
                "team_1_code": "AAA",
                "team_2_code": "BBB",
                "team_1_goals": 2,
                "team_2_goals": 1,
            },
            {
                "match_date": "2026-06-28",
                "tournament_code": "WC",
                "team_1_code": "AAA",
                "team_2_code": "CCC",
                "team_1_goals": 1,
                "team_2_goals": 0,
            },
        ]
    )
    latest_results_path = tmp_path / "latest_results.csv"
    teams_lookup_path = tmp_path / "teams_lookup.csv"
    results_df.to_csv(latest_results_path, index=False)
    teams_df.to_csv(teams_lookup_path, index=False)

    completed_df = load_completed_group_results(
        groups_df,
        latest_results_path=latest_results_path,
        teams_lookup_path=teams_lookup_path,
    )

    assert len(completed_df) == 1
    assert "Ignored 1 non-group-stage match(es)" in caplog.text
    assert "A vs C" in caplog.text


def test_standings_generation_ignores_knockout_match_in_latest_results(
    tmp_path,
    monkeypatch,
):
    groups_df = pd.DataFrame(
        {
            "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
            "country": ["A", "B", "C", "D", "E", "F", "G", "H"],
        }
    )
    teams_df = pd.DataFrame(
        {
            "country_code": [
                "AAA", "BBB", "CCC", "DDD",
                "EEE", "FFF", "GGG", "HHH",
            ],
            "team_name": ["A", "B", "C", "D", "E", "F", "G", "H"],
        }
    )
    prediction_rows = []
    for group_teams in [["A", "B", "C", "D"], ["E", "F", "G", "H"]]:
        prediction_rows.extend(
            ("2026-06-01", team_1, team_2, "1-0")
            for team_1, team_2 in combinations(group_teams, 2)
        )
    predictions_df = pd.DataFrame(
        prediction_rows,
        columns=["match_date", "team_1", "team_2", "predicted_score"],
    )
    results_df = pd.DataFrame(
        [
            {
                "match_date": "2026-06-01",
                "tournament_code": "WC",
                "team_1_code": "AAA",
                "team_2_code": "BBB",
                "team_1_goals": 2,
                "team_2_goals": 1,
            },
            {
                "match_date": "2026-06-28",
                "tournament_code": "WC",
                "team_1_code": "AAA",
                "team_2_code": "EEE",
                "team_1_goals": 1,
                "team_2_goals": 0,
            },
        ]
    )
    latest_results_path = tmp_path / "latest_results.csv"
    teams_lookup_path = tmp_path / "teams_lookup.csv"
    results_df.to_csv(latest_results_path, index=False)
    teams_df.to_csv(teams_lookup_path, index=False)
    completed_df = load_completed_group_results(
        groups_df,
        latest_results_path=latest_results_path,
        teams_lookup_path=teams_lookup_path,
    )
    monkeypatch.setattr(
        standings_module,
        "load_completed_group_results",
        lambda groups: completed_df,
    )

    group_matches_df = build_group_match_results(predictions_df, groups_df)

    assert len(group_matches_df) == 12
    assert len(group_matches_df[group_matches_df["result_source"] == "actual"]) == 1
    assert not (
        (group_matches_df["team_1"] == "A")
        & (group_matches_df["team_2"] == "E")
    ).any()
