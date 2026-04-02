from decimal import Decimal

def calculate_line_total(quantity: int, unit_price: Decimal, rate_percentage: Decimal | None):
    
    base = Decimal(quantity) * Decimal(unit_price)

    if rate_percentage is None:
        return base.quantize(Decimal("0.01"))

    multiplier = (Decimal("100") + Decimal(rate_percentage)) / Decimal("100")
    return (base * multiplier).quantize(Decimal("0.01"))
