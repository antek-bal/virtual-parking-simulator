class PriceCalculator:
    def __init__(self, prices: dict):
        self.prices = prices

    def calculate_fee(self, minutes: int, floor: int) -> float:
        if not isinstance(minutes, int):
            raise TypeError("Minutes must be an integer")

        if minutes < 0:
            raise ValueError("Time can't be negative")

        if floor not in self.prices:
            raise ValueError(f"Floor {floor} not in price list")

        if minutes <= 30:
            return 0.0

        price_per_minute = self.prices[floor] / 60
        billable_minutes = minutes - 30

        fee = billable_minutes * price_per_minute
        return round(fee, 2)