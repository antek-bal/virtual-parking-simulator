from collections import defaultdict
from typing import Dict, Any, List
from datetime import datetime
from src.app.services.pricing import PriceCalculator
from src.app.services.validator import VehicleValidator


class ParkingManager:
    active_parkings: Dict[str, Dict[str, Any]]
    history: Dict[str, List[Dict[str, Any]]]

    def __init__(self, price_calculator: PriceCalculator, validator: VehicleValidator):
        self.price_calculator = price_calculator
        self.validator = validator
        self.active_parkings = {}
        self.history = defaultdict(list)

    def register_entry(self, country: str, registration_no: str, floor: int) -> bool:
        if not self.validator.validate(country, registration_no):
            raise ValueError("Invalid registration number")

        vehicle_id = f"{country}_{registration_no}"

        if vehicle_id in self.active_parkings:
            raise ValueError("Vehicle already in the parking")

        if floor not in self.price_calculator.prices:
            raise ValueError(f"Floor {floor} is not available in this parking")

        self.active_parkings[vehicle_id] = {
            "entry_time": datetime.now(),
            "floor": floor,
            "is_paid": False
        }
        return True

    def get_payment_info(self, country: str, registration_no: str) -> Dict[str, Any]:
        vehicle_id = f"{country}_{registration_no}"
        if vehicle_id not in self.active_parkings:
            raise ValueError("Vehicle not found on parking")

        entry_data = self.active_parkings[vehicle_id]

        duration = datetime.now() - entry_data["entry_time"]
        minutes = int(duration.total_seconds() / 60)

        fee = self.price_calculator.calculate_fee(minutes, entry_data["floor"])

        return {"country": country, "registration_no": registration_no, "fee": fee, "minutes": minutes}

    def pay_parking_fee(self, country: str, registration_no: str, amount: float) -> Dict[str, Any]:
        payment_info = self.get_payment_info(country, registration_no)
        required_fee = payment_info["fee"]

        if amount < payment_info["fee"]:
            raise ValueError(f"Insufficient amount. Required: {required_fee} PLN")

        change = round(amount - required_fee, 2)

        vehicle_id = f"{country}_{registration_no}"
        self.active_parkings[vehicle_id]["is_paid"] = True

        return {
            "status": True,
            "required_fee": required_fee,
            "paid_amount": amount,
            "change": change
        }


    def register_exit(self, country: str, registration_no: str) -> bool:
        vehicle_id = f"{country}_{registration_no}"
        fee = self.get_payment_info(country, registration_no)["fee"]
        entry_time = self.active_parkings[vehicle_id]["entry_time"]
        floor = self.active_parkings[vehicle_id]["floor"]

        if not self.active_parkings[vehicle_id]["is_paid"]:
            raise ValueError("Parking fee not paid")

        self.history[vehicle_id].append({
            "entry_time": entry_time,
            "exit_time": datetime.now(),
            "floor": floor,
            "fee": fee
        })

        del self.active_parkings[vehicle_id]
        return True

    def change_vehicle_floor(self, country: str, registration_no: str, new_floor: int) -> bool:
        vehicle_id = f"{country}_{registration_no}"
        if vehicle_id not in self.active_parkings:
            raise ValueError("Vehicle not found on parking")
        if new_floor not in self.price_calculator.prices:
            raise ValueError(f"Floor {new_floor} is not available in this parking")

        self.active_parkings[vehicle_id]["floor"] = new_floor
        return True
