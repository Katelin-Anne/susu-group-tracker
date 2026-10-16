"""Exact money parsing and formatting using integer pesewas (100 per GHS)."""
from decimal import Decimal, InvalidOperation


class MoneyError(ValueError):
    """Raised when a money value is invalid or has more than two decimals."""


def to_pesewas(value: str | int | Decimal) -> int:
    """Convert a GHS amount to integer pesewas without floating-point math."""
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise MoneyError("Enter a valid money amount, e.g. 50.00.") from exc
    if not amount.is_finite():
        raise MoneyError("Money amount must be a finite number.")
    if amount.as_tuple().exponent < -2:
        raise MoneyError("Money amounts may have at most two decimal places.")
    pesewas = amount * 100
    if pesewas != pesewas.to_integral_value():
        raise MoneyError("Money amounts may have at most two decimal places.")
    return int(pesewas)


def format_ghs(pesewas: int) -> str:
    """Format integer pesewas as a two-decimal GHS amount."""
    sign = "-" if pesewas < 0 else ""
    absolute = abs(pesewas)
    return f"{sign}GHS {absolute // 100}.{absolute % 100:02d}"
