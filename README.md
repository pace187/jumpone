# JumpOne

JumpOne is a 2D platformer game developed as part of a bachelor thesis. The game is built with Phaser 3 and TypeScript using the Phaser Editor workflow.

## Bachelor Thesis

This project serves as the practical component of a bachelor thesis investigating **player churn prediction based on movement telemetry data**. The game collects in-game movement data (e.g., player positions, jump patterns, directional changes) and uses this telemetry to analyze and predict whether a player is likely to stop playing (churn). The goal is to identify behavioral patterns in player movement that correlate with disengagement, enabling early intervention strategies to improve player retention.

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

To start the local development server use `npm run dev`.

## Deploying to Production

To create a production build use the command `npm run build`.

This will take your game code and build it into a single bundle, ready for deployment. This bundle is saved to the `dist` folder. Upload all contents of the `dist` folder to a public-facing web server.

## Tech Stack

- **Game Framework:** [Phaser 3](https://phaser.io)
- **Language:** TypeScript
- **Bundler:** Vite
- **Editor:** [Phaser Editor v4](https://phaser.io/editor)
