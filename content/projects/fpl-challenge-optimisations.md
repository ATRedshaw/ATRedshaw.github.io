# FPL Challenge Optimisation Engine

Fantasy football is usually a game about gut feeling and weekly panic transfers. FPL Challenge is different. It runs as a standalone format alongside the main game, resetting completely each gameweek with a fresh squad, a fresh budget and a different scoring twist each time. One week, under-23 players score double points. The next, goalkeepers earn bonus points for every save they make. The challenge changes constantly, and that turns a casual pastime into a genuinely interesting optimisation problem.

This project is my attempt to solve that problem properly.

## The Idea

The core question is straightforward: given this week's specific scoring rules and a set of point projections for every player, what is the mathematically optimal squad to pick?

The interesting engineering challenge is that "this week's specific scoring rules" is never the same twice. A naïve approach of hard-coding each rule set would quickly become unmanageable. So the project is built around a pipeline that separates concerns cleanly: fetch projections, adjust them for this week's rules, then solve an integer linear programme to find the best squad.

Once results are in, a hindsight pass re-runs the same optimisation using actual points rather than predicted ones, which lets you see exactly how close the pre-gameweek prediction came to the theoretical best possible selection.

## Project Structure (2025-26 onwards)

The 2025-26 season was a full rewrite of earlier exploratory Jupyter notebook work. The structure below is now the canonical layout and will be replicated for every future season.

```
2025-26/
├── gw{n}.py                  # Per-gameweek runner scripts
├── hindsight.py              # Hindsight pass across all completed GWs
├── data/
│   ├── config.yaml           # Season-level config (team ID, JS bundle URL)
│   ├── constraints.yaml      # Per-GW solver constraints
│   ├── projections/          # Saved xPts CSVs, one per gameweek
│   ├── lineups/
│   │   ├── predicted_optimal.json
│   │   ├── actual_optimal.json
│   │   └── actual_outcome.json
│   └── descriptions/
│       └── challenges.json
└── utils/
    ├── solver.py             # FPLChallengeOptimiser (ILP via PuLP)
    ├── projections.py        # xPts fetch and DataFrame construction
    ├── data.py               # JSON persistence and site mirroring
    ├── decisions.py          # Interactive ban/force with fuzzy matching
    ├── challenges.py         # Challenge metadata scraping
    └── rules/
        └── gw{n}.py          # Per-GW projection adjustment logic
```

Each gameweek has its own runner script (`gw1.py`, `gw2.py` and so on) that orchestrates the full pipeline: load constraints from YAML, fetch and adjust projections, handle any interactive player bans or forces, then solve and save. The per-gameweek scripts are intentionally thin. All the real logic lives in `utils/`.

### Projections

Player point projections come from a private ML model (although I have aspirations of releasing this for wider consumption in the future). The raw output lands in `data/projections/` as a CSV, so the data can still be used even if the projections can no longer be made (such as when the gameweek deadline has passed). Each row carries a player's base expected points (`Predicted_Points`), expected minutes (`xMins`), price, position and team. These fields feed everything downstream.

### Challenge Rule Adjustments

The `utils/rules/` directory is where the interesting work happens. Each gameweek has its own rule module that transforms the raw projections to reflect the week's specific challenge scoring.

Some challenges are simple multipliers. If under-23 players score double, the rule module fetches birth dates from the FPL Challenge bootstrap API, flags the relevant players and doubles their `Predicted_Points`. Done in a dozen lines.

Others are more involved. For challenges that award bonus points for repeatable in-game actions (clean sheets, goal attempts, chances created), per-90 rates are estimated from season-to-date stats and scaled by `xMins`:

```
estimated_events = (events_per_90 / 90) * xMins
extra_points     = estimated_events * points_per_event
```

For threshold-based challenges, a Poisson model turns the expected event count into a probability of hitting the threshold, which gets multiplied out into expected bonus points. This avoids the bluntness of a hard binary decision and assigns partial expected credit continuously across the player pool.

For challenges where bonus points depend on a team winning, win probabilities are distributed across a team's players weighted by their expected goal contribution, meaning the solver is working with a realistic expected value rather than an overconfident all-or-nothing assignment.

