# World Cup Forecast Atlas

Interactive simulation and forecasting platform for the FIFA World Cup 2026.

Built with Python, Elo Ratings, Monte Carlo simulation, goal-expectation estimates derived from match probabilities, Poisson score modeling, and Streamlit.

---

## Live Demo

<https://world-cup-forecast-atlas.streamlit.app/>

---

## Atlas Experience

The project includes an editorial-style interactive Atlas that transforms simulation outputs into a digital tournament magazine.

### Included Sections

- Cover
- Atlas
- Groups
- Bracket
- Matches
- Method

Instead of presenting predictions as traditional dashboards, the Atlas organizes forecasts, standings, probabilities, and knockout projections into a narrative experience inspired by classic World Cup guides.

---

## Project Goals

- Consume and process international football datasets based on Elo Ratings.
- Generate match forecasts using team strength and recent form.
- Simulate the complete FIFA World Cup 2026.
- Determine qualification using the official 48-team format.
- Implement FIFA Annex C knockout mapping.
- Simulate all knockout rounds through the Final.
- Explore tournament outcomes through Monte Carlo simulation.
- Serve as a practical project for Python, data engineering, simulation modeling, testing, and product design.

---

## Key Features

### Simulation Engine

- Elo Ratings
- Recent Form
- Host Advantage
- Goal-expectation estimates derived from match probabilities
- Poisson Distribution
- Monte Carlo Simulation
- Dynamic Elo Updates
- FIFA Tiebreakers

### Tournament Simulation

- Full group-stage simulation
- Group standings generation
- Best third-place qualification
- Official FIFA 2026 tournament format
- FIFA Annex C implementation
- Complete knockout simulation
- Extra-time and penalty resolution
- Tournament champion prediction
- FIFA group-stage football criteria through head-to-head goals scored
- Simulator-specific deterministic Elo fallback for unresolved ties after modeled FIFA criteria

### Monte Carlo Analytics

- Stochastic score generation
- Tournament reruns
- Champion probabilities
- Most likely finals
- Team progression probabilities

### Editorial Atlas

- Interactive tournament cover
- Championship probability rankings
- Group-stage storytelling
- Third-place qualification race
- Knockout wall chart
- Match forecast archive
- Methodology guide

### Automation & Operations

- End-to-end tournament pipeline
- Automated data ingestion
- Scheduled execution via GitHub Actions with committed refreshed data outputs
- Data freshness validation
- Execution logging and monitoring
- Resilient fallback for external Elo sources

---

## Architecture

### Data Pipeline

```text
External Datasets
        ↓
Ingestion
        ↓
Processing
        ↓
Team Strength + Recent Form
        ↓
Match Forecasts
        ↓
Group Simulation
        ↓
Qualification
        ↓
FIFA Annex C
        ↓
Knockout Simulation
        ↓
Monte Carlo Analysis
        ↓
Atlas Experience
```

---

## Project Structure

```text
prode-mundial-2026/
│
├── app/
│   ├── atlas_app/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── data.py
│   │   ├── formatting.py
│   │   └── styles.py
│   │
│   ├── legacy_dashboard.py
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
│
├── docs/
│   ├── annex_c.md
│   └── knockout_pipeline.md
│
├── src/
│   ├── analysis/
│   ├── ingestion/
│   ├── knockout/
│   ├── predictor/
│   ├── processing/
│   └── simulation/
│
├── tests/
│
├── README.md
├── README_EN.md
└── requirements.txt
```

---

## Running the Atlas

Launch the Streamlit application:

```bash
streamlit run app/streamlit_app.py
```

---

## Running Tournament Simulation

Execute the complete tournament pipeline:

```bash
python -m src.knockout.tournament
```

---

## Installation

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Testing

Run all tests:

```bash
pytest
```

Current coverage includes more than 60 automated tests covering:

- FIFA tiebreakers
- FIFA Annex C
- Group-stage simulation
- Knockout simulation
- Monte Carlo execution
- Elo updates
- Data ingestion
- External source resilience
- Output validation

---

## Documentation

Additional technical documentation:

- `docs/annex_c.md`
- `docs/knockout_pipeline.md`

---

## Technical Summary

- 48 national teams
- 104 tournament matches
- Official FIFA 2026 format
- FIFA Annex C implementation (495 combinations)
- Monte Carlo simulation engine
- Dynamic Elo updates
- Editorial Atlas experience
- GitHub Actions automation
- 60+ automated tests

---

## Screenshots

### Cover Page

`docs/screenshots/cover.png`

### Atlas Page

`docs/screenshots/atlas.png`

### Groups Page

`docs/screenshots/groups.png`

### Bracket Page

`docs/screenshots/bracket.png`

### Method Page

`docs/screenshots/method.png`

---

## Project Status

Version: v1.0

Completed:

- Full FIFA World Cup 2026 simulation
- Official 48-team format
- FIFA Annex C implementation
- Monte Carlo tournament engine
- Editorial Atlas experience
- GitHub Actions automation
- FIFA group-stage tiebreakers through modeled football criteria

Possible future evolutions:

- Interactive bracket
- Historical World Cup mode
- Team comparison tools
- Dedicated Next.js frontend
- Public simulation API

---

## Disclaimer

This project is intended for educational, analytical, and entertainment purposes.

Forecasts are generated through simulation models and probabilistic methods. They do not constitute betting advice and should not be interpreted as predictions of actual future results.
