"""Flask entry point for the supplier selection system."""
from __future__ import annotations

import json
import os

from flask import Flask, render_template, request, send_file

from supplier_selection.calculations import build_ranked_results, map_payload, weekly_volume, weekly_weight
from supplier_selection.data import DEFAULT_CARRIERS, DEFAULT_CUSTOMER, DEFAULT_FACTORIES, DEFAULT_GLOBALS, DEFAULT_WEIGHT_CONFIG
from supplier_selection.forms import carriers_from_form, customer_from_form, factories_from_form, globals_from_form, weight_config_from_form
from supplier_selection.import_export import generate_template_xlsx, read_tabular_file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "thesis-form-import")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")


def _default_state():
    customer = DEFAULT_CUSTOMER.copy()
    globals_cfg = DEFAULT_GLOBALS.copy()
    weight_cfg = DEFAULT_WEIGHT_CONFIG.copy()
    factories = [dict(item) for item in DEFAULT_FACTORIES]
    carriers = [dict(item) for item in DEFAULT_CARRIERS]
    return customer, factories, carriers, globals_cfg, weight_cfg


def render_page(customer, factories, carriers, globals_cfg, results, weight_cfg, error=None):
    factories_map, routes_map = map_payload(customer, factories, results["best_plan"] if results else [])
    factories_view = [
        {**factory, "weekly_volume_m3": weekly_volume(factory), "weekly_weight_kg": weekly_weight(factory)}
        for factory in factories
    ]
    return render_template(
        "index.html",
        api_key=YANDEX_API_KEY,
        customer=customer,
        customer_map=json.dumps(customer, ensure_ascii=False),
        globals_cfg=globals_cfg,
        factories=factories_view,
        carriers=carriers,
        factories_map=json.dumps(factories_map, ensure_ascii=False),
        routes_map=json.dumps(routes_map, ensure_ascii=False),
        results=results,
        weight_cfg=weight_cfg,
        error=error,
    )


@app.route("/", methods=["GET"])
def index():
    customer, factories, carriers, globals_cfg, weight_cfg = _default_state()
    results = build_ranked_results(customer, factories, carriers, globals_cfg, weight_cfg["method"], weight_cfg)
    return render_page(customer, factories, carriers, globals_cfg, results, weight_cfg)


@app.route("/download_template", methods=["GET"])
def download_template():
    output = generate_template_xlsx()
    return send_file(
        output,
        as_attachment=True,
        download_name="supplier_system_template.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/calc", methods=["POST"])
def calc():
    if request.form.get("load_defaults") == "1":
        customer, factories, carriers, globals_cfg, weight_cfg = _default_state()
        results = build_ranked_results(customer, factories, carriers, globals_cfg, weight_cfg["method"], weight_cfg)
        return render_page(customer, factories, carriers, globals_cfg, results, weight_cfg)

    customer = customer_from_form(request.form)
    globals_cfg = globals_from_form(request.form)
    weight_cfg = weight_config_from_form(request.form)

    try:
        factories = factories_from_form(request.form)
        carriers = carriers_from_form(request.form)

        factories_file = request.files.get("factories_file")
        carriers_file = request.files.get("carriers_file")

        if factories_file and factories_file.filename:
            factories = read_tabular_file(factories_file, "factories")
        if carriers_file and carriers_file.filename:
            carriers = read_tabular_file(carriers_file, "carriers")

        if not factories:
            raise ValueError("Нужен хотя бы один завод.")
        if not carriers:
            raise ValueError("Нужна хотя бы одна транспортная компания.")

        results = build_ranked_results(
            customer, factories, carriers, globals_cfg, weight_cfg["method"], weight_cfg
        )
        return render_page(customer, factories, carriers, globals_cfg, results, weight_cfg)
    except Exception as exc:  # noqa: BLE001 - show validation errors in UI
        fallback_customer, fallback_factories, fallback_carriers, fallback_globals, fallback_weights = _default_state()
        results = build_ranked_results(
            fallback_customer,
            fallback_factories,
            fallback_carriers,
            fallback_globals,
            fallback_weights["method"],
            fallback_weights,
        )
        return render_page(customer, fallback_factories, fallback_carriers, globals_cfg, results, weight_cfg, f"Ошибка обработки данных: {exc}")


if __name__ == "__main__":
    app.run(debug=True)
