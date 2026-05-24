import argparse
import csv
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    with open(ROOT / "config" / "rules.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _to_float(v: str, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _to_row(raw: dict) -> dict:
    return {
        "date": raw.get("date", ""),
        "country": raw.get("country", ""),
        "platform": raw.get("platform", ""),
        "sku": raw.get("sku", ""),
        "roi": _to_float(raw.get("roi")),
        "spend_usd": _to_float(raw.get("spend_usd")),
        "gmv_usd": _to_float(raw.get("gmv_usd")),
        "inventory_days": _to_float(raw.get("inventory_days")),
        "refund_rate": _to_float(raw.get("refund_rate")),
        "cvr": _to_float(raw.get("cvr")),
        "owner": raw.get("owner", "UNASSIGNED"),
        "due_date": raw.get("due_date", ""),
        "amount_usd": _to_float(raw.get("amount_usd")),
    }


def load_metrics(run_date: str) -> list[dict]:
    rows = []
    with open(ROOT / "data" / "daily_metrics.csv", "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            if raw.get("date") == run_date:
                rows.append(_to_row(raw))
    return rows


def load_cashflow() -> list[dict]:
    path = ROOT / "data" / "cashflow_13_weeks.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            inflow = _to_float(raw.get("inflow_usd"))
            outflow = _to_float(raw.get("outflow_usd"))
            rows.append({
                "week": raw.get("week", ""),
                "inflow_usd": inflow,
                "outflow_usd": outflow,
                "net_usd": inflow - outflow,
            })
    return rows


def validate_assignment(r: dict) -> list[dict]:
    issues = []
    if not r["owner"] or r["owner"] == "UNASSIGNED":
        issues.append({"type": "governance_alert", "severity": "critical", "sku": r["sku"], "action": "BLOCK_UNASSIGNED_TASK", "reason": "No owner assigned"})
    if not r["due_date"]:
        issues.append({"type": "governance_alert", "severity": "critical", "sku": r["sku"], "action": "BLOCK_UNSCHEDULED_TASK", "reason": "No due_date set"})
    if r["amount_usd"] <= 0:
        issues.append({"type": "governance_alert", "severity": "warning", "sku": r["sku"], "action": "FLAG_NO_BUDGET", "reason": "No amount_usd set"})
    return issues


def apply_rules(rows: list[dict], cfg: dict) -> list[dict]:
    actions = []
    ad = cfg["ad_rules"]
    inv = cfg["inventory_rules"]
    gov = cfg["governance_rules"]

    for r in rows:
        actions.extend(validate_assignment(r))

        if r["amount_usd"] >= gov["approval_threshold_usd"]:
            actions.append({"type": "approval_gate", "severity": "high", "country": r["country"], "platform": r["platform"], "sku": r["sku"], "owner": r["owner"], "due_date": r["due_date"], "amount_usd": r["amount_usd"], "action": "REQUIRE_24H_COOLDOWN_AND_CHALLENGER_REVIEW", "reason": f"Amount ${r['amount_usd']:.2f} exceeds ${gov['approval_threshold_usd']}"})

        if r["roi"] < ad["low_roi_threshold"]:
            actions.append({"type": "ad_budget_adjustment", "severity": "high", "country": r["country"], "platform": r["platform"], "sku": r["sku"], "owner": r["owner"], "due_date": r["due_date"], "amount_usd": r["amount_usd"], "action": f"CUT_BUDGET_{ad['low_roi_budget_cut_pct']}%", "reason": f"ROI {r['roi']} below {ad['low_roi_threshold']}"})
        elif r["roi"] > ad["high_roi_threshold"] and r["inventory_days"] >= ad["min_inventory_days_for_scale"]:
            actions.append({"type": "ad_budget_adjustment", "severity": "medium", "country": r["country"], "platform": r["platform"], "sku": r["sku"], "owner": r["owner"], "due_date": r["due_date"], "amount_usd": r["amount_usd"], "action": f"RAISE_BUDGET_{ad['high_roi_budget_raise_pct']}%", "reason": f"ROI {r['roi']} above {ad['high_roi_threshold']} with healthy stock"})

        if r["inventory_days"] < inv["critical_days"]:
            actions.append({"type": "inventory_alert", "severity": "critical", "country": r["country"], "sku": r["sku"], "owner": r["owner"], "due_date": r["due_date"], "amount_usd": r["amount_usd"], "action": "EMERGENCY_REPLENISH_AND_DOWNSCALE_ADS", "reason": f"Inventory days {r['inventory_days']} below critical {inv['critical_days']}"})
        elif r["inventory_days"] < inv["warning_days"]:
            actions.append({"type": "inventory_alert", "severity": "warning", "country": r["country"], "sku": r["sku"], "owner": r["owner"], "due_date": r["due_date"], "amount_usd": r["amount_usd"], "action": "REPLENISHMENT_WARNING", "reason": f"Inventory days {r['inventory_days']} below warning {inv['warning_days']}"})

    return actions


def compute_cashflow_risk(cashflow_rows: list[dict]) -> dict:
    rolling = 0.0
    min_point = None
    min_week = ""
    for r in cashflow_rows:
        rolling += r["net_usd"]
        if min_point is None or rolling < min_point:
            min_point = rolling
            min_week = r["week"]
    return {"lowest_cash_point_usd": min_point or 0.0, "lowest_week": min_week}


def render_ceo_report(run_date: str, rows: list[dict], actions: list[dict], cfg: dict, cashflow_risk: dict) -> str:
    revenue = sum(r["gmv_usd"] for r in rows)
    spend = sum(r["spend_usd"] for r in rows)
    roi = (revenue / spend) if spend else 0
    target = cfg["targets"]["revenue_usd_daily"]
    attain = (revenue / target) * 100 if target else 0

    lines = [
        f"# CEO Daily Report - {run_date}",
        "",
        f"- Revenue (GMV): ${revenue:,.2f}",
        f"- Ad Spend: ${spend:,.2f}",
        f"- Blended ROI: {roi:.2f}",
        f"- Target Attainment: {attain:.2f}% (target ${target:,.0f})",
        f"- 13-week lowest cash point: ${cashflow_risk['lowest_cash_point_usd']:,.2f} ({cashflow_risk['lowest_week']})",
        "",
        "## Auto Actions (Owner / Due Date / Amount)",
    ]

    if not actions:
        lines.append("- No actions triggered.")
    else:
        for a in actions[: cfg["report"]["top_n_risks"]]:
            owner = a.get("owner", "N/A")
            due = a.get("due_date", "N/A")
            amt = a.get("amount_usd", 0)
            lines.append(f"- [{a['severity'].upper()}] {a['type']} | {a.get('country','')} | {a.get('platform','')} | {a['sku']} -> {a['action']} | owner={owner} due={due} amount=${amt:,.2f} ({a['reason']})")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().isoformat())
    args = parser.parse_args()

    cfg = load_config()
    rows = load_metrics(args.date)
    if not rows:
        raise SystemExit(f"No metrics found for date {args.date}")

    actions = apply_rules(rows, cfg)
    cashflow_rows = load_cashflow()
    cashflow_risk = compute_cashflow_risk(cashflow_rows)

    out_json = ROOT / "outputs" / f"actions_{args.date}.json"
    out_md = ROOT / "outputs" / f"ceo_report_{args.date}.md"
    out_cf = ROOT / "outputs" / f"cashflow_risk_{args.date}.json"

    out_json.write_text(json.dumps(actions, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(render_ceo_report(args.date, rows, actions, cfg, cashflow_risk), encoding="utf-8")
    out_cf.write_text(json.dumps(cashflow_risk, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_cf}")


if __name__ == "__main__":
    main()
