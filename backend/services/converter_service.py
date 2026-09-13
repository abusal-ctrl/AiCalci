"""
Converter service — units + live currency (with fallback snapshot).
"""
import time
import json
import os

# ============ UNIT TABLES ============
LENGTH_TO_M = {"m":1, "km":1000, "cm":0.01, "mm":0.001, "mi":1609.344, "yd":0.9144, "ft":0.3048, "in":0.0254}
MASS_TO_KG  = {"kg":1, "g":0.001, "mg":1e-6, "lb":0.45359237, "oz":0.028349523125, "t":1000}
TIME_TO_S   = {"s":1, "min":60, "h":3600, "day":86400, "week":604800}
AREA_TO_M2  = {"m2":1, "km2":1e6, "cm2":1e-4, "ft2":0.09290304, "in2":0.00064516, "acre":4046.8564224, "ha":10000}
VOLUME_TO_L = {"L":1, "mL":0.001, "m3":1000, "cm3":0.001, "gal":3.785411784, "qt":0.946352946, "pt":0.473176473, "cup":0.2365882365, "floz":0.0295735296}
SPEED_TO_MS = {"m/s":1, "km/h":1/3.6, "mph":0.44704, "knot":0.514444, "ft/s":0.3048}

# ============ CURRENCY (fallback snapshot) ============
_FALLBACK_CURRENCY_TO_USD = {
    "USD": 1.0, "EUR": 1.08, "GBP": 1.27, "INR": 0.012,
    "JPY": 0.0067, "AUD": 0.66, "CAD": 0.73, "CHF": 1.13, "CNY": 0.14,
}

_rates_cache = {"data": None, "ts": 0}
CACHE_TTL = 3600  # seconds


def _fetch_live_rates():
    """Fetch USD-based rates from a free API. Falls back to snapshot on failure."""
    now = time.time()
    if _rates_cache["data"] and now - _rates_cache["ts"] < CACHE_TTL:
        return _rates_cache["data"]

    try:
        import urllib.request
        url = "https://open.er-api.com/v6/latest/USD"
        with urllib.request.urlopen(url, timeout=4) as resp:
            data = json.loads(resp.read().decode())
        rates = data.get("rates", {})
        # Keep only the currencies our UI offers
        filtered = {k: rates[k] for k in _FALLBACK_CURRENCY_TO_USD if k in rates}
        if filtered:
            filtered["USD"] = 1.0
            _rates_cache["data"] = filtered
            _rates_cache["ts"] = now
            return filtered
    except Exception as e:
        print(f"[converter] live rates unavailable, using snapshot: {e}")

    return _FALLBACK_CURRENCY_TO_USD


def _convert_temperature(value, frm, to):
    if frm == "C":   c = value
    elif frm == "F": c = (value - 32) * 5/9
    elif frm == "K": c = value - 273.15
    else:            raise ValueError(f"Unknown temperature unit: {frm}")
    if to == "C":   return c
    if to == "F":   return c * 9/5 + 32
    if to == "K":   return c + 273.15
    raise ValueError(f"Unknown temperature unit: {to}")


def _linear(value, frm, to, table):
    if frm not in table or to not in table:
        raise ValueError(f"Unknown unit: {frm} or {to}")
    return value * table[frm] / table[to]


def convert(category, value, frm, to):
    if category == "length":      return _linear(value, frm, to, LENGTH_TO_M)
    if category == "mass":        return _linear(value, frm, to, MASS_TO_KG)
    if category == "time":        return _linear(value, frm, to, TIME_TO_S)
    if category == "area":        return _linear(value, frm, to, AREA_TO_M2)
    if category == "volume":      return _linear(value, frm, to, VOLUME_TO_L)
    if category == "speed":       return _linear(value, frm, to, SPEED_TO_MS)
    if category == "temperature": return _convert_temperature(value, frm, to)
    if category == "currency":
        rates = _fetch_live_rates()
        if frm not in rates or to not in rates:
            raise ValueError(f"Unknown currency: {frm} or {to}")
        return value / rates[frm] * rates[to]
    raise ValueError(f"Unknown category: {category}")