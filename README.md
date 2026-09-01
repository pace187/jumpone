# JumpOne

JumpOne is a 2D platformer game developed as part of a bachelor thesis. The game is built with Phaser 3 and TypeScript using the Phaser Editor workflow. 
Website: https://bachelor.openpace.org/

## Bachelor Thesis

This project serves as the practical component of a bachelor thesis investigating **real-time level completion prediction based on in-game telemetry data**. The game continuously collects movement and gameplay data and uses a trained XGBoost model to predict — in real-time — whether a player will successfully finish the level.

The model runs fully **client-side in the browser** with no backend server required for inference.

---

## ML Pipeline

The ML pipeline lives in the `ml_pipeline/` directory and consists of the following scripts:

| Script | Purpose |
|--------|---------|
| `data_parser.py` | Parses the Supabase `.sql` export into a pandas DataFrame |
| `train_xgboost.py` | Trains Logistic Regression, Decision Tree, and XGBoost; exports the best model to `src/scenes/WinPredictor.ts` |
| `gaussian_check.py` | Per-feature normality tests (D'Agostino K²) with distribution plots |
| `overall_skill_distribution.py` | PCA-based overall skill score distribution analysis |
| `visualize_results.py` | Generates all publication-quality plots (model comparison, ROC, feature importance, confusion matrix, win probability over time, Gaussian fits) |
| `evaluate_model.py` | Reports row-wise **and** session-wise (leave-one-session-out) metrics without exporting anything — the safe way to compare configurations |
| `compare_datasets.py` | Compares two SQL exports: scope, session overlap, feature drift, and how a model trained on the older export scores on the sessions only present in the newer one |

The `session_overview.py` tool in the root directory provides session management utilities (overview, filtering, deletion).

### Model Results

Three classifiers were trained and compared on 25 cleaned sessions (8 finished /
17 abandoned). Sessions are subsampled to at most 500 rows each (`--max-rows 500`),
which leaves 11,025 training rows and gives every session roughly equal weight
instead of letting the longest sessions dominate.

| Model | Accuracy | F1-Score | AUC-ROC |
|-------|----------|----------|---------|
| Logistic Regression | 84.2% | 0.770 | 0.889 |
| Decision Tree | 87.8% | 0.806 | 0.921 |
| **XGBoost** ✅ | **93.0%** | **0.900** | **0.972** |

> **Note on validation.** The table above uses a row-wise 80/20 split, so rows from
> the same session land in both train and test and the model can memorise sessions.
> Those numbers are therefore optimistic; they are reported for comparability.
>
> Under a **session-wise** split (leave-one-session-out — each session held out
> entirely) XGBoost reaches a session-level **AUC of 0.824** and classifies **19 of
> 25** sessions correctly, against a majority-class baseline of 17/25. That is the
> figure that describes performance on an *unseen player*. (Varying the subsampling
> seed moves the AUC between 0.824 and 0.838 while 19/25 stays constant.) Reproduce
> both with:
>
> ```bash
> python3 evaluate_model.py --max-rows 500
> ```

XGBoost is exported as JavaScript via `m2cgen` and embedded directly into the game as `WinPredictor.ts`.

### Top Predictive Features (XGBoost Gain)

| Feature | Importance | Interpretation |
|---------|-----------|---------------|
| `pos_y` | 39.9% | Proxy for level progress |
| `distancePerJump` | 12.6% | Skill indicator |
| `jumpSuccessRate` | 10.5% | Skill indicator |
| `maxFallDistance` | 10.0% | Skill indicator |
| `jumpsFailed` | 8.2% | Skill indicator |
| `totalFalls` | 8.0% | |
| `totalJumpsAttempted` | 7.9% | |
| `pos_x` | 2.9% | |

`velocity_magnitude` is part of the feature vector but was never selected as a split
by the trained model.

### Excluded Feature: `avgTimeBetweenJumps`

This feature was dropped from the model even though it originally ranked highest
by gain (30.4%). It is computed in `Level.applyJump()` as `jumpStartTime - landTime`,
which also counts wall-clock time the scene spent **paused** — one recorded pause
inflated it from 1083 ms to 22992 ms. Because sessions in which the player paused
were mostly abandoned, the model learned "player paused" as a proxy for "player
will quit": above a threshold of 1941 ms, 21 of 23 trees routed to a constant
negative leaf and ignored level progress entirely, pinning the in-game prediction
at ~12% even directly in front of the finish.

The column is still collected and stored in the telemetry table — it is simply not
trained on. Making it usable would require excluding paused time at collection
and re-recording the dataset.

### Running the Pipeline

Ensure Python is installed, then from the project root:

```bash
cd ml_pipeline
pip install -r requirements.txt

# Train all models and export XGBoost to WinPredictor.ts.
# --max-rows 500 is the configuration the shipped model uses:
python3 train_xgboost.py --max-rows 500

# Report row-wise and session-wise metrics without touching WinPredictor.ts:
python3 evaluate_model.py --max-rows 500

# Feature distribution normality check:
python3 gaussian_check.py

# PCA-based overall skill score analysis:
python3 overall_skill_distribution.py

# Generate all publication plots → ml_pipeline/plots/.
# Pass the same --max-rows as the training run, otherwise the figures
# describe a different model than the one shipped in the game:
python3 visualize_results.py --max-rows 500
```

### Working With Several Exports

Every script defaults to `../telemetry_rows.sql` but takes `--sql PATH`, so a new
export can be used without renaming files (`session_overview.py` takes the same
flag, relative to the project root):

```bash
python3 train_xgboost.py --sql ../telemetry_rows_01092026.sql --max-rows 500
python3 visualize_results.py --sql ../telemetry_rows_01092026.sql
```

The default lives in one place — `DEFAULT_SQL` in `data_parser.py`.

To compare two exports against each other:

```bash
python3 compare_datasets.py ../telemetry_rows.sql ../telemetry_rows_01092026.sql
```

Note that `train_xgboost.py` always overwrites `src/scenes/WinPredictor.ts`, so
running it against an experimental export replaces the model shipped in the game.
Re-run it without `--sql` to restore the model built from the reference dataset.

### Data Management

Raw telemetry is exported from Supabase as a PostgreSQL `.sql` file (`telemetry_rows.sql` in the project root, not tracked by git).

**The current dataset.** `telemetry_rows.sql` holds 25 sessions (92,869 rows),
derived from the raw export of 2026-09-01 (31 sessions) by two deliberate removals:

| Removed | Why |
|---|---|
| 5 sessions with < 100 rows (35–89 rows) | The player never left the spawn point — no gameplay to learn from. Removed with `--clean 100`. |
| `1774209321205-sgs17rrl7` (42,341 rows) | A single abandoned session accounting for 31% of the entire export. Its data is valid, but leaving it in would let one losing run dominate the model. |

Two large abandoned sessions from April (`1776803425316-eqi1koup9`,
`1776681488292-gnbskm3md`) were re-admitted after being absent from the earlier
19-session dataset; no defect was found in their data.

Use `session_overview.py` to inspect and clean sessions before training:

```bash
# Show all sessions with entry count and last known state:
python3 session_overview.py

# Remove specific sessions by ID (creates automatic backup):
python3 session_overview.py --delete <session_id_1> <session_id_2>

# Remove all sessions with fewer than N entries:
python3 session_overview.py --clean 100

# Dry-run (preview without modifying):
python3 session_overview.py --delete <id> --dry-run
```

---

## Game Commands

[Node.js](https://nodejs.org) is required.

| Command | Description |
|---------|-------------|
| `npm install` | Install project dependencies |
| `npm start` | Launch development web server |
| `npm run build` | Create production build in `dist/` |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Game Framework | [Phaser 3](https://phaser.io) |
| Language | TypeScript |
| Bundler | Vite |
| Editor | [Phaser Editor v4](https://phaser.io/editor) |
| Telemetry DB | Supabase (PostgreSQL) |
| ML | Python · XGBoost · scikit-learn · m2cgen |
| Visualization | matplotlib · seaborn · scipy |

---

## Credits

- **Icons/Graphics:** [Kenney](https://kenney.nl/)
