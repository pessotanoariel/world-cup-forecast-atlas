import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_PATH))

import pandas as pd
import streamlit as st

import plotly.express as px

from config.translations import (
    TEAM_TRANSLATIONS
)


PREDICTIONS_PATH = Path(
    "data/output/predictions.csv"
)

GROUPS_PATH = Path(
    "data/raw/world_cup_groups.csv"
)

@st.cache_data
def load_predictions():

    df = pd.read_csv(PREDICTIONS_PATH)

    return df


df = load_predictions()

groups_df = pd.read_csv(GROUPS_PATH)

champions_df = pd.read_csv(
    "data/output/champion_probabilities.csv"
)

finals_df = pd.read_csv(
    "data/output/most_likely_finals.csv"
)

round_of_32_df = pd.read_csv(
    "data/output/round_of_32_predictions.csv"
)

round_of_16_df = pd.read_csv(
    "data/output/round_of_16_predictions.csv"
)

quarterfinals_df = pd.read_csv(
    "data/output/quarterfinals_predictions.csv"
)

semifinals_df = pd.read_csv(
    "data/output/semifinals_predictions.csv"
)

third_place_df = pd.read_csv(
    "data/output/third_place_predictions.csv"
)

final_df = pd.read_csv(
    "data/output/final_predictions.csv"
)

standings_df = pd.read_csv(
    "data/output/group_standings.csv"
)

qualified_df = pd.read_csv(
    "data/output/qualified_teams.csv"
)

group_mapping = (
    groups_df
    .groupby("group")["country"]
    .apply(list)
    .to_dict()
)

total_matches = len(df)

total_bardos = (
    df["upset_risk"] == "EXTREME"
).sum()

most_unbalanced_match = (
    df.sort_values(
        by="team_1_win_probability",
        ascending=False
    )
    .iloc[0]
)

most_unbalanced_team_1 = TEAM_TRANSLATIONS.get(
    most_unbalanced_match["team_1"],
    most_unbalanced_match["team_1"]
)

most_unbalanced_team_2 = TEAM_TRANSLATIONS.get(
    most_unbalanced_match["team_2"],
    most_unbalanced_match["team_2"]
)

most_unbalanced_label = (
    f"{most_unbalanced_team_1} vs {most_unbalanced_team_2}"
)

st.title(
    "🏆 World Cup 2026 Forecast Engine"
)

st.subheader(
    "Powered by Elo Ratings, goal-expectation estimates & Monte Carlo Simulation"
)

forecast_col, finals_col, chart_col = st.columns(3)

with forecast_col:

    st.subheader(
        "🏆 Favoritos al Título"
    )

    top_3 = champions_df.head(3)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🥇 Favorito",
        TEAM_TRANSLATIONS.get(
            top_3.iloc[0]["team"],
            top_3.iloc[0]["team"]
        ),
        f"{top_3.iloc[0]['probability']:.0%}"
    )

    col2.metric(
        "🥈 Segundo",
        TEAM_TRANSLATIONS.get(
            top_3.iloc[1]["team"],
            top_3.iloc[1]["team"]
        ),
        f"{top_3.iloc[1]['probability']:.0%}"
    )

    col3.metric(
        "🥉 Tercero",
        TEAM_TRANSLATIONS.get(
            top_3.iloc[2]["team"],
            top_3.iloc[2]["team"]
        ),
        f"{top_3.iloc[2]['probability']:.0%}"
    )

with finals_col:

    st.subheader(
        "🎯 Finales Más Probables"
    )

    top_finals = finals_df.head(5)

    for _, row in top_finals.iterrows():

        team_1 = TEAM_TRANSLATIONS.get(
            row["team_1"],
            row["team_1"]
        )

        team_2 = TEAM_TRANSLATIONS.get(
            row["team_2"],
            row["team_2"]
        )

        st.markdown(
            f"- **{team_1} vs {team_2}** ({row['probability']:.0%})"
        )

