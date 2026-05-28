"""Import/export helpers for CSV, XLSX and XLS files."""
from __future__ import annotations

import io
from typing import Any

import pandas as pd

from .calculations import to_float
from .data import CARRIER_FIELDS, DEFAULT_CARRIERS, DEFAULT_FACTORIES, FACTORY_FIELDS
from .forms import bool_from_str


def _columns_by_lowercase(df: pd.DataFrame) -> dict[str, str]:
    return {str(column).lower().strip(): column for column in df.columns}


def _read_cell(row: pd.Series, column: str, default: str = "") -> Any:
    value = row[column]
    if pd.isna(value):
        return default
    return value


def df_to_factories(df: pd.DataFrame) -> list[dict[str, Any]]:
    rename = _columns_by_lowercase(df)
    missing = [column for column in FACTORY_FIELDS if column not in rename]
    if missing:
        raise ValueError("В файле заводов не хватает колонок: " + ", ".join(missing))

    records = []
    for _, row in df.iterrows():
        manufacturer = str(_read_cell(row, rename["manufacturer"])).strip()
        product = str(_read_cell(row, rename["product"])).strip()
        if not manufacturer and not product:
            continue
        records.append(
            {
                "manufacturer": manufacturer,
                "product": product,
                "city": str(_read_cell(row, rename["city"])).strip(),
                "address": str(_read_cell(row, rename["address"])).strip(),
                "lat": to_float(_read_cell(row, rename["lat"])),
                "lon": to_float(_read_cell(row, rename["lon"])),
                "distance_km": to_float(_read_cell(row, rename["distance_km"])),
                "transport_time_days": to_float(_read_cell(row, rename["transport_time_days"])),
                "weekly_quantity_units": to_float(_read_cell(row, rename["weekly_quantity_units"])),
                "unit_weight_kg": to_float(_read_cell(row, rename["unit_weight_kg"])),
                "unit_volume_m3": to_float(_read_cell(row, rename["unit_volume_m3"])),
                "manufacturer_reliability": to_float(_read_cell(row, rename["manufacturer_reliability"])),
                "purchase_price_per_unit": to_float(_read_cell(row, rename["purchase_price_per_unit"])),
                "shipping_window": str(_read_cell(row, rename["shipping_window"])).strip(),
            }
        )
    return records


def df_to_carriers(df: pd.DataFrame) -> list[dict[str, Any]]:
    rename = _columns_by_lowercase(df)
    missing = [column for column in CARRIER_FIELDS if column not in rename]
    if missing:
        raise ValueError("В файле перевозчиков не хватает колонок: " + ", ".join(missing))

    records = []
    for _, row in df.iterrows():
        name = str(_read_cell(row, rename["name"])).strip()
        if not name:
            continue
        records.append(
            {
                "name": name,
                "base_city": str(_read_cell(row, rename["base_city"])).strip(),
                "cost_per_km": to_float(_read_cell(row, rename["cost_per_km"])),
                "reliability": to_float(_read_cell(row, rename["reliability"])),
                "tracking": bool_from_str(_read_cell(row, rename["tracking"])),
                "speed_kmh": to_float(_read_cell(row, rename["speed_kmh"]), 80.0),
            }
        )
    return records


def read_tabular_file(file_storage: Any, expected: str) -> list[dict[str, Any]]:
    filename = file_storage.filename.lower()
    content = file_storage.read()

    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(io.BytesIO(content), encoding="cp1251")
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise ValueError("Поддерживаются только CSV, XLSX и XLS.")

    if expected == "factories":
        return df_to_factories(df)
    if expected == "carriers":
        return df_to_carriers(df)
    raise ValueError("Неизвестный тип импортируемых данных.")


def generate_template_xlsx() -> io.BytesIO:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(DEFAULT_FACTORIES)[FACTORY_FIELDS].to_excel(
            writer, index=False, sheet_name="factories"
        )
        pd.DataFrame(DEFAULT_CARRIERS)[CARRIER_FIELDS].to_excel(
            writer, index=False, sheet_name="carriers"
        )
    output.seek(0)
    return output
