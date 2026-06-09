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

The `session_overview.py` tool in the root directory provides session management utilities (overview, filtering, deletion).

### Model Results

Three classifiers were trained and compared on 53,659 telemetry rows from 19 cleaned sessions (80/20 train/test split):

| Model | Accuracy | F1-Score | AUC-ROC |
|-------|----------|----------|---------|
| Logistic Regression | 86.0% | 0.888 | 0.874 |
| Decision Tree | 92.8% | 0.941 | 0.974 |
| **XGBoost** ✅ | **95.9%** | **0.966** | **0.997** |

XGBoost is exported as JavaScript via `m2cgen` and embedded directly into the game as `WinPredictor.ts`.

### Top Predictive Features (XGBoost Gain)

| Feature | Importance | Interpretation |
|---------|-----------|---------------|
| `avgTimeBetweenJumps` | 30.4% | Engagement/frustration indicator |
| `pos_y` | 21.2% | Proxy for level progress |
| `maxFallDistance` | 12.3% | Skill indicator |
| `jumpSuccessRate` | 12.3% | Skill indicator |
| `totalFalls` | 7.9% | |
| `distancePerJump` | 7.7% | |
| `totalJumpsAttempted` | 4.2% | |
| `jumpsFailed` | 4.1% | |

### Running the Pipeline

Ensure Python is installed, then from the project root:

```bash
cd ml_pipeline
pip install -r requirements.txt

# Train all models and export XGBoost to WinPredictor.ts:
python3 train_xgboost.py

# Optional: limit rows per session to prevent dominant sessions biasing the model:
python3 train_xgboost.py --max-rows 500

# Feature distribution normality check:
python3 gaussian_check.py

# PCA-based overall skill score analysis:
python3 overall_skill_distribution.py

# Generate all publication plots → ml_pipeline/plots/:
python3 visualize_results.py
```

### Data Management

Raw telemetry is exported from Supabase as a PostgreSQL `.sql` file (`telemetry_rows.sql` in the project root, not tracked by git).

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
