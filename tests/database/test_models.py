"""Tests for SQLAlchemy database initialization, session management, and models."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    LapEventModel,
    RaceConfigModel,
    SimulationRunModel,
    StrategyResultModel,
)


@pytest.fixture
def db_session():
    """Create an isolated in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_and_retrieve_race_config(db_session):
    race = RaceConfigModel(
        race_id="race-test-01",
        race_name="Monza Test Grand Prix",
        circuit_id="monza",
        config_json='{"total_laps": 53}',
    )
    db_session.add(race)
    db_session.commit()

    retrieved = db_session.query(RaceConfigModel).filter_by(race_id="race-test-01").first()
    assert retrieved is not None
    assert retrieved.race_name == "Monza Test Grand Prix"
    assert retrieved.circuit_id == "monza"


def test_simulation_run_foreign_key_and_cascade(db_session):
    race = RaceConfigModel(
        race_id="race-cascade-01",
        race_name="Silverstone GP",
        circuit_id="silverstone",
        config_json='{"total_laps": 52}',
    )
    db_session.add(race)
    db_session.commit()

    run = SimulationRunModel(
        run_id="run-01",
        race_id="race-cascade-01",
        run_type="MONTE_CARLO",
        status="COMPLETED",
        random_seed=42,
        simulation_count=100,
    )
    db_session.add(run)
    db_session.commit()

    res = StrategyResultModel(
        result_id="res-01",
        run_id="run-01",
        strategy_json='{"name": "One Stop"}',
        mean_race_time=4800.5,
        median_race_time=4800.0,
        std_dev_race_time=12.3,
        p95_race_time=4820.0,
        rank=1,
    )
    db_session.add(res)
    db_session.commit()

    lap = LapEventModel(
        event_id="lap-01",
        run_id="run-01",
        lap_number=1,
        lap_time=91.2,
        compound="MEDIUM",
        tire_age=1,
        weather="DRY",
        safety_car_active=False,
        pit_stop_occurred=False,
    )
    db_session.add(lap)
    db_session.commit()

    # Verify retrieval via relationship
    queried_run = db_session.query(SimulationRunModel).filter_by(run_id="run-01").first()
    assert queried_run is not None
    assert len(queried_run.strategy_results) == 1
    assert len(queried_run.lap_events) == 1

    # Cascade delete race -> removes runs, results, lap events
    db_session.delete(race)
    db_session.commit()

    assert db_session.query(SimulationRunModel).filter_by(run_id="run-01").first() is None
    assert db_session.query(StrategyResultModel).filter_by(result_id="res-01").first() is None
    assert db_session.query(LapEventModel).filter_by(event_id="lap-01").first() is None
