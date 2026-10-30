"""Endpoints for creating and retrieving race configurations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import RaceRepository
from app.schemas.race import RaceConfig, RaceConfigCreate, RaceConfigResponse

router = APIRouter(prefix="/api/v1/races", tags=["Races"])


@router.post("", response_model=RaceConfigResponse, status_code=status.HTTP_201_CREATED)
def create_race_configuration(
    race_in: RaceConfigCreate,
    db: Session = Depends(get_db),
) -> RaceConfigResponse:
    """Accept and validate a new race configuration, persisting it into the database."""
    race_model = RaceRepository.create_race(db, race_in)
    return RaceConfigResponse(
        race_id=race_model.race_id,
        race_name=race_model.race_name,
        circuit_id=race_model.circuit_id,
        config=RaceConfig.model_validate_json(race_model.config_json),
        created_at=race_model.created_at.isoformat(),
    )


@router.get("/{race_id}", response_model=RaceConfigResponse)
def get_race_configuration(
    race_id: str,
    db: Session = Depends(get_db),
) -> RaceConfigResponse:
    """Retrieve an existing race configuration by ID."""
    race_model = RaceRepository.get_race(db, race_id)
    if not race_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Race configuration with ID '{race_id}' not found.",
        )
    return RaceConfigResponse(
        race_id=race_model.race_id,
        race_name=race_model.race_name,
        circuit_id=race_model.circuit_id,
        config=RaceConfig.model_validate_json(race_model.config_json),
        created_at=race_model.created_at.isoformat(),
    )
