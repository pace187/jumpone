# JumpOne

JumpOne is a 2D platformer game developed as part of a bachelor thesis. The game is built with Phaser 3 and TypeScript using the Phaser Editor workflow.

## Bachelor Thesis

This project serves as the practical component of a bachelor thesis investigating **level completion prediction based on movement telemetry data**. The game collects in-game movement data and uses it to predict whether a player will be able to finish the level, based on their skill level.

The prediction model uses the following telemetry features:

| Feature | Description |
|---------|-------------|
| `jumpSuccessRate` | Ratio of successful to attempted jumps |
| `jumpsFailed` | Number of failed jumps |
| `totalFalls` | Total number of falls |
| `avgFallDistance` | Average distance fallen per fall |
| `maxFallDistance` | Longest single fall |
| `distancePerJump` | Average horizontal distance covered per successful jump |
| `avgTimeBetweenJumps` | Average time the player spends planning before jumping |
| `totalJumpsAttempted` | Total jump attempts |
| `sessionDuration_sec` | Time spent in the session |
| `checkpointsReached` | Number of checkpoints the player has reached |

Based on these features, a Python ML model predicts the likelihood of the player **not being able to finish the level**. The goal is to identify low-skill players early and predict frustration in real-time.

### ML Pipeline (Live Prediction)

The ML pipeline is located in the `ml_pipeline/` directory. It uses an **XGBoost classifier** to evaluate player skill based on session aggregates. The trained model is exported natively to Javascript using `m2cgen` into `src/scenes/WinPredictor.ts`, allowing the Phaser game to evaluate the win probability live in the browser without needing a backend server.

#### Running the ML Pipeline
Ensure you have Python installed, then run the following from the root directory:

```bash
cd ml_pipeline
pip install -r requirements.txt

# To generate feature-by-feature Gaussian distribution validation plots:
python gaussian_check.py

# To generate an overall PCA-based Gaussian distribution plot for the entire dataset:
python overall_skill_distribution.py

# To train the XGBoost model and export the logic natively to the game:
python train_xgboost.py
```

#### Preventing Bias (Subsampling)
If one game session contains much more recorded metrics than the another ones, the machine learning model will become statistically biased towards the playstyle of the longer session. 

To easily prevent overrepresentation, all three Python scripts accept a `--max-rows` argument. This randomly extracts a maximum set limit of rows from each session to equalize them, while perfectly retaining their chronological order.

```bash
# Example: Limit every session to at most 1,000 random data points
python train_xgboost.py --max-rows 1000
python overall_skill_distribution.py --max-rows 1000
```

## Requirements

[Node.js](https://nodejs.org) is required to install dependencies and run scripts via `npm`.

## Available Commands

| Command | Description |
|---------|-------------|
| `npm install`   | Install project dependencies |
| `npm start`     | Launch a development web server |
| `npm run build` | Create a production build in the `dist` folder |

## Development

After cloning the repo, run `npm install` from your project directory.

To start the local development server run `npm start`.

## Deploying to Production

To create a production build use the command `npm run build`.

This will take your game code and build it into a single bundle, ready for deployment. This bundle is saved to the `dist` folder. Upload all contents of the `dist` folder to a public-facing web server.

## Tech Stack

- **Game Framework:** [Phaser 3](https://phaser.io)
- **Language:** TypeScript
- **Bundler:** Vite
- **Editor:** [Phaser Editor v4](https://phaser.io/editor)
- **Backend/DB:** Supabase (telemetry storage)
- **ML:** Python (skill-based level completion prediction)

## Credits

- **Icons/Graphics:** [Kenney](https://kenney.nl/)