### The Solver

Once the projections are adjusted, `FPLChallengeOptimiser` sets up and solves an integer linear programme via PuLP. The objective is to maximise total predicted points including the captain's doubled contribution:

```
maximise  Σ(lineup[i] × pts[i]) + Σ(captain[i] × pts[i])
```

Constraints are loaded directly from `data/constraints.yaml`, which stores the rules for every gameweek upfront. This means the total squad size, position minimums and maximums, captain count and maximum players per club are all defined in config rather than code. Changing a constraint for a specific gameweek is a one-line YAML edit. The solver itself never needs to change.

An interactive ban and force mechanism lets you exclude specific players or guarantee their inclusion before solving, resolved via fuzzy name matching so you do not need to type names perfectly.

### Hindsight

After each gameweek is confirmed, `hindsight.py` runs the same optimisation pipeline but replaces projected points with actual points pulled from the live FPL Challenge API. The result is the true with-hindsight optimal squad, the theoretically best possible selection given perfect information. Comparing this against the pre-gameweek prediction gives an honest measure of model quality.

The hindsight script skips gameweeks that have already been processed, so it can be run freely after any gameweek without duplicating results.

## The Frontend

All results are surfaced through a static HTML frontend at `site/index.html`. There is no build step and no framework dependency. It loads two JSON files from `site/data/{season}/`: one for predicted optimal and one for actual optimal, then renders both side-by-side for each gameweek.

![A screenshot of the modal for a specific challenge](/assets/images/projects/fpl-challenge-optimisations/challenge-example-modal.png)

_Figure: The post-gameweek modal for Challenge 17, illustrating the performance gap between the initial 85.8 xPts projection and the 189.0 hindsight optimal. The UI highlights the "Match Rate" (50%) and uses green ticks to identify where the solver successfully aligned with the perfect lineup._

The UI is dark-themed and minimal. Each gameweek shows the challenge title and description (scraped from the FPL Challenge JS bundle via a targeted regex and stored in `challenges.json`), the predicted optimal squad, the hindsight optimal squad and a score breakdown. Players who appear in both lineups are visually distinguished from those that differ, making it immediately obvious where the model got it right and where it did not.

A chart tracking predicted versus actual total points across all completed gameweeks gives a quick season-level view of how the model has held up over time.

![Overall challenge stats bar at the top of the page, including overall rank, rank %, total gameweeks, etc.](/assets/images/projects/fpl-challenge-optimisations/challenge-rank-progression.png)

_Figure: The graph showing the progression of the model's rank over the course of the season._

![Overall challenge stats bar at the top of the page, including overall rank, rank %, total gameweeks, etc.](/assets/images/projects/fpl-challenge-optimisations/challenge-stats.png)
_Figure: The overall challenge stats bar indicating the overall season rank of the model can be found at the top of the page._

The site data is mirrored automatically from the season data directory (`2025-26/data/lineups/`) every time the solver or hindsight scripts are run, so the frontend always reflects the latest state without any manual copying.

## Stack

| Layer | Tool |
|---|---|
| Machine Learning Projections | Scikit-learn |
| Optimisation | PuLP (CBC solver) |
| Data manipulation | pandas, NumPy |
| Statistical modelling | SciPy |
| API access | requests |
| Name matching | RapidFuzz |
| Config | PyYAML |
| Frontend | Vanilla HTML, Tailwind CSS, Chart.js |

## What I Learned

The most useful part of building this was being forced to think clearly about uncertainty. It is tempting to just pick the player most likely to hit a bonus threshold and assign them full credit. But that overfits a single outcome. Distributing expected value continuously across players, using Poisson probabilities or win-weighted distributions, consistently produces better expected-value squads even if it occasionally loses to a simpler pick that happened to land.

The YAML-driven constraint system turned out to be one of the better design decisions. Early versions of the project had constraints embedded directly in the solver code, which meant touching core logic every single gameweek. Moving them to config eliminated that entirely.

The hindsight comparison is genuinely the most valuable output of the whole project. Seeing exactly which players the model missed, and by how much, is what drives improvements to the rule modules between gameweeks.