"""Endpoints for machine learning training and empirical parameter calibration."""

import json
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.repository import RaceRepository
from app.schemas.race import RaceConfigResponse
from app.services.trainer import DataTrainer

router = APIRouter(prefix="/api/v1/calibration", tags=["Calibration & Training"])

CALIBRATION_FILE = str(settings.BASE_DIR / "data" / "calibrated_models.json")


class TrainingRequest(BaseModel):
    """Request payload to initiate parameter training."""

    dataset_path: str = Field(
        default="C:/SDM 2 MOTOR/datasets",
        description="Path to uploaded datasets containing Formula1.sqlite and notebooks.",
    )


class TrainingResponse(BaseModel):
    """Response payload detailing training outcomes."""

    status: str
    dataset_source: str
    training_timestamp: str
    pit_loss_model: dict
    safety_car_model: dict
    tire_regression_scores: dict
    calibrated_circuits: list[str]


@router.post("/train", response_model=TrainingResponse)
def train_models_from_dataset(request: TrainingRequest) -> TrainingResponse:
    """Train tire degradation regression, pit loss distribution, and safety car models from dataset."""
    if not os.path.exists(request.dataset_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset directory '{request.dataset_path}' not found.",
        )

    try:
        results = DataTrainer.train_all(
            dataset_path=request.dataset_path,
            output_file=CALIBRATION_FILE,
        )
        return TrainingResponse(
            status="SUCCESS",
            dataset_source=results["dataset_source"],
            training_timestamp=results["training_timestamp"],
            pit_loss_model=results["pit_model"],
            safety_car_model=results["safety_car_model"],
            tire_regression_scores=results["tire_model"]["r2_scores"],
            calibrated_circuits=list(results["circuits"].keys()),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(exc)}",
        )


@router.get("/parameters")
def get_calibrated_parameters() -> dict:
    """Retrieve current calibrated model parameters."""
    if os.path.exists(CALIBRATION_FILE):
        with open(CALIBRATION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Train and return if not yet generated
    return DataTrainer.train_all(
        dataset_path="C:/SDM 2 MOTOR/datasets",
        output_file=CALIBRATION_FILE,
    )


@router.get("/circuits")
def list_calibrated_circuits() -> dict:
    """List available circuits calibrated from empirical F1 data."""
    params = get_calibrated_parameters()
    return params.get("circuits", {})


@router.post(
    "/races/{circuit_id}", response_model=RaceConfigResponse, status_code=status.HTTP_201_CREATED
)
def create_calibrated_race(
    circuit_id: str,
    db: Session = Depends(get_db),
) -> RaceConfigResponse:
    """Generate and persist a full RaceConfig directly calibrated from empirical F1 data for a circuit."""
    params = get_calibrated_parameters()
    if circuit_id not in params.get("circuits", {}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit '{circuit_id}' not found in calibrated catalog.",
        )

    config = DataTrainer.generate_calibrated_race_config(
        circuit_id=circuit_id,
        calibrated_data=params,
    )

    race_model = RaceRepository.create_race(db, config)
    return RaceConfigResponse(
        race_id=race_model.race_id,
        race_name=race_model.race_name,
        circuit_id=race_model.circuit_id,
        config=config,
        created_at=race_model.created_at.isoformat(),
    )
