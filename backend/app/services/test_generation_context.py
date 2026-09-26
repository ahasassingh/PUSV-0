import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.requirement import Requirement, SpecificationGap
from app.models.vehicle import Vehicle, ECU, Sensor, Actuator, Signal
from app.core.config import settings

logger = logging.getLogger("civic_ai.test_generation_context")

class TestGenerationContextAssembler:
    """
    Assembles controlled engineering context for a normalized requirement
    before AI test-case generation.
    CRITICAL RULE: AI generates. Deterministic systems validate.
    Does NOT invent thresholds, timing, or ECU relations.
    """

    def __init__(self, db: Session):
        self.db = db

    def assemble(self, requirement_id: str) -> Dict[str, Any]:
        """
        Assemble requirement, vehicle, and matching architecture context.
        Accepts requirement database id or req_code (e.g. BRK-REQ-101).
        """
        req = self.db.query(Requirement).filter(
            (Requirement.id == requirement_id) | (Requirement.req_code == requirement_id)
        ).first()

        if not req:
            raise ValueError(f"Requirement not found: {requirement_id}")

        # Fetch vehicle
        vehicle = self.db.query(Vehicle).filter(Vehicle.id == req.vehicle_id).first()
        vehicle_info = {
            "id": vehicle.id if vehicle else settings.REFERENCE_VEHICLE,
            "name": vehicle.name if vehicle else "PUSV-01",
            "model": vehicle.reference_model if vehicle else "Honda Civic / PUSV-01 Ref",
            "sw_version": vehicle.sw_version if vehicle else settings.SW_VERSION
        }

        # Fetch specification gaps linked to this requirement
        gaps = self.db.query(SpecificationGap).filter(
            SpecificationGap.requirement_id == req.id
        ).all()
        gap_types = [g.gap_type for g in gaps]
        gap_details = [
            {
                "gap_type": g.gap_type,
                "severity": g.severity,
                "description": g.description,
                "missing_parameter": g.missing_parameter
            }
            for g in gaps
        ]

        # Find architectural context: ECU, sensors, actuators, signals
        matched_ecus = []
        matched_sensors = []
        matched_actuators = []
        matched_signals = []

        all_ecus = self.db.query(ECU).all()
        all_sensors = self.db.query(Sensor).all()
        all_actuators = self.db.query(Actuator).all()
        all_signals = self.db.query(Signal).all()

        text_to_search = f"{req.req_code} {req.system} {req.subsystem or ''} {req.original_text} {req.normalized_summary or ''}".lower()

        # Match primary ECU
        if req.ecu_id:
            primary_ecu = self.db.query(ECU).filter(ECU.id == req.ecu_id).first()
            if primary_ecu and primary_ecu.name not in matched_ecus:
                matched_ecus.append(primary_ecu.name)

        # Match ECUs by name or subsystem mention
        for ecu in all_ecus:
            ecu_name_clean = ecu.name.replace("_", " ").lower()
            if ecu.name.lower() in text_to_search or ecu_name_clean in text_to_search:
                if ecu.name not in matched_ecus:
                    matched_ecus.append(ecu.name)
            elif ecu.subsystem and ecu.subsystem.lower() in text_to_search:
                if ecu.name not in matched_ecus:
                    matched_ecus.append(ecu.name)

        # Match sensors
        for s in all_sensors:
            s_name_clean = s.name.replace("_", " ").lower()
            s_type_clean = s.sensor_type.replace("_", " ").lower()
            if s.name.lower() in text_to_search or s_name_clean in text_to_search or s_type_clean in text_to_search:
                matched_sensors.append({
                    "id": s.id,
                    "name": s.name,
                    "sensor_type": s.sensor_type,
                    "unit": s.unit,
                    "sampling_rate_hz": s.sampling_rate_hz,
                    "failure_modes": s.failure_modes
                })

        # Match actuators
        for a in all_actuators:
            a_name_clean = a.name.replace("_", " ").lower()
            a_type_clean = a.actuator_type.replace("_", " ").lower()
            if a.name.lower() in text_to_search or a_name_clean in text_to_search or a_type_clean in text_to_search:
                matched_actuators.append({
                    "id": a.id,
                    "name": a.name,
                    "actuator_type": a.actuator_type,
                    "response_time_ms": a.response_time_ms,
                    "max_output": a.max_output
                })

        # Match signals
        for sig in all_signals:
            sig_name_clean = sig.name.replace("_", " ").lower()
            if sig.name.lower() in text_to_search or sig_name_clean in text_to_search:
                matched_signals.append({
                    "id": sig.id,
                    "name": sig.name,
                    "unit": sig.unit,
                    "cycle_time_ms": sig.cycle_time_ms,
                    "min_value": sig.min_value,
                    "max_value": sig.max_value
                })

        architecture_context_status = "RESOLVED" if matched_ecus or matched_sensors or matched_signals else "UNKNOWN"

        # Traceability metadata
        traceability = req.source_traceability or {}
        source_doc = req.source_document or traceability.get("source_document") or "seeded_specification"
        source_page = req.source_page or traceability.get("source_page") or 1
        source_section = req.source_section or traceability.get("source_section") or req.system

        context = {
            "requirement": {
                "id": req.id,
                "req_code": req.req_code,
                "original_text": req.original_text,
                "normalized_summary": req.normalized_summary,
                "system": req.system,
                "subsystem": req.subsystem,
                "inputs": req.inputs,
                "outputs": req.outputs,
                "conditions": req.conditions,
                "dependencies": req.dependencies,
                "threshold": req.threshold,
                "timing_constraint": req.timing_constraint,
                "safety_relevance": req.safety_relevance,
                "completeness_status": req.completeness_status,
                "specification_gaps": gap_types,
                "specification_gap_details": gap_details,
                "traceability": {
                    "requirement_id": req.req_code,
                    "source_document": source_doc,
                    "source_page": source_page,
                    "source_section": source_section,
                    "source_location": req.source_location or traceability.get("source_location")
                }
            },
            "vehicle": vehicle_info,
            "architecture": {
                "status": architecture_context_status,
                "ecus": matched_ecus,
                "sensors": matched_sensors,
                "actuators": matched_actuators,
                "signals": matched_signals
            },
            "generation_rules": {
                "no_invented_thresholds": True,
                "no_invented_timing": True,
                "no_invented_ecus": True,
                "require_traceability": True,
                "require_expected_result": True,
                "require_pass_fail_criteria": True,
                "preserve_specification_gaps": True,
                "require_review_if_incomplete": True
            }
        }

        return context
