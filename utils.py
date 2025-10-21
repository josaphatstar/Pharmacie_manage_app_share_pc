"""Utility functions for validation and formatting."""
from __future__ import annotations

from datetime import date, datetime
from typing import Tuple, Optional


def normalize_date(value: date | str) -> str:
    """Return ISO date (YYYY-MM-DD) from a date or string (already ISO)."""
    if isinstance(value, date):
        return value.isoformat()
    # Expect 'YYYY-MM-DD'
    # Validate format loosely and return as-is (detailed validation elsewhere)
    try:
        dt = datetime.strptime(value, "%Y-%m-%d").date()
        return dt.isoformat()
    except Exception:
        # Return original, validator will catch
        return str(value)


def validate_quantity(qty: int | float | str) -> Tuple[bool, Optional[int], str]:
    """Validate quantity as a non-negative integer.

    Returns (is_valid, normalized_quantity, error_message)
    """
    try:
        if isinstance(qty, str):
            qty = qty.strip()
            if qty == "":
                return False, None, "La quantité est requise."
            iv = int(qty)
        elif isinstance(qty, float):
            if int(qty) != qty:
                return False, None, "La quantité doit être un entier."
            iv = int(qty)
        else:
            iv = int(qty)
    except Exception:
        return False, None, "La quantité doit être un entier."

    if iv < 1:
        return False, None, "La quantité doit être au minimum de 1."
    return True, iv, ""


def validate_expiry_date(d: date | str) -> Tuple[bool, Optional[str], str]:
    """Validate expiry date is a real date and not in the past.

    Returns (is_valid, iso_date, error_message)
    """
    try:
        if isinstance(d, str):
            dt = datetime.strptime(d, "%Y-%m-%d").date()
        else:
            dt = d
    except Exception:
        return False, None, "La date d'expiration est invalide (format attendu AAAA-MM-JJ)."

    today = date.today()
    if dt <= today:
        return False, None, "La date d'expiration ne peut pas être dans le passé ou aujourd'hui."

    return True, dt.isoformat(), ""


__all__ = [
    "normalize_date",
    "validate_quantity",
    "validate_expiry_date",
]
