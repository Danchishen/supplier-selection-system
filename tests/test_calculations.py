from supplier_selection.calculations import build_ranked_results
from supplier_selection.data import DEFAULT_CARRIERS, DEFAULT_CUSTOMER, DEFAULT_FACTORIES, DEFAULT_GLOBALS, DEFAULT_WEIGHT_CONFIG


def test_default_scenario_returns_plan_for_each_product():
    results = build_ranked_results(
        DEFAULT_CUSTOMER,
        DEFAULT_FACTORIES,
        DEFAULT_CARRIERS,
        DEFAULT_GLOBALS,
        DEFAULT_WEIGHT_CONFIG["method"],
        DEFAULT_WEIGHT_CONFIG,
    )

    assert len(results["best_plan"]) == 3
    assert results["summary"]["total_cost_rub"] > 0
    assert len(results["weights"]) == 4
    assert abs(sum(results["weights"]) - 1.0) < 1e-6
