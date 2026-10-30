export type TireCompound = 'SOFT' | 'MEDIUM' | 'HARD' | 'INTERMEDIATE' | 'WET';

export type WeatherCondition = 'DRY' | 'DRIZZLE' | 'RAIN' | 'HEAVY_RAIN';

export type SafetyCarStatus = 'NONE' | 'VIRTUAL_SAFETY_CAR' | 'SAFETY_CAR';

export interface CircuitConfig {
  circuit_id: string;
  name: string;
  total_laps: number;
  baseline_lap_time: number;
  circuit_wear_factor: number;
  is_street_circuit: boolean;
  pit_loss: number;
}

export interface TireStint {
  stint_index?: number;
  compound: TireCompound;
  start_lap: number;
  end_lap: number;
  planned_laps: number;
  initial_wear?: number;
}

export interface Strategy {
  strategy_id: string;
  name: string;
  stints: TireStint[];
  pit_laps: number[];
  compounds: TireCompound[];
  expected_time?: number;
  time_std?: number;
  win_probability?: number;
  risk_score?: number;
}

export interface LapTelemetry {
  lap_number: number;
  compound: TireCompound;
  tire_age: number;
  tire_wear: number;
  lap_time: number;
  cumulative_time: number;
  fuel_load: number;
  weather: WeatherCondition;
  track_water_depth: number;
  safety_car: SafetyCarStatus;
  is_pit_lap: boolean;
  pit_duration: number;
}

export interface SingleSimulationResult {
  strategy_name: string;
  total_time: number;
  laps: LapTelemetry[];
  total_stops: number;
  safety_car_laps: number;
  rain_laps: number;
  circuit_name?: string;
}

export interface OptimizationRequest {
  circuit_id: string;
  total_laps?: number;
  baseline_lap_time?: number;
  num_simulations?: number;
  algorithm?: 'mcts' | 'monte_carlo' | 'hybrid';
  risk_aversion?: number;
  pit_window_start?: number;
  pit_window_end?: number;
}

export interface RankedStrategy {
  strategy: Strategy;
  mean_time: number;
  std_time: number;
  min_time: number;
  max_time: number;
  p95_time: number;
  win_rate: number;
  risk_score: number;
  rank: number;
}

export interface OptimizationResponse {
  run_id?: string;
  recommended_strategy: Strategy;
  ranked_strategies: RankedStrategy[];
  algorithm_used: string;
  simulations_run: number;
  execution_time_seconds: number;
  circuit?: CircuitConfig;
}

export interface TireSetInventoryItem {
  id: string;
  set_number: string;
  compound: TireCompound;
  status: 'NEW' | 'USED' | 'FITTED' | 'SCRUBBED';
  laps_run: number;
  wear_percent: number;
  allocation_session: string;
  allocated_date: string;
}

export interface HistoricalRunItem {
  id: string;
  run_id: string;
  created_at: string;
  circuit_name: string;
  circuit_id: string;
  total_laps: number;
  algorithm: string;
  simulations_count: number;
  best_strategy: string;
  best_time_formatted: string;
  best_time_seconds: number;
  risk_lambda: number;
  status: 'COMPLETED' | 'RUNNING' | 'FAILED';
}

