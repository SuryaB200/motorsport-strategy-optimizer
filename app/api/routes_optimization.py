"""Endpoints for motorsport strategy optimization."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import RaceRepository
from app.schemas.race import RaceConfig
from app.schemas.results import OptimizationRequest, OptimizationResponse
from app.services.optimizer import StrategyOptimizer

router = APIRouter(prefix="/api/v1/strategies", tags=["Optimization"])


@router.post("/optimize", response_model=OptimizationResponse)
def optimize_strategy(
    request: OptimizationRequest,
    db: Session = Depends(get_db),
) -> OptimizationResponse:
    """Evaluate and optimize pit-stop and tire strategy using Monte Carlo simulation or MCTS."""
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
        persisted = RaceRepository.create_race(db, config)
        db_race_id = persisted.race_id
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'race_id' or 'race_config' must be provided.",
        )

    seed = request.random_seed if request.random_seed is not None else config.random_seed
    run_model = RaceRepository.create_simulation_run(
        db=db,
        race_id=db_race_id,
        run_type=f"OPTIMIZE_{request.method.value}",
        random_seed=seed,
        simulation_count=request.monte_carlo_simulations,
    )

    try:
        response = StrategyOptimizer.optimize(
            config=config,
            request=request,
            race_id=db_race_id,
        )
        # Update run_id to match persistent run_model
        response.run_id = run_model.run_id

        # Persist strategy comparisons
        RaceRepository.save_strategy_results(
            db=db,
            run_id=run_model.run_id,
            summaries=response.candidate_comparisons,
            objective_type=request.objective_type.value,
        )

        RaceRepository.complete_simulation_run(db, run_model.run_id)
        return response

    except Exception as exc:
        RaceRepository.complete_simulation_run(db, run_model.run_id, error_message=str(exc))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Optimization failed: {str(exc)}",
        )
