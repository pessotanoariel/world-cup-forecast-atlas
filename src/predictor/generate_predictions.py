from pathlib import Path

import pandas as pd

from src.predictor.score_model import (
    predict_score,
    simulate_score
)

from src.predictor.expected_goals import (
    estimate_expected_goals
)
from src.predictor.calibration import (
    FORM_WEIGHT,
    PROBABILITY_SHRINK_FACTOR,
)

INPUT_PATH = Path("data/processed/upcoming_matches.csv")

OUTPUT_PATH = Path("data/output/predictions.csv")


def generate_predictions(df: pd.DataFrame, simulation_mode=False) -> pd.DataFrame:

    predictions = []

    for _, row in df.iterrows():

        draw_prob = row["draw_probability"]

        base_home_prob = row["team_1_win_expectancy"]

        form_adjustment = (
            row["form_score_difference"] * FORM_WEIGHT
        )

        home_prob = (
            base_home_prob + form_adjustment
        )

        # keep probabilities valid
        home_prob = min(
            max(home_prob, 0),
            1 - draw_prob
        )

        # probability calibration
        home_prob = 0.5 + (
            (home_prob - 0.5) * PROBABILITY_SHRINK_FACTOR
        )

        home_prob = min(
            max(home_prob, 0),
            1 - draw_prob
        )

        away_prob = 1 - home_prob - draw_prob

        if home_prob >= 0.60:
            predicted_winner = row["team_1_name"]
            confidence = "High"

        elif home_prob >= 0.45:
            predicted_winner = row["team_1_name"]
            confidence = "Medium"

        elif away_prob >= 0.45:
            predicted_winner = row["team_2_name"]
            confidence = "Medium"

        else:
            predicted_winner = "Draw"
            confidence = "Low"

        probability_gap = abs(
            home_prob - away_prob
        )

        if probability_gap <= 0.05:
            upset_risk = "EXTREME"

        elif probability_gap <= 0.12:
            upset_risk = "HIGH"

        elif probability_gap <= 0.20:
            upset_risk = "MEDIUM"

        else:
            upset_risk = "LOW"

        home_xg, away_xg = (
            estimate_expected_goals(
                home_prob,
                away_prob
            )
        )

        if simulation_mode:

            print("SIMULATION MODE ACTIVE")

            home_goals, away_goals = (
                simulate_score(
                    home_xg,
                    away_xg
                )
            )

            predicted_score = (
                f"{home_goals}-{away_goals}"
            )

            if home_goals > away_goals:

                predicted_winner = (
                    row["team_1_name"]
                )

            elif away_goals > home_goals:

                predicted_winner = (
                    row["team_2_name"]
                )

            else:

                predicted_winner = "Draw"

        else:

            predicted_score = predict_score(
                home_xg,
                away_xg,
                predicted_winner,
                row["team_1_name"],
                row["team_2_name"]
            )

        predictions.append({
            "match_date": row["match_date"],
            "team_1": row["team_1_name"],
            "team_2": row["team_2_name"],
            "team_1_win_probability": round(home_prob, 3),
            "draw_probability": round(draw_prob, 3),
            "team_2_win_probability": round(away_prob, 3),
            "predicted_winner": predicted_winner,
            "predicted_score": predicted_score,
            "confidence": confidence,
            "upset_risk": upset_risk
        })

    return pd.DataFrame(predictions)


def main() -> None:

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    matches_df = pd.read_csv(INPUT_PATH)

    predictions_df = generate_predictions(matches_df)

    predictions_df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8"
    )

    print(f"\nOK - Predictions saved to {OUTPUT_PATH}\n")

    print(predictions_df.head(20))


if __name__ == "__main__":
    main()
