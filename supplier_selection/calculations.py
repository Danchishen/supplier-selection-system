"""Calculation core for supplier selection."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from .data import CRITERIA_LABELS, DEFAULT_WEIGHT_CONFIG


def weekly_volume(factory: dict[str, Any]) -> float:
    return factory["weekly_quantity_units"] * factory["unit_volume_m3"]


def weekly_weight(factory: dict[str, Any]) -> float:
    return factory["weekly_quantity_units"] * factory["unit_weight_kg"]


def trucks_required(factory: dict[str, Any], globals_cfg: dict[str, Any]) -> int:
    by_volume = weekly_volume(factory) / globals_cfg["capacity_m3"]
    by_weight = weekly_weight(factory) / globals_cfg["capacity_kg"]
    return math.ceil(max(by_volume, by_weight))


def alx_weekly_transport_cost(
    factory: dict[str, Any], carrier: dict[str, Any], globals_cfg: dict[str, Any]
) -> float:
    return (
        carrier["cost_per_km"]
        / globals_cfg["capacity_m3"]
        * weekly_volume(factory)
        * factory["distance_km"]
    )


def full_truck_reference_cost(
    factory: dict[str, Any], carrier: dict[str, Any], globals_cfg: dict[str, Any]
) -> float:
    return carrier["cost_per_km"] * factory["distance_km"] * trucks_required(factory, globals_cfg)


def composite_reliability(factory: dict[str, Any], carrier: dict[str, Any]) -> float:
    return round(factory["manufacturer_reliability"] * carrier["reliability"] / 100.0, 2)


def is_time_feasible(factory: dict[str, Any], globals_cfg: dict[str, Any]) -> bool:
    return factory["transport_time_days"] <= globals_cfg["max_time_days"]


def is_candidate_allowed(
    factory: dict[str, Any], carrier: dict[str, Any], globals_cfg: dict[str, Any]
) -> bool:
    if globals_cfg["require_tracking"] and not carrier["tracking"]:
        return False
    if carrier["cost_per_km"] > globals_cfg["max_cost_per_km"]:
        return False
    if not is_time_feasible(factory, globals_cfg):
        return False

    mode = globals_cfg["reliability_filter_mode"]
    if mode == "separate":
        return (
            factory["manufacturer_reliability"] >= globals_cfg["min_manufacturer_reliability"]
            and carrier["reliability"] >= globals_cfg["min_carrier_reliability"]
        )
    if mode == "composite":
        return composite_reliability(factory, carrier) >= globals_cfg["min_composite_reliability"]
    return True


def get_criteria_matrix(rows: list[dict[str, Any]]) -> list[list[float]]:
    return [
        [
            r["alx_transport_cost_rub"],
            r["time_days"],
            r["composite_reliability"],
            r["distance_km"],
        ]
        for r in rows
    ]


def variance_weights(rows: list[dict[str, Any]]) -> list[float]:
    if not rows:
        return [0.25, 0.25, 0.25, 0.25]

    matrix = get_criteria_matrix(rows)
    variances = []
    for j in range(4):
        col = [row[j] for row in matrix]
        mean = sum(col) / len(col)
        variances.append(sum((x - mean) ** 2 for x in col) / len(col))

    total = sum(variances)
    if total == 0:
        return [0.25, 0.25, 0.25, 0.25]
    return [v / total for v in variances]


def entropy_weights(rows: list[dict[str, Any]]) -> list[float]:
    if not rows:
        return [0.25, 0.25, 0.25, 0.25]

    matrix = get_criteria_matrix(rows)
    n = len(matrix)
    if n == 1:
        return [0.25, 0.25, 0.25, 0.25]

    transformed = [[0.0] * 4 for _ in range(n)]
    for j in range(4):
        col = [row[j] for row in matrix]
        cmin = min(col)
        cmax = max(col)
        span = cmax - cmin
        for i, val in enumerate(col):
            if span == 0:
                score = 1.0
            elif j in (0, 1, 3):  # cost, time, distance -> minimize
                score = (cmax - val) / span
            else:  # reliability -> maximize
                score = (val - cmin) / span
            transformed[i][j] = score + 1e-12

    k = 1.0 / math.log(n)
    diversities = []
    for j in range(4):
        col_sum = sum(transformed[i][j] for i in range(n))
        probs = [transformed[i][j] / col_sum for i in range(n)]
        entropy = -k * sum(p * math.log(p) for p in probs if p > 0)
        diversities.append(1 - entropy)

    total = sum(diversities)
    if total <= 1e-12:
        return [0.25, 0.25, 0.25, 0.25]
    return [d / total for d in diversities]


def to_float(value: Any, default: float = 0.0) -> float:
    if value is None or str(value).strip() == "":
        return default
    return float(str(value).replace(",", ".").strip())


def ahp_weights_from_mapping(values: dict[str, Any] | None) -> tuple[list[float], dict[str, float]]:
    values = values or {}
    vals = {
        "ct": max(to_float(values.get("ahp_cost_time"), DEFAULT_WEIGHT_CONFIG["ahp_cost_time"]), 1e-9),
        "cr": max(to_float(values.get("ahp_cost_reliability"), DEFAULT_WEIGHT_CONFIG["ahp_cost_reliability"]), 1e-9),
        "cd": max(to_float(values.get("ahp_cost_distance"), DEFAULT_WEIGHT_CONFIG["ahp_cost_distance"]), 1e-9),
        "tr": max(to_float(values.get("ahp_time_reliability"), DEFAULT_WEIGHT_CONFIG["ahp_time_reliability"]), 1e-9),
        "td": max(to_float(values.get("ahp_time_distance"), DEFAULT_WEIGHT_CONFIG["ahp_time_distance"]), 1e-9),
        "rd": max(to_float(values.get("ahp_reliability_distance"), DEFAULT_WEIGHT_CONFIG["ahp_reliability_distance"]), 1e-9),
    }

    matrix = [
        [1.0, vals["ct"], vals["cr"], vals["cd"]],
        [1.0 / vals["ct"], 1.0, vals["tr"], vals["td"]],
        [1.0 / vals["cr"], 1.0 / vals["tr"], 1.0, vals["rd"]],
        [1.0 / vals["cd"], 1.0 / vals["td"], 1.0 / vals["rd"], 1.0],
    ]

    geometric_means = []
    for row in matrix:
        product = 1.0
        for item in row:
            product *= item
        geometric_means.append(product ** (1 / len(row)))

    total = sum(geometric_means)
    weights = [g / total for g in geometric_means]

    aw = [sum(matrix[i][j] * weights[j] for j in range(4)) for i in range(4)]
    lambda_max = sum(aw[i] / weights[i] for i in range(4)) / 4.0
    ci = (lambda_max - 4.0) / 3.0
    ri = 0.90
    cr = ci / ri if ri > 0 else 0.0

    return weights, {"lambda_max": lambda_max, "ci": ci, "cr": cr}


def topsis(rows: list[dict[str, Any]], weights: list[float]) -> list[dict[str, Any]]:
    if not rows:
        return []

    matrix = get_criteria_matrix(rows)
    impacts = ["-", "-", "+", "-"]
    denoms = [math.sqrt(sum(row[j] ** 2 for row in matrix)) or 1.0 for j in range(4)]

    weighted = []
    for row in matrix:
        weighted.append([(row[j] / denoms[j]) * weights[j] for j in range(4)])

    best, worst = [], []
    for j in range(4):
        col = [row[j] for row in weighted]
        if impacts[j] == "+":
            best.append(max(col))
            worst.append(min(col))
        else:
            best.append(min(col))
            worst.append(max(col))

    scores = []
    for i, row in enumerate(weighted):
        d_best = math.sqrt(sum((row[j] - best[j]) ** 2 for j in range(4)))
        d_worst = math.sqrt(sum((row[j] - worst[j]) ** 2 for j in range(4)))
        score = d_worst / (d_best + d_worst + 1e-9)
        enriched = dict(rows[i])
        enriched["score"] = round(score, 4)
        scores.append(enriched)
    return scores


def build_supplier_options(
    customer: dict[str, Any],
    factories: list[dict[str, Any]],
    carriers: list[dict[str, Any]],
    globals_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for factory in factories:
        for carrier in carriers:
            rows.append(
                {
                    "supplier_name": f"{factory['manufacturer']} + {carrier['name']}",
                    "manufacturer": factory["manufacturer"],
                    "product": factory["product"],
                    "carrier": carrier["name"],
                    "factory_city": factory["city"],
                    "factory_address": factory["address"],
                    "factory_lat": factory["lat"],
                    "factory_lon": factory["lon"],
                    "customer_name": customer["name"],
                    "distance_km": factory["distance_km"],
                    "time_days": factory["transport_time_days"],
                    "weekly_quantity_units": factory["weekly_quantity_units"],
                    "weekly_volume_m3": weekly_volume(factory),
                    "weekly_weight_kg": weekly_weight(factory),
                    "trucks_required": trucks_required(factory, globals_cfg),
                    "carrier_cost_per_km": carrier["cost_per_km"],
                    "alx_transport_cost_rub": alx_weekly_transport_cost(factory, carrier, globals_cfg),
                    "full_truck_cost_rub": full_truck_reference_cost(factory, carrier, globals_cfg),
                    "manufacturer_reliability": factory["manufacturer_reliability"],
                    "carrier_reliability": carrier["reliability"],
                    "composite_reliability": composite_reliability(factory, carrier),
                    "tracking": carrier["tracking"],
                    "allowed": is_candidate_allowed(factory, carrier, globals_cfg),
                }
            )
    return rows


def build_ranked_results(
    customer: dict[str, Any],
    factories: list[dict[str, Any]],
    carriers: list[dict[str, Any]],
    globals_cfg: dict[str, Any],
    weight_method: str = "variance",
    weight_values: dict[str, Any] | None = None,
) -> dict[str, Any]:
    all_rows = build_supplier_options(customer, factories, carriers, globals_cfg)
    allowed_rows = [r for r in all_rows if r["allowed"]]

    ahp_info = None
    if weight_method == "entropy":
        weights = entropy_weights(allowed_rows)
    elif weight_method == "ahp":
        weights, ahp_info = ahp_weights_from_mapping(weight_values)
    else:
        weight_method = "variance"
        weights = variance_weights(allowed_rows)

    scored = topsis(allowed_rows, weights)
    grouped = defaultdict(list)
    for row in scored:
        grouped[row["product"]].append(row)
    for product in grouped:
        grouped[product].sort(key=lambda x: x["score"], reverse=True)

    ordered_products = []
    seen = set()
    for factory in factories:
        if factory["product"] not in seen:
            ordered_products.append(factory["product"])
            seen.add(factory["product"])

    best_plan = []
    missing_products = []
    for product in ordered_products:
        if grouped.get(product):
            best_plan.append(grouped[product][0])
        else:
            missing_products.append(product)

    total_cost = sum(r["alx_transport_cost_rub"] for r in best_plan)
    total_full_truck_cost = sum(r["full_truck_cost_rub"] for r in best_plan)
    total_trucks = sum(r["trucks_required"] for r in best_plan)
    total_volume = sum(r["weekly_volume_m3"] for r in best_plan)

    return {
        "weight_method": weight_method,
        "weights": weights,
        "weight_labels": CRITERIA_LABELS,
        "weight_pairs": list(zip(CRITERIA_LABELS, weights)),
        "ahp_info": ahp_info,
        "all_rows": all_rows,
        "allowed_rows": allowed_rows,
        "ranked": dict(grouped),
        "best_plan": best_plan,
        "missing_products": missing_products,
        "summary": {
            "total_cost_rub": round(total_cost, 2),
            "total_full_truck_cost_rub": round(total_full_truck_cost, 2),
            "total_trucks": total_trucks,
            "total_volume_m3": round(total_volume, 2),
            "budget_rub": globals_cfg["budget_rub"],
            "budget_ok": total_cost <= globals_cfg["budget_rub"],
        },
    }


def map_payload(
    customer: dict[str, Any], factories: list[dict[str, Any]], best_plan: list[dict[str, Any]] | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    factories_map = [
        {
            "name": factory["manufacturer"],
            "product": factory["product"],
            "lat": factory["lat"],
            "lon": factory["lon"],
            "city": factory["city"],
        }
        for factory in factories
    ]
    routes = []
    for row in best_plan or []:
        routes.append(
            {
                "supplier_name": row["supplier_name"],
                "product": row["product"],
                "from_lat": row["factory_lat"],
                "from_lon": row["factory_lon"],
                "to_lat": customer["lat"],
                "to_lon": customer["lon"],
            }
        )
    return factories_map, routes
