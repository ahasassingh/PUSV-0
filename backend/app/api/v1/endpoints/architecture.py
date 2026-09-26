from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.vehicle import ECU, Sensor, Actuator, Signal
from app.schemas.vehicle import VehicleGraphSchema, GraphNode, GraphEdge, ECUSchema, SignalSchema

router = APIRouter()

@router.get("/graph", response_model=VehicleGraphSchema)
def get_vehicle_graph(db: Session = Depends(get_db)):
    nodes = []
    edges = []

    ecus = db.query(ECU).all()
    sensors = db.query(Sensor).all()
    actuators = db.query(Actuator).all()
    signals = db.query(Signal).all()

    for ecu in ecus:
        nodes.append(GraphNode(
            id=ecu.id,
            label=ecu.name,
            type="ECU",
            domain=ecu.domain,
            subsystem=ecu.subsystem,
            extra={"bus_type": ecu.bus_type, "asil": ecu.safety_integrity_level}
        ))

    for s in sensors:
        nodes.append(GraphNode(
            id=s.id,
            label=s.name,
            type="SENSOR",
            subsystem=s.sensor_type,
            extra={"rate_hz": s.sampling_rate_hz, "unit": s.unit}
        ))
        edges.append(GraphEdge(
            source=s.id,
            target=s.ecu_id,
            relation="FEEDS_INTO"
        ))

    for a in actuators:
        nodes.append(GraphNode(
            id=a.id,
            label=a.name,
            type="ACTUATOR",
            subsystem=a.actuator_type,
            extra={"response_ms": a.response_time_ms}
        ))
        edges.append(GraphEdge(
            source=a.ecu_id,
            target=a.id,
            relation="CONTROLS"
        ))

    for sig in signals:
        nodes.append(GraphNode(
            id=sig.id,
            label=sig.name,
            type="SIGNAL",
            subsystem=sig.signal_type,
            extra={"cycle_ms": sig.cycle_time_ms, "unit": sig.unit}
        ))
        # Edge from source ECU to signal
        edges.append(GraphEdge(
            source=sig.source_ecu_id,
            target=sig.id,
            relation="TRANSMITS"
        ))
        # Edges from signal to consumer ECUs
        for consumer_id in sig.consumer_ecu_ids:
            edges.append(GraphEdge(
                source=sig.id,
                target=consumer_id,
                relation="CONSUMED_BY"
            ))

    return VehicleGraphSchema(nodes=nodes, edges=edges)

@router.get("/ecus")
def get_ecus(db: Session = Depends(get_db)):
    ecus = db.query(ECU).all()
    result = []
    for e in ecus:
        sensors = db.query(Sensor).filter(Sensor.ecu_id == e.id).all()
        actuators = db.query(Actuator).filter(Actuator.ecu_id == e.id).all()
        signals_produced = db.query(Signal).filter(Signal.source_ecu_id == e.id).all()
        result.append({
            "id": e.id,
            "name": e.name,
            "subsystem": e.subsystem,
            "domain": e.domain,
            "description": e.description,
            "bus_type": e.bus_type,
            "safety_integrity_level": e.safety_integrity_level,
            "sensors": [{"id": s.id, "name": s.name, "type": s.sensor_type} for s in sensors],
            "actuators": [{"id": a.id, "name": a.name, "type": a.actuator_type} for a in actuators],
            "signals_produced": [{"id": sig.id, "name": sig.name, "cycle_ms": sig.cycle_time_ms} for sig in signals_produced]
        })
    return result

@router.get("/signals")
def get_signals(db: Session = Depends(get_db)):
    signals = db.query(Signal).all()
    result = []
    for s in signals:
        result.append({
            "id": s.id,
            "name": s.name,
            "source_ecu_id": s.source_ecu_id,
            "consumer_ecu_ids": s.consumer_ecu_ids,
            "signal_type": s.signal_type,
            "unit": s.unit,
            "min_value": s.min_value,
            "max_value": s.max_value,
            "cycle_time_ms": s.cycle_time_ms,
            "default_value": s.default_value
        })
    return result