with chart_col:

    st.subheader(
        "📊 Probabilidad de Campeón"
    )

    chart_df = (
        champions_df
        .head(5)
        .copy()
    )

    chart_df["team"] = (
        chart_df["team"]
        .replace(TEAM_TRANSLATIONS)
    )

    chart_df["probability"] = (
        chart_df["probability"] * 100
    )

    chart_df = chart_df.sort_values(
        "probability"
    )

    fig = px.bar(
        chart_df,
        x="probability",
        y="team",
        orientation="h",
        labels={
            "probability": "%",
            "team": ""
        }
    )

    fig.update_layout(
        height=250,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

display_df = df[
    [
        "match_date",
        "team_1",
        "team_2",
        "predicted_winner",
        "predicted_score",
        "confidence",
        "upset_risk"
    ]
].copy()

st.header(
    "🌎 Fase de Grupos Simulada"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Partidos simulados",
    total_matches
)

col2.metric(
    "Posibles batacazos",
    total_bardos
)

col3.metric(
    "Partido más desparejo",
    most_unbalanced_label
)

selected_group = st.radio(
    "Grupos",
    ["Todos"] + sorted(group_mapping.keys()),
    horizontal=True
)


filter_col1, filter_col2, filter_col3, filter_col5 = st.columns(4)

with filter_col1:

    confidence_filter = st.selectbox(
        "Confianza",
        ["Todas", "Alta", "Media", "Baja"]
    )

with filter_col2:

    risk_filter = st.selectbox(
        "Batacazo",
        ["Todos", "Bajo", "Medio", "Alto", "Bardo"]
    )

display_df.columns = [
    "Fecha",
    "Equipo 1",
    "Equipo 2",
    "Ganador",
    "Resultado Estimado",
    "Confianza",
    "Riesgo Batacazo"
]

dates = sorted(
    display_df["Fecha"].unique()
)

formatted_dates = pd.to_datetime(
    dates
).strftime("%d %b")

display_df["Equipo 1"] = (
    display_df["Equipo 1"]
    .replace(TEAM_TRANSLATIONS)
)

display_df["Equipo 2"] = (
    display_df["Equipo 2"]
    .replace(TEAM_TRANSLATIONS)
)

display_df["Ganador"] = (
    display_df["Ganador"]
    .replace(TEAM_TRANSLATIONS)
)

teams = sorted(
    list(
        set(display_df["Equipo 1"])
        | set(display_df["Equipo 2"])
    )
)

display_df["Fecha"] = pd.to_datetime(
    display_df["Fecha"]
).dt.strftime("%d %b")


with filter_col3:

    date_filter = st.selectbox(
        "Fecha",
        ["Todas"] + list(formatted_dates)
    )

with filter_col5:

    team_filter = st.selectbox(
        "Selección",
        ["Todas"] + teams
    )

display_df["Confianza"] = (
    display_df["Confianza"]
    .replace({
        "High": "Alta",
        "Medium": "Media",
        "Low": "Baja"
    })
)

display_df["Riesgo Batacazo"] = (
    display_df["Riesgo Batacazo"]
    .replace({
        "LOW": "Bajo",
        "MEDIUM": "Medio",
        "HIGH": "Alto",
        "EXTREME": "Bardo"
    })
)

display_df["Ganador"] = (
    display_df["Ganador"]
    .replace({
        "Draw": "Empate"
    })
)

if confidence_filter != "Todas":

    display_df = display_df[
        display_df["Confianza"] == confidence_filter
    ]


if risk_filter != "Todos":

    display_df = display_df[
        display_df["Riesgo Batacazo"] == risk_filter
    ]

if team_filter != "Todas":

    display_df = display_df[
        (
            display_df["Equipo 1"] == team_filter
        )
        |
        (
            display_df["Equipo 2"] == team_filter
        )
    ]

if date_filter != "Todas":

    display_df = display_df[
        display_df["Fecha"] == date_filter
    ]

if selected_group != "Todos":

    selected_teams = group_mapping[selected_group]

    selected_teams = [
        TEAM_TRANSLATIONS.get(
            team,
            team
        )
        for team in selected_teams
   ]

    display_df = display_df[
        (
            display_df["Equipo 1"]
            .isin(selected_teams)
        )
        &
        (
            display_df["Equipo 2"]
            .isin(selected_teams)
        )
    ]

display_df = display_df.reset_index(
    drop=True
)

styled_df = (
    display_df.style
    .map(
        lambda x:
            "color: #00C853; font-weight: bold"
            if x == "Alta"
            else (
                "color: #FFD600; font-weight: bold"
                if x == "Media"
                else (
                    "color: #FF5252; font-weight: bold"
                    if x == "Baja"
                    else ""
                )
            ),
        subset=["Confianza"]
    )
    .map(
        lambda x:
            "color: #00C853; font-weight: bold"
            if x == "Bajo"
            else (
                "color: #FFD600; font-weight: bold"
                if x == "Medio"
                else (
                    "color: #FF9100; font-weight: bold"
                    if x == "Alto"
                    else (
                        "color: #FF1744; font-weight: bold"
                        if x == "Bardo"
                        else ""
                    )
                )
            ),
        subset=["Riesgo Batacazo"]
    )
)

left_col, right_col = st.columns(2)

for index, row in display_df.iterrows():

    target_col = (
        left_col
        if index % 2 == 0
        else right_col
    )

    with target_col:

        st.markdown(
            f"""
### {row['Equipo 1']} vs {row['Equipo 2']}

**Ganador:** {row['Ganador']}

**Resultado:** {row['Resultado Estimado']}

**Confianza:** {row['Confianza']}

**Batacazo:** {row['Riesgo Batacazo']}

---
"""
        )


st.divider()

st.header(
    "📊 Posiciones de Grupos"
)

if selected_group != "Todos":

    standings_display = (
        standings_df[
            standings_df["group"]
            == selected_group
        ]
    )

else:

    standings_display = standings_df.copy()

standings_display = standings_display[
    [
        "group",
        "position",
        "team",
        "PJ",
        "PG",
        "PE",
        "PP",
        "GF",
        "GC",
        "DG",
        "PTS"
    ]
]

standings_display["team"] = (
    standings_display["team"]
    .replace(TEAM_TRANSLATIONS)
)

standings_display.columns = [
    "Grupo",
    "Pos",
    "Selección",
    "PJ",
    "PG",
    "PE",
    "PP",
    "GF",
    "GC",
    "DG",
    "PTS"
]

st.dataframe(
    standings_display,
    use_container_width=True,
    hide_index=True
)

st.subheader(
    "✅ Clasificados a Dieciseisavos"
)

qualified_display = qualified_df.copy()

if selected_group != "Todos":

    qualified_display = qualified_display[
        qualified_display["group"]
        == selected_group
    ]

qualified_display["team"] = (
    qualified_display["team"]
    .replace(TEAM_TRANSLATIONS)
)

qualified_display = qualified_display[
    [
        "group",
        "position",
        "team",
        "PTS"
    ]
]

qualified_display.columns = [
    "Grupo",
    "Posición",
    "Selección",
    "PTS"
]

st.dataframe(
    qualified_display,
    use_container_width=True,
    hide_index=True
)

st.divider()

third_places_display = standings_df[
    standings_df["position"] == 3
].copy()

third_places_display = (
    third_places_display
    .sort_values(
        by=[
            "PTS",
            "DG",
            "GF"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )
)

third_places_display["team"] = (
    third_places_display["team"]
    .replace(TEAM_TRANSLATIONS)
)

third_places_display = (
    third_places_display[
        [
            "group",
            "team",
            "PTS",
            "DG",
            "GF"
        ]
    ]
)

third_places_display.columns = [
    "Grupo",
    "Selección",
    "PTS",
    "DG",
    "GF"
]

st.subheader(
    "🥉 Ranking de Mejores Terceros"
)

top_thirds = third_places_display.copy()

top_thirds["Clasifica"] = [
    "✅" if i < 8 else "❌"
    for i in range(len(top_thirds))
]

st.dataframe(
    top_thirds,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.header(
    "🏆 Camino al Título"
)

col_r32, col_r16, col_qf, col_sf, col_f = st.columns(5)

with col_r32:

    st.subheader("Dieciseisavos")

    for _, row in round_of_32_df.iterrows():

        team_1 = TEAM_TRANSLATIONS.get(
            row["team_1"],
            row["team_1"]
        )

        team_2 = TEAM_TRANSLATIONS.get(
            row["team_2"],
            row["team_2"]
        )

        winner = TEAM_TRANSLATIONS.get(
            row["predicted_winner"],
            row["predicted_winner"]
        )

        st.markdown(
            f"**{team_1} vs {team_2}**"
        )

        st.caption(
            f"🏆 {winner}"
        )

        st.caption(
            f"⚽ {row['predicted_score']}"
        )

        st.markdown("---")

with col_r16:

    st.subheader("Octavos")

    for _, row in round_of_16_df.iterrows():

        team_1 = TEAM_TRANSLATIONS.get(
            row["team_1"],
            row["team_1"]
        )

        team_2 = TEAM_TRANSLATIONS.get(
            row["team_2"],
            row["team_2"]
        )

        winner = TEAM_TRANSLATIONS.get(
            row["predicted_winner"],
            row["predicted_winner"]
        )

        st.markdown(
            f"**{team_1} vs {team_2}**"
        )

        st.caption(
            f"🏆 {winner}"
        )

        st.caption(
            f"⚽ {row['predicted_score']}"
        )

        st.markdown("---")

with col_qf:

    st.subheader("Cuartos")

    for _, row in quarterfinals_df.iterrows():

        team_1 = TEAM_TRANSLATIONS.get(
            row["team_1"],
            row["team_1"]
        )

        team_2 = TEAM_TRANSLATIONS.get(
            row["team_2"],
            row["team_2"]
        )

        winner = TEAM_TRANSLATIONS.get(
            row["predicted_winner"],
            row["predicted_winner"]
        )

        st.markdown(
            f"**{team_1} vs {team_2}**"
        )

        st.caption(
            f"🏆 {winner}"
        )

        st.caption(
            f"⚽ {row['predicted_score']}"
        )

        st.markdown("---")

with col_sf:

    st.subheader("Semis")

    for _, row in semifinals_df.iterrows():

        team_1 = TEAM_TRANSLATIONS.get(
            row["team_1"],
            row["team_1"]
        )

        team_2 = TEAM_TRANSLATIONS.get(
            row["team_2"],
            row["team_2"]
        )

        winner = TEAM_TRANSLATIONS.get(
            row["predicted_winner"],
            row["predicted_winner"]
        )

        st.markdown(
            f"**{team_1} vs {team_2}**"
        )

        st.caption(
            f"🏆 {winner}"
        )

        st.caption(
            f"⚽ {row['predicted_score']}"
        )

        st.markdown("---")

with col_f:

    st.subheader("Final")

    for _, row in final_df.iterrows():

        team_1 = TEAM_TRANSLATIONS.get(
            row["team_1"],
            row["team_1"]
        )

        team_2 = TEAM_TRANSLATIONS.get(
            row["team_2"],
            row["team_2"]
        )

        winner = TEAM_TRANSLATIONS.get(
            row["predicted_winner"],
            row["predicted_winner"]
        )

        st.markdown(
            f"**{team_1} vs {team_2}**"
        )

        st.caption(
            f"🏆 {winner}"
        )

        st.caption(
            f"⚽ {row['predicted_score']}"
        )

        st.markdown("---")

st.divider()

st.subheader(
    "🥉 Partido por el Tercer Puesto"
)

for _, row in third_place_df.iterrows():

    team_1 = TEAM_TRANSLATIONS.get(
        row["team_1"],
        row["team_1"]
    )

    team_2 = TEAM_TRANSLATIONS.get(
        row["team_2"],
        row["team_2"]
    )

    winner = TEAM_TRANSLATIONS.get(
        row["predicted_winner"],
        row["predicted_winner"]
    )

    st.markdown(
        f"**{team_1} vs {team_2}**"
    )

    st.caption(
        f"🏆 {winner}"
    )

    st.caption(
        f"⚽ {row['predicted_score']}"
    )
