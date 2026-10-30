# Motorsport Pit-Stop & Tire Strategy Optimizer — Desktop Application (v1.0.0)

This directory contains the standalone Windows Desktop executable for the **Motorsport Pit-Stop & Tire Strategy Optimization System**.

## 🏎️ What is Included?

- `MotorsportOptimizer.exe` (Standalone Windows 64-bit Executable)
  - **Embedded Python Runtime & FastAPI Backend**: Uvicorn server running asynchronously on localhost.
  - **Embedded React 19 Frontend**: High-frequency Formula 1 pit-wall telemetry dashboard pre-compiled into static production assets.
  - **Native Desktop Window Integration**: Uses Windows PyWebView (or system default browser fallback) for a borderless, low-latency desktop interface.
  - **Empirical F1 Calibration Data**: Bundled tire wear, pit-lane loss, and safety car models calibrated from historical Formula 1 Grand Prix timing databases.
  - **No external Python or Node.js runtime required**: Fully self-contained single executable.

---

## 🚀 Quick Launch Instructions

### Method 1: Double-Click Launch
1. Double-click `MotorsportOptimizer.exe`.
2. A console window will initialize the internal stochastic simulation engine and database.
3. The native desktop dashboard window will open automatically displaying the **Motorsport Pit-Stop & Tire Strategy Optimizer**.
4. To close the application, simply close the desktop window or press `Ctrl + C` in the console window.

### Method 2: Command Line Launch
```powershell
.\MotorsportOptimizer.exe
```

The application automatically identifies an available network port (defaulting to `8000`), seeds local SQLite tables, mounts the telemetry API endpoints, and serves the dashboard UI.

---

## ⚙️ Features Available in Desktop Mode

1. **Race Monitoring & Track Overview**:
   - Interactive circuit selection (Silverstone, Monza, Spa-Francorchamps, Monaco, Circuit de Barcelona-Catalunya, etc.).
   - Live telemetry status, track conditions, lap progress, and pit-stop countdowns.
2. **Stochastic Simulation Engine**:
   - High-throughput Monte Carlo simulation with correlated normal pace variations.
   - 3-State discrete Markov weather transitions (Dry / Intermediate / Wet).
   - Compound Poisson Safety Car and Virtual Safety Car (VSC) hazard injections.
3. **Tire Inventory Management**:
   - Track compound allocations (Soft, Medium, Hard, Intermediate, Wet).
   - Real-time wear degradation monitoring, remaining life estimation, and active set fitting.
4. **Strategy Optimization Engine**:
   - Monte Carlo exhaustive candidate ranking & Monte Carlo Tree Search (MCTS) exploration.
   - Dual objective functions: Expected Race Time minimization ($\pi^* = \arg\min \mathbb{E}[T \mid \pi]$) and Risk-Sensitive CVaR optimization ($J(\pi) = \mathbb{E}[T] + \lambda \cdot \text{SD}[T]$).
5. **Weather & Risk Analytics**:
   - Non-stationary lap-by-lap precipitation projections.
   - Empirical Markov transition matrices and probability density distributions.
   - Compound crossover point sensitivity curves.
6. **Simulation History & Results Database**:
   - SQLite-backed run persistence with JSON stint breakdowns and statistical dispersion metrics.
7. **Customizable Pit-Wall UX (Settings Drawer)**:
   - **Glassmorphism / Frosted Glass**: Toggle GPU-accelerated backdrop blur.
   - **F1 Neon Laser Glow**: Toggle high-contrast telemetry accent lighting.
   - **Live Stream Polling**: Toggle real-time background simulation synchronization.

---

## 🔒 System Requirements & Offline Operation
- **OS**: Windows 10 / Windows 11 (64-bit)
- **RAM**: 4 GB minimum (8 GB recommended for 5,000+ Monte Carlo batches)
- **Network**: **100% Offline Capable**. All simulation algorithms, regression engines, and frontend assets execute locally on your machine with zero external cloud dependencies.
