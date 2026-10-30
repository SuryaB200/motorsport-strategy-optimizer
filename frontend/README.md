# Motorsport Pit-Stop & Tire Strategy Optimizer — Frontend

A high-performance Formula 1 pit-wall strategy analytics dashboard built with **React**, **TypeScript**, **Vite**, **Tailwind CSS**, and **Recharts**.

Connected to a Python **FastAPI** simulation engine with **Monte Carlo Tree Search (MCTS)** and **Common Random Numbers (CRN)** stochastic optimization under uncertain weather and Safety Car deployments.

---

## 🏁 System Features

The frontend reproduces the dark pit-wall command aesthetic (#090D12 base, #0D1219 sidebar, #111821 cards, #F20D2F racing red) across 6 specialized modules:

1. **Race Overview (`RaceOverview.tsx`)**:
   - Interactive circuit selection (Monaco, Silverstone, Spa, Monza, Albert Park, Americas).
   - Dynamic track geometry vector map with sector markers.
   - Real-time track & air temperature gauges and rain probability indicator.
   - Live stint progress bar and remaining lap countdown.
   - Current tire compound widget with circular life/wear ring.
   - Safety car status flag, pit window target, and estimated race completion time.

2. **Race Simulation (`Simulation.tsx`)**:
   - Comprehensive stochastic parameter controls (Laps, Initial Weather, Markov rain transition probability, Safety Car probability, duration, pace variation $\sigma$, random seed).
   - Multi-tab visualization suite:
     - **Lap Chart**: Dual-line degradation trajectory (Simulated telemetry vs Optimal baseline) with Safety Car shaded overlay bands.
     - **Weather Timeline**: Multi-color horizontal stint bar (Dry, Int. Wet, Wet, Safety Car).
     - **Event Telemetry**: Chronological pit-wall incident log.
     - **Summary Metrics**: Net delta vs target, tire cliff margin, and pit loss audit.

3. **Tire Sets Management (`TireSets.tsx`)**:
   - Inventory table of allocated tire sets (Soft C4/C5, Medium C3, Hard C2, Intermediates, Wets).
   - Compound badges with color coding (Red, Amber, White, Emerald, Blue).
   - Real-time wear percentage bar and remaining laps calculation.
   - Interactive **"Fit"** button to equip any tire set to the active car.
   - Compound filter pills and live search bar.
   - FIA/Pirelli allocation compliance cards.

4. **Strategy Optimization (`StrategyOptimization.tsx`)**:
   - Algorithmic controls: Monte Carlo Tree Search (MCTS), Common Random Numbers (CRN), and Hybrid rollouts.
   - Objective functions: Minimize Expected Time $E[T]$, Maximize Win Probability $P(\text{Win})$, or Risk-Averse Mean - $\lambda \cdot \text{StdDev}$.
   - Allowed compound toggles and risk penalty slider ($\lambda$).
   - Optimal strategy recommendation card with convergence badge.
   - High-level telemetry: Expected Time, Std Deviation ($\pm \sigma$), Median Time, and 95% Confidence Interval.
   - Visual Stint Timeline breakdown with color-coded compound bands.
   - Strategy Leaderboard table ranking candidate alternatives with deltas to 1st place.
   - Tactical pit stop schedule with Safety Car probability at pit window.

5. **Weather & Risk Analysis (`WeatherRisk.tsx`)**:
   - **Rain Probability by Lap**: Interactive area curve tracking dynamic rain spikes.
   - **Weather Transition Matrix**: 3x3 Markov Chain probability heatmap table (Dry $\leftrightarrow$ Int $\leftrightarrow$ Wet).
   - **Safety Car Likelihood**: 5-lap window histogram showing incident risk hotspots.
   - **Finish Time Distribution**: Monte Carlo Gaussian histogram of projected race times.
   - **Strategy Sensitivity Curve**: Multi-line plot demonstrating how Conservative, Balanced, and Aggressive strategies degrade across increasing rain probabilities.

6. **Results & History (`ResultsHistory.tsx`)**:
   - Historical log of optimization runs with circuit filters and search.
   - Comparative metrics (Algorithm, Best Strategy, Expected Time, Simulation count).
   - Interactive **"View"** modal displaying full telemetry report.

7. **Overview Grid Mode (`OverviewGrid.tsx`)**:
   - 6-panel composite command layout displaying mini-telemetry for all modules simultaneously.
   - One-click navigation to single-focus mode from any panel.

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js v18+ (tested on Node v24)
- npm or yarn

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Copy `.env.example` to `.env` (optional; defaults to proxying `/api` to `http://127.0.0.1:8000`):
```bash
cp .env.example .env
```

### 3. Run Development Server
```bash
npm run dev
```
The app will launch at `http://localhost:5173/`.

### 4. Build for Production
```bash
npm run build
```
Generates optimized static assets in the `dist/` directory.

---

## 🛠 Tech Stack

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS 3
- **Charts**: Recharts
- **Icons**: Lucide React

