"""Request parsing helpers for Flask forms."""
from __future__ import annotations

from typing import Any

from .calculations import to_float
from .data import CARRIER_FIELDS, DEFAULT_CUSTOMER, DEFAULT_GLOBALS, DEFAULT_WEIGHT_CONFIG, FACTORY_FIELDS


def bool_from_str(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "да", "y", "on"}


def weight_method_from_form(form: Any) -> str:
    method = form.get("weight_method", DEFAULT_WEIGHT_CONFIG["method"])
    return method if method in {"variance", "entropy", "ahp"} else "variance"


def customer_from_form(form: Any) -> dict[str, Any]:
    return {
        "name": form.get("customer_name", DEFAULT_CUSTOMER["name"]).strip(),
        "address": form.get("customer_address", DEFAULT_CUSTOMER["address"]).strip(),
        "lat": to_float(form.get("customer_lat"), DEFAULT_CUSTOMER["lat"]),
        "lon": to_float(form.get("customer_lon"), DEFAULT_CUSTOMER["lon"]),
        "acceptance_window": form.get(
            "customer_acceptance_window", DEFAULT_CUSTOMER["acceptance_window"]
        ).strip(),
    }


def globals_from_form(form: Any) -> dict[str, Any]:
    return {
        "capacity_m3": to_float(form.get("capacity_m3"), DEFAULT_GLOBALS["capacity_m3"]),
        "capacity_kg": to_float(form.get("capacity_kg"), DEFAULT_GLOBALS["capacity_kg"]),
        "budget_rub": to_float(form.get("budget_rub"), DEFAULT_GLOBALS["budget_rub"]),
        "max_cost_per_km": to_float(form.get("max_cost_per_km"), DEFAULT_GLOBALS["max_cost_per_km"]),
        "max_time_days": to_float(form.get("max_time_days"), DEFAULT_GLOBALS["max_time_days"]),
        "require_tracking": "require_tracking" in form,
        "reliability_filter_mode": form.get(
            "reliability_filter_mode", DEFAULT_GLOBALS["reliability_filter_mode"]
        ),
        "min_manufacturer_reliability": to_float(
            form.get("min_manufacturer_reliability"), DEFAULT_GLOBALS["min_manufacturer_reliability"]
        ),
        "min_carrier_reliability": to_float(
            form.get("min_carrier_reliability"), DEFAULT_GLOBALS["min_carrier_reliability"]
        ),
        "min_composite_reliability": to_float(
            form.get("min_composite_reliability"), DEFAULT_GLOBALS["min_composite_reliability"]
        ),
    }


def weight_config_from_form(form: Any) -> dict[str, Any]:
    return {
        "method": weight_method_from_form(form),
        "ahp_cost_time": to_float(form.get("ahp_cost_time"), DEFAULT_WEIGHT_CONFIG["ahp_cost_time"]),
        "ahp_cost_reliability": to_float(
            form.get("ahp_cost_reliability"), DEFAULT_WEIGHT_CONFIG["ahp_cost_reliability"]
        ),
        "ahp_cost_distance": to_float(
            form.get("ahp_cost_distance"), DEFAULT_WEIGHT_CONFIG["ahp_cost_distance"]
        ),
        "ahp_time_reliability": to_float(
            form.get("ahp_time_reliability"), DEFAULT_WEIGHT_CONFIG["ahp_time_reliability"]
        ),
        "ahp_time_distance": to_float(
            form.get("ahp_time_distance"), DEFAULT_WEIGHT_CONFIG["ahp_time_distance"]
        ),
        "ahp_reliability_distance": to_float(
            form.get("ahp_reliability_distance"), DEFAULT_WEIGHT_CONFIG["ahp_reliability_distance"]
        ),
    }


def factories_from_form(form: Any) -> list[dict[str, Any]]:
    cols = {field: form.getlist(f"factory_{field}[]") for field in FACTORY_FIELDS}
    max_len = max((len(value) for value in cols.values()), default=0)
    rows = []

    for i in range(max_len):
        manufacturer = cols["manufacturer"][i].strip() if i < len(cols["manufacturer"]) else ""
        product = cols["product"][i].strip() if i < len(cols["product"]) else ""
        if not manufacturer and not product:
            continue
        rows.append(
            {
                "manufacturer": manufacturer,
                "product": product,
                "city": cols["city"][i].strip() if i < len(cols["city"]) else "",
                "address": cols["address"][i].strip() if i < len(cols["address"]) else "",
                "lat": to_float(cols["lat"][i]) if i < len(cols["lat"]) else 0.0,
                "lon": to_float(cols["lon"][i]) if i < len(cols["lon"]) else 0.0,
                "distance_km": to_float(cols["distance_km"][i]) if i < len(cols["distance_km"]) else 0.0,
                "transport_time_days": to_float(cols["transport_time_days"][i])
                if i < len(cols["transport_time_days"])
                else 0.0,
                "weekly_quantity_units": to_float(cols["weekly_quantity_units"][i])
                if i < len(cols["weekly_quantity_units"])
                else 0.0,
                "unit_weight_kg": to_float(cols["unit_weight_kg"][i])
                if i < len(cols["unit_weight_kg"])
                else 0.0,
                "unit_volume_m3": to_float(cols["unit_volume_m3"][i])
                if i < len(cols["unit_volume_m3"])
                else 0.0,
                "manufacturer_reliability": to_float(cols["manufacturer_reliability"][i])
                if i < len(cols["manufacturer_reliability"])
                else 0.0,
                "purchase_price_per_unit": to_float(cols["purchase_price_per_unit"][i])
                if i < len(cols["purchase_price_per_unit"])
                else 0.0,
                "shipping_window": cols["shipping_window"][i].strip()
                if i < len(cols["shipping_window"])
                else "",
            }
        )
    return rows


def carriers_from_form(form: Any) -> list[dict[str, Any]]:
    cols = {field: form.getlist(f"carrier_{field}[]") for field in CARRIER_FIELDS}
    max_len = max((len(value) for value in cols.values()), default=0)
    rows = []

    for i in range(max_len):
        name = cols["name"][i].strip() if i < len(cols["name"]) else ""
        if not name:
            continue
        rows.append(
            {
                "name": name,
                "base_city": cols["base_city"][i].strip() if i < len(cols["base_city"]) else "",
                "cost_per_km": to_float(cols["cost_per_km"][i]) if i < len(cols["cost_per_km"]) else 0.0,
                "reliability": to_float(cols["reliability"][i]) if i < len(cols["reliability"]) else 0.0,
                "tracking": bool_from_str(cols["tracking"][i]) if i < len(cols["tracking"]) else False,
                "speed_kmh": to_float(cols["speed_kmh"][i], 80.0) if i < len(cols["speed_kmh"]) else 80.0,
            }
        )
    return rows
