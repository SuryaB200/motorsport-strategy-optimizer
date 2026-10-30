"""Database repository for transactional persistence of race models and results."""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import (
    LapEventModel,
    RaceConfigModel,
    SimulationRunModel,
    StrategyResultModel,
)
from app.schemas.race import RaceConfig
from app.schemas.results import StrategySummaryStats
from app.schemas.simulation import LapTelemetry


class RaceRepository:
    """Manages database CRUD operations with SQLite."""

    @staticmethod
    def create_race(db: Session, config: RaceConfig) -> RaceConfigModel:
        """Persist a new race configuration."""
        race_model = RaceConfigModel(
            race_name=config.race_name,
            circuit_id=config.circuit_id,
            config_json=config.model_dump_json(),
        )
        db.add(race_model)
        db.commit()
        db.refresh(race_model)
        return race_model

    @staticmethod
    def get_race(db: Session, race_id: str) -> Optional[RaceConfigModel]:
        """Retrieve a stored race configuration by ID."""
        return db.query(RaceConfigModel).filter(RaceConfigModel.race_id == race_id).first()

    @staticmethod
    def create_simulation_run(
        db: Session,
        race_id: str,
        run_type: str,
        random_seed: int,
        simulation_count: int = 1,
    ) -> SimulationRunModel:
        """Create a new tracked simulation run entry."""
        run_model = SimulationRunModel(
            race_id=race_id,
            run_type=run_type,
            status="PENDING",
            random_seed=random_seed,
            simulation_count=simulation_count,
        )
        db.add(run_model)
        db.commit()
        db.refresh(run_model)
        return run_model

    @staticmethod
    def complete_simulation_run(
        db: Session,
        run_id: str,
        error_message: Optional[str] = None,
    ) -> None:
        """Mark a simulation run completed or failed."""
        run = db.query(SimulationRunModel).filter(SimulationRunModel.run_id == run_id).first()
        if run:
            run.completion_time = datetime.now(timezone.utc)
            if error_message:
                run.status = "FAILED"
                run.error_message = error_message
            else:
                run.status = "COMPLETED"
            db.commit()

    @staticmethod
    def save_lap_telemetry(
        db: Session,
        run_id: str,
        telemetry: list[LapTelemetry],
    ) -> None:
        """Batch save lap events for a single race simulation."""
        events = [
            LapEventModel(
                run_id=run_id,
                lap_number=t.lap_number,
                lap_time=t.lap_time,
                compound=t.compound.value,
                tire_age=t.tire_age,
                weather=t.weather.value,
                safety_car_active=t.safety_car_active,
                pit_stop_occurred=t.pit_stop_taken,
            )
            for t in telemetry
        ]
        db.bulk_save_objects(events)
        db.commit()

    @staticmethod
    def save_strategy_results(
        db: Session,
        run_id: str,
        summaries: list[StrategySummaryStats],
        objective_type: str,
    ) -> list[StrategyResultModel]:
        """Save statistical evaluation metrics for candidate strategies."""
        models: list[StrategyResultModel] = []
        for s in summaries:
            model = StrategyResultModel(
                run_id=run_id,
                strategy_json=s.strategy.model_dump_json(),
                objective_type=objective_type,
                mean_race_time=s.mean_race_time,
                median_race_time=s.median_race_time,
                std_dev_race_time=s.std_dev_race_time,
                p95_race_time=s.p95_race_time,
                rank=s.rank,
                metadata_json=json.dumps(
                    {
                        "min_race_time": s.min_race_time,
                        "max_race_time": s.max_race_time,
                        "ci_95_low": s.confidence_interval_95_low,
                        "ci_95_high": s.confidence_interval_95_high,
                        "objective_value": s.objective_value,
                        "simulation_count": s.simulation_count,
                    }
                ),
            )
            db.add(model)
            models.append(model)
        db.commit()
        for m in models:
            db.refresh(m)
        return models

    @staticmethod
    def get_strategy_result(db: Session, result_id: str) -> Optional[StrategyResultModel]:
        """Retrieve a specific strategy result by ID."""
        return (
            db.query(StrategyResultModel).filter(StrategyResultModel.result_id == result_id).first()
        )

    @staticmethod
    def get_strategies_for_run(db: Session, run_id: str) -> list[StrategyResultModel]:
        """Retrieve all strategy comparisons for a run, ordered by rank."""
        return (
            db.query(StrategyResultModel)
            .filter(StrategyResultModel.run_id == run_id)
            .order_by(StrategyResultModel.rank.asc())
            .all()
        )
