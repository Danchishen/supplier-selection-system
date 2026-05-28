"""Default input data for the supplier selection demo."""

DEFAULT_CUSTOMER = {
    "name": "TechnoSbornka Moscow",
    "address": "Moscow, Logisticheskaya st., 1",
    "lat": 55.7558,
    "lon": 37.6173,
    "acceptance_window": "Mon-Fri, 08:00-20:00",
}

DEFAULT_GLOBALS = {
    "capacity_m3": 85.0,
    "capacity_kg": 20_000.0,
    "budget_rub": 250_000.0,
    "max_cost_per_km": 50.0,
    "max_time_days": 2.0,
    "require_tracking": True,
    # none | separate | composite
    "reliability_filter_mode": "none",
    "min_manufacturer_reliability": 95.0,
    "min_carrier_reliability": 95.0,
    "min_composite_reliability": 95.0,
}

DEFAULT_WEIGHT_CONFIG = {
    "method": "variance",
    "ahp_cost_time": 3.0,
    "ahp_cost_reliability": 0.3333,
    "ahp_cost_distance": 2.0,
    "ahp_time_reliability": 0.25,
    "ahp_time_distance": 1.0,
    "ahp_reliability_distance": 3.0,
}

CRITERIA_LABELS = ["Стоимость", "Время", "Надёжность", "Дистанция"]

DEFAULT_FACTORIES = [
    {
        "manufacturer": "ElectroMotor",
        "product": "Motor",
        "city": "Nizhny Novgorod",
        "address": "Promyshlennaya st., 15",
        "lat": 56.2965,
        "lon": 43.9361,
        "distance_km": 420.0,
        "transport_time_days": 0.5,
        "weekly_quantity_units": 1000.0,
        "unit_weight_kg": 5.0,
        "unit_volume_m3": 0.03,
        "manufacturer_reliability": 98.0,
        "purchase_price_per_unit": 2500.0,
        "shipping_window": "Mon-Fri, 09:00-17:00",
    },
    {
        "manufacturer": "KholodTech",
        "product": "Compressor",
        "city": "Kazan",
        "address": "Zavodskoy ave., 42",
        "lat": 55.8304,
        "lon": 49.0661,
        "distance_km": 820.0,
        "transport_time_days": 1.0,
        "weekly_quantity_units": 800.0,
        "unit_weight_kg": 12.0,
        "unit_volume_m3": 0.15,
        "manufacturer_reliability": 97.0,
        "purchase_price_per_unit": 4200.0,
        "shipping_window": "Tue-Sat, 08:00-16:00",
    },
    {
        "manufacturer": "PlastikProm",
        "product": "Panel",
        "city": "Yekaterinburg",
        "address": "Metallurgov st., 78",
        "lat": 56.8389,
        "lon": 60.6057,
        "distance_km": 1800.0,
        "transport_time_days": 2.0,
        "weekly_quantity_units": 2000.0,
        "unit_weight_kg": 3.0,
        "unit_volume_m3": 0.20,
        "manufacturer_reliability": 96.0,
        "purchase_price_per_unit": 1200.0,
        "shipping_window": "Mon-Fri, 10:00-18:00",
    },
]

DEFAULT_CARRIERS = [
    {
        "name": "TransLogist",
        "base_city": "Nizhny Novgorod",
        "cost_per_km": 45.0,
        "reliability": 98.0,
        "tracking": True,
        "speed_kmh": 80.0,
    },
    {
        "name": "UralTrans",
        "base_city": "Yekaterinburg",
        "cost_per_km": 48.0,
        "reliability": 96.0,
        "tracking": True,
        "speed_kmh": 80.0,
    },
    {
        "name": "CenterGruz",
        "base_city": "Moscow",
        "cost_per_km": 50.0,
        "reliability": 97.0,
        "tracking": True,
        "speed_kmh": 80.0,
    },
]

FACTORY_FIELDS = [
    "manufacturer",
    "product",
    "city",
    "address",
    "lat",
    "lon",
    "distance_km",
    "transport_time_days",
    "weekly_quantity_units",
    "unit_weight_kg",
    "unit_volume_m3",
    "manufacturer_reliability",
    "purchase_price_per_unit",
    "shipping_window",
]

CARRIER_FIELDS = [
    "name",
    "base_city",
    "cost_per_km",
    "reliability",
    "tracking",
    "speed_kmh",
]
