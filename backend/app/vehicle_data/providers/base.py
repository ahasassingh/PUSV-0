from abc import ABC, abstractmethod
from app.vehicle_data.models import VehicleState

class VehicleDataProvider(ABC):
    """
    Abstract interface for vehicle telemetry & state providers.
    All vehicle state consumers (including future AI Test Case Generators,
    simulation orchestrators, and validation oracles) must depend ONLY on this
    abstraction, NEVER on concrete simulator implementations like Assetto Corsa.
    """

    @abstractmethod
    def get_vehicle_state(self) -> VehicleState:
        """
        Retrieve a validated, canonical VehicleState instance.
        Raises ValueError or appropriate domain exception if state is unavailable or invalid.
        """
        pass
