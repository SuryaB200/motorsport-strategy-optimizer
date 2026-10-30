"""Endpoints for retrieving stored simulation and optimization results."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import RaceRepository

router = APIRouter(prefix="/api/v1/results", tags=["Results"])


@router.get("/{result_id}")
def get_strategy_result(
    result_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Retrieve an individual strategy result record by its result ID."""
    result = RaceRepository.get_strategy_result(db, result_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result with ID '{result_id}' not found.",
        )

    return {
        "result_id": result.result_id,
        "run_id": result.run_id,
        "strategy": json.loads(result.strategy_json),
        "objective_type": result.objective_type,
        "mean_race_time": result.mean_race_time,
        "median_race_time": result.median_race_time,
        "std_dev_race_time": result.std_dev_race_time,
        "p95_race_time": result.p95_race_time,
        "rank": result.rank,
        "metadata": json.loads(result.metadata_json) if result.metadata_json else {},
    }


@router.get("/{result_id}/strategies")
def get_strategies_for_result_run(
    result_id: str,
    db: Session = Depends(get_db),
) -> list[dict]:
    """Retrieve all ranked strategy comparisons for the optimization run associated with result_id."""
    res = RaceRepository.get_strategy_result(db, result_id)
    # Check if the param provided was a direct result_id or a run_id
    run_id = res.run_id if res else result_id

    strategies = RaceRepository.get_strategies_for_run(db, run_id)
    if not strategies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No strategy comparisons found for result/run ID '{result_id}'.",
        )

    return [
        {
            "result_id": s.result_id,
            "run_id": s.run_id,
            "strategy": json.loads(s.strategy_json),
            "objective_type": s.objective_type,
            "mean_race_time": s.mean_race_time,
            "median_race_time": s.median_race_time,
            "std_dev_race_time": s.std_dev_race_time,
            "p95_race_time": s.p95_race_time,
            "rank": s.rank,
            "metadata": json.loads(s.metadata_json) if s.metadata_json else {},
        }
        for s in strategies
    ]
