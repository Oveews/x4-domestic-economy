"""Offline balance model; this does not emulate the X4 scripting engine."""
from fractions import Fraction


def consume(stock: int, carry: Fraction, rate: int, seconds: int):
    due = carry + Fraction(rate * seconds, 3600)
    whole = int(due)
    # Unmet demand expires. A blockade must not create unlimited deferred demand.
    return stock - min(stock, whole), due - whole, min(stock, whole)


def available_order(stock: int, target: int, reserved: int):
    return max(0, target - stock - reserved)


def price_fraction(stock: int, target: int):
    """Fraction between vanilla min/max prices, decreasing with stock."""
    fill = min(Fraction(stock, target), 1)
    return Fraction(1, 5) + Fraction(3, 5) * (1 - fill)
