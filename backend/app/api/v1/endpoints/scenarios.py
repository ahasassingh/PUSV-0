from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.scenario import Scenario, CompoundScenario
from app.schemas.scenario import ScenarioSchema, CompoundScenarioCreateSchema, CompoundScenarioSchema

router = APIRouter()

@router.get("", response_model=List[ScenarioSchema])
@router.get("/", response_model=List[ScenarioSchema])
def get_scenarios(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Scenario)
    if category:
        query = query.filter(Scenario.category == category)
    return query.order_by(Scenario.category.asc(), Scenario.code.asc()).all()

@router.get("/{id}", response_model=ScenarioSchema)
def get_scenario(id: str, db: Session = Depends(get_db)):
    scen = db.query(Scenario).filter((Scenario.id == id) | (Scenario.code == id)).first()
    if not scen:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scen

@router.post("/compound")
def create_compound_scenario(payload: CompoundScenarioCreateSchema, db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).filter(Scenario.id.in_(payload.scenario_ids)).all()
    if not scenarios:
        raise HTTPException(status_code=400, detail="No valid scenarios provided")

    # Merge environmental coefficients
    min_friction = min([s.road_friction for s in scenarios])
    max_visibility_red = max([s.visibility_reduction_pct for s in scenarios])
    
    combined = {
        "road_friction_mu": min_friction,
        "visibility_reduction_pct": max_visibility_red,
        "participating_categories": list(set([s.category for s in scenarios])),
        "sub_scenarios": [{"id": s.id, "name": s.name, "category": s.category} for s in scenarios]
    }

    compound = CompoundScenario(
        id=f"cmp_{len(db.query(CompoundScenario).all()) + 1}",
        name=payload.name,
        description=payload.description or f"Compound scenario composed of {len(scenarios)} conditions.",
        created_at=datetime.utcnow()
    )
    compound.scenario_ids = payload.scenario_ids
    compound.combined_params = combined
    db.add(compound)
    db.commit()
    db.refresh(compound)

    return {
        "id": compound.id,
        "name": compound.name,
        "description": compound.description,
        "scenario_ids": compound.scenario_ids,
        "combined_params": compound.combined_params
    }
