import json
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.vehicle_state import VehicleStateRecord
from app.vehicle_data.models import VehicleState
from app.vehicle_data.providers.json_file import JSONFileProvider
from app.vehicle_data.validation import count_populated_fields

class VehicleDataService:
    @staticmethod
    def _generate_vehicle_state_id(db: Session) -> str:
        count = db.query(VehicleStateRecord).count()
        return f"VS-{count + 1:06d}"

    @classmethod
    def import_from_json_content(
        cls,
        db: Session,
        raw_content: str,
        filename: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[VehicleState], List[Dict[str, str]], List[str], int]:
        """
        Parses, validates, and persists a VehicleState payload from raw JSON text.
        Returns: (success, vehicle_state_id, vehicle_state, errors, warnings, field_count)
        """
        provider = JSONFileProvider(raw_content)

        if not provider.is_valid:
            return False, None, None, provider.errors, provider.warnings, 0

        vehicle_state = provider.get_vehicle_state()
        state_id = cls._generate_vehicle_state_id(db)

        raw_payload_str = json.dumps(provider.raw_dict)
        normalized_dict = vehicle_state.model_dump(mode="json")
        normalized_payload_str = json.dumps(normalized_dict)

        field_count = count_populated_fields(normalized_dict)

        record = VehicleStateRecord(
            id=state_id,
            schema_version=vehicle_state.schema_version,
            timestamp=vehicle_state.timestamp,
            source_type=vehicle_state.source.type.value,
            source_simulator=vehicle_state.source.simulator,
            source_provider=vehicle_state.source.provider,
            session_id=vehicle_state.source.session_id,
            raw_payload=raw_payload_str,
            normalized_payload=normalized_payload_str,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return True, state_id, vehicle_state, [], provider.warnings, field_count

    @classmethod
    def get_current_vehicle_state(cls, db: Session) -> Tuple[Optional[str], Optional[VehicleStateRecord], Optional[Dict[str, Any]]]:
        """
        Retrieves the most recently imported valid VehicleState record.
        Returns: (state_id, record, normalized_dict)
        """
        record = (
            db.query(VehicleStateRecord)
            .order_by(VehicleStateRecord.created_at.desc(), VehicleStateRecord.id.desc())
            .first()
        )
        if not record:
            return None, None, None

        try:
            normalized_data = json.loads(record.normalized_payload)
            return record.id, record, normalized_data
        except Exception:
            return record.id, record, None

    @classmethod
    def get_history(cls, db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve recent vehicle state import history summaries.
        """
        records = (
            db.query(VehicleStateRecord)
            .order_by(VehicleStateRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        history = []
        for r in records:
            history.append({
                "id": r.id,
                "schema_version": r.schema_version,
                "timestamp": r.timestamp,
                "source_type": r.source_type,
                "source_provider": r.source_provider,
                "session_id": r.session_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        return history
