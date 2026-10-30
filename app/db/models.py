"""SQLAlchemy database models for motorsport strategy optimizer."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def generate_uuid() -> str:
    """Generate a string UUID."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)


class RaceConfigModel(Base):
    """Stores validated race configuration entities."""

    __tablename__ = "race_configurations"

    race_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    race_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    circuit_id: Mapped[str] = mapped_column(String(64), nullable=False)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    simulation_runs: Mapped[list["SimulationRunModel"]] = relationship(
        "SimulationRunModel", back_populates="race", cascade="all, delete-orphan"
    )


class SimulationRunModel(Base):
    """Tracks individual simulation and optimization execution runs."""

    __tablename__ = "simulation_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    race_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("race_configurations.race_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_type: Mapped[str] = mapped_column(String(32), nullable=False)  # SINGLE, MONTE_CARLO, MCTS
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING"
    )  # PENDING, COMPLETED, FAILED
    random_seed: Mapped[int] = mapped_column(Integer, nullable=False)
    simulation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    completion_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    race: Mapped["RaceConfigModel"] = relationship(
        "RaceConfigModel", back_populates="simulation_runs"
    )
    strategy_results: Mapped[list["StrategyResultModel"]] = relationship(
        "StrategyResultModel", back_populates="run", cascade="all, delete-orphan"
    )
    lap_events: Mapped[list["LapEventModel"]] = relationship(
        "LapEventModel", back_populates="run", cascade="all, delete-orphan"
    )


class StrategyResultModel(Base):
    """Stores statistical evaluation results for candidate strategies within a run."""

    __tablename__ = "strategy_results"

    result_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("simulation_runs.run_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    strategy_json: Mapped[str] = mapped_column(Text, nullable=False)
    objective_type: Mapped[str] = mapped_column(String(64), nullable=False, default="EXPECTED_TIME")
    mean_race_time: Mapped[float] = mapped_column(Float, nullable=False)
    median_race_time: Mapped[float] = mapped_column(Float, nullable=False)
    std_dev_race_time: Mapped[float] = mapped_column(Float, nullable=False)
    p95_race_time: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    run: Mapped["SimulationRunModel"] = relationship(
        "SimulationRunModel", back_populates="strategy_results"
    )

    __table_args__ = (Index("idx_strategy_run_rank", "run_id", "rank"),)


class LapEventModel(Base):
    """Detailed lap-by-lap telemetry for single-race or detailed analysis runs."""

    __tablename__ = "lap_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("simulation_runs.run_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time: Mapped[float] = mapped_column(Float, nullable=False)
    compound: Mapped[str] = mapped_column(String(16), nullable=False)
    tire_age: Mapped[int] = mapped_column(Integer, nullable=False)
    weather: Mapped[str] = mapped_column(String(16), nullable=False)
    safety_car_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pit_stop_occurred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationship
    run: Mapped["SimulationRunModel"] = relationship(
        "SimulationRunModel", back_populates="lap_events"
    )

    __table_args__ = (Index("idx_lap_run_number", "run_id", "lap_number"),)
