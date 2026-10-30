"""Database repository tests using isolated in-memory SQLite."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.repository import RaceRepository
from app.schemas.race import RaceConfig, TireCompound
from app.schemas.results import StrategySummaryStats
from app.schemas.strategy import PitStopDecision, Strategy


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_repository_race_crud(test_db):
    config = RaceConfig(race_name="Spa-Francorchamps", total_laps=44)
    model = RaceRepository.create_race(test_db, config)
    assert model.race_id is not None

    retrieved = RaceRepository.get_race(test_db, model.race_id)
    assert retrieved is not None
    assert retrieved.race_name == "Spa-Francorchamps"


def test_repository_simulation_run_lifecycle(test_db):
    config = RaceConfig(total_laps=20)
    race = RaceRepository.create_race(test_db, config)

    run = RaceRepository.create_simulation_run(test_db, race.race_id, "MONTE_CARLO", 42, 100)
    assert run.status == "PENDING"
    assert run.completion_time is None

    RaceRepository.complete_simulation_run(test_db, run.run_id)
    test_db.refresh(run)
    assert run.status == "COMPLETED"
    assert run.completion_time is not None


def test_repository_save_and_retrieve_strategy_results(test_db):
    config = RaceConfig(total_laps=20)
    race = RaceRepository.create_race(test_db, config)
    run = RaceRepository.create_simulation_run(test_db, race.race_id, "OPTIMIZE_MCTS", 42, 50)

    strat = Strategy(
        name="1-Stop Medium-Hard",
        initial_compound=TireCompound.MEDIUM,
        pit_stops=[PitStopDecision(lap=10, compound=TireCompound.HARD)],
    )
    summary = StrategySummaryStats(
        strategy=strat,
        simulation_count=50,
        mean_race_time=1850.2,
        median_race_time=1850.0,
        std_dev_race_time=6.4,
        min_race_time=1835.0,
        max_race_time=1865.0,
        p95_race_time=1860.0,
        confidence_interval_95_low=1848.4,
        confidence_interval_95_high=1852.0,
        objective_value=1850.2,
        rank=1,
    )

    models = RaceRepository.save_strategy_results(test_db, run.run_id, [summary], "EXPECTED_TIME")
    assert len(models) == 1

    res_id = models[0].result_id
    retrieved = RaceRepository.get_strategy_result(test_db, res_id)
    assert retrieved is not None
    assert retrieved.mean_race_time == 1850.2
    assert retrieved.rank == 1

    run_strategies = RaceRepository.get_strategies_for_run(test_db, run.run_id)
    assert len(run_strategies) == 1
