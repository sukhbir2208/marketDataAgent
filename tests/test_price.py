import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import PriceRequest, _fetch_price


def test_price_request_validation():
    with pytest.raises(ValueError):
        PriceRequest(symbol="invalid$")


def test_fetch_price_invalid_symbol():
    assert _fetch_price("ZZZZ") is None
