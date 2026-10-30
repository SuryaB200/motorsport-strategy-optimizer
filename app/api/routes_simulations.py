"""Endpoints for running single race simulations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import RaceRepository
from app.schemas.race import RaceConfig
from app.schemas.simulation import SimulationRequest, SingleSimulationResult
from app.services.race_simulator import RaceSimulator
from app.services.random_source import RandomSource

router = APIRouter(prefix="/api/v1/simulations", tags=["Simulations"])


@router.post("", response_model=SingleSimulationResult)
def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db),
) -> SingleSimulationResult:
    """Execute a single race simulation using a specified or stored race configuration."""
    # Resolve race configuration
    if request.race_id:
        race_model = RaceRepository.get_race(db, request.race_id)
        if not race_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Race configuration with ID '{request.race_id}' not found.",
            )
        config = RaceConfig.model_validate_json(race_model.config_json)
        db_race_id = race_model.race_id
    elif request.race_config:
        config = request.race_config
        # Store transient configuration so foreign keys remain intact
        persisted = RaceRepository.create_race(db, config)
        db_race_id = persisted.race_id
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'race_id' or 'race_config' must be provided.",
        )

    # Initialize PRNG
    seed = request.random_seed if request.random_seed is not None else config.random_seed
    rng = RandomSource(seed=seed)

    # Register simulation run
    run_model = RaceRepository.create_simulation_run(
        db=db,
        race_id=db_race_id,
        run_type="SINGLE_SIMULATION",
        random_seed=seed,
        simulation_count=1,
    )

    try:
        result = RaceSimulator.simulate(
            config=config,
            strategy=request.strategy,
            random_source=rng,
            record_telemetry=request.record_telemetry,
        )

        if request.record_telemetry and result.telemetry:
            RaceRepository.save_lap_telemetry(db, run_model.run_id, result.telemetry)

        RaceRepository.complete_simulation_run(db, run_model.run_id)
        return result

    except Exception as exc:
        RaceRepository.complete_simulation_run(db, run_model.run_id, error_message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation error: {str(exc)}",
        )
