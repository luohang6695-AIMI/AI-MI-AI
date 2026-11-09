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


def filter_country(rows: list[dict], country: str | None) -> list[dict]:
    if not country:
        return rows
    return [row for row in rows if row.get("country") == country]


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


def load_market_launch_backlog() -> list[dict]:
    path = ROOT / "data" / "market_launch_backlog.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            row["budget_usd"] = _to_float(raw.get("budget_usd"))
            row["priority"] = int(_to_float(raw.get("priority"), 999))
            rows.append(row)
    return rows


def load_operator_integrations() -> list[dict]:
    path = ROOT / "data" / "operator_integrations.csv"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_operator_workflows() -> list[dict]:
    path = ROOT / "data" / "operator_workflows.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            row["step_order"] = int(_to_float(raw.get("step_order"), 999))
            row["approval_required"] = raw.get("approval_required", "").lower() == "true"
            rows.append(row)
    return rows


def load_growth_campaigns() -> list[dict]:
    path = ROOT / "data" / "growth_campaigns.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            row["total_budget_usd"] = _to_float(raw.get("total_budget_usd"))
            row["ads_pct"] = _to_float(raw.get("ads_pct"))
            row["coins_pct"] = _to_float(raw.get("coins_pct"))
            row["min_live_viewers"] = int(_to_float(raw.get("min_live_viewers")))
            row["target_daily_gmv_usd"] = _to_float(raw.get("target_daily_gmv_usd"))
            rows.append(row)
    return rows


def load_operator_intake(country: str | None) -> list[dict]:
    if country != "MY":
        return []
    path = ROOT / "data" / "malaysia_operator_intake.csv"
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def build_market_launch_plan(backlog: list[dict], cfg: dict) -> list[dict]:
    rules = cfg["market_launch_rules"]
    readiness_fields = rules["readiness_fields"]
    target_countries = set(rules["target_countries"])
    plan = []

    for row in sorted(backlog, key=lambda item: (item["country"], item["priority"])):
        if row["country"] not in target_countries:
            continue

        blockers = [
            field.replace("_status", "")
            for field in readiness_fields
            if row.get(field) != rules["required_status"]
        ]
        over_budget = row["budget_usd"] > rules["max_launch_budget_usd"]
        status = "LAUNCH_NOW" if not blockers and not over_budget else "BLOCKED"

        plan.append({
            "country": row["country"],
            "platform": row["platform"],
            "priority": row["priority"],
            "owner": row["owner"],
            "due_date": row["due_date"],
            "budget_usd": row["budget_usd"],
            "status": status,
            "blockers": blockers + (["budget_approval"] if over_budget else []),
            "next_action": "Publish storefront, start creator seeding, and open daily GMV/ROI loop" if status == "LAUNCH_NOW" else "Clear blockers before launch gate",
        })

    return plan


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


def render_market_launch_report(run_date: str, plan: list[dict]) -> str:
    launchable = [item for item in plan if item["status"] == "LAUNCH_NOW"]
    blocked = [item for item in plan if item["status"] == "BLOCKED"]
    lines = [
        f"# Cross-Border Ecommerce Launch Plan - {run_date}",
        "",
        "## Scope",
        "- Countries: Vietnam, Thailand, Malaysia, Singapore, Brazil, Taiwan",
        "- Launch gate: localization, payment, logistics, compliance, and budget must be ready.",
        "",
        f"## Launch Now ({len(launchable)})",
    ]

    for item in launchable:
        lines.append(
            f"- {item['country']} | {item['platform']} | P{item['priority']} | "
            f"owner={item['owner']} due={item['due_date']} budget=${item['budget_usd']:,.2f} "
            f"-> {item['next_action']}"
        )

    lines.extend(["", f"## Blocked ({len(blocked)})"])
    for item in blocked:
        lines.append(
            f"- {item['country']} | {item['platform']} | P{item['priority']} | "
            f"owner={item['owner']} due={item['due_date']} budget=${item['budget_usd']:,.2f} "
            f"blockers={','.join(item['blockers'])}"
        )

    return "\n".join(lines) + "\n"


def build_operator_execution_queue(
    run_date: str,
    rows: list[dict],
    launch_plan: list[dict],
    integrations: list[dict],
    workflows: list[dict],
    cfg: dict,
) -> list[dict]:
    operator = cfg["operator_rules"]
    daily_target = operator["monthly_min_revenue_usd"] / operator["days_per_month"]
    revenue = sum(r["gmv_usd"] for r in rows)
    gap = max(daily_target - revenue, 0)
    missing_integrations = [i["integration"] for i in integrations if i["status"] != "connected"]
    queue = []

    def add_workflow_items(trigger: str, context: dict) -> None:
        for wf in sorted([w for w in workflows if w["trigger"] == trigger], key=lambda item: item["step_order"]):
            command = wf["command_template"].format(**context)
            queue.append({
                "run_date": run_date,
                "mode": operator["operator_mode"],
                "trigger": trigger,
                "country": context.get("country", ""),
                "platform": context.get("platform", ""),
                "owner": wf["owner"],
                "approval_required": wf["approval_required"],
                "blocked_by_integrations": missing_integrations,
                "command": command,
                "status": "READY_FOR_OPERATOR" if not missing_integrations and not wf["approval_required"] else "NEEDS_SETUP_OR_APPROVAL",
            })

    if gap > 0:
        add_workflow_items("REVENUE_GAP", {
            "gap_usd": f"{gap:.2f}",
            "required_daily_usd": f"{daily_target:.2f}",
        })

    for item in launch_plan:
        context = {
            "country": item["country"],
            "platform": item["platform"],
            "blockers": ",".join(item["blockers"]) if item["blockers"] else "none",
            "budget_usd": f"{item['budget_usd']:.2f}",
            "creator_budget": f"{item['budget_usd'] * 0.25:.2f}",
            "ad_budget": f"{item['budget_usd'] * 0.50:.2f}",
        }
        add_workflow_items(item["status"], context)
        if "budget_approval" in item["blockers"]:
            add_workflow_items("budget_approval", context)

    return queue


def render_operator_report(run_date: str, queue: list[dict], cfg: dict) -> str:
    operator = cfg["operator_rules"]
    ready = [item for item in queue if item["status"] == "READY_FOR_OPERATOR"]
    blocked = [item for item in queue if item["status"] != "READY_FOR_OPERATOR"]
    lines = [
        f"# Autonomous Operator Queue - {run_date}",
        "",
        f"- Monthly minimum revenue target: ${operator['monthly_min_revenue_usd']:,.2f}",
        f"- Required daily run-rate: ${operator['monthly_min_revenue_usd'] / operator['days_per_month']:,.2f}",
        f"- Operator mode: {operator['operator_mode']}",
        "",
        "## Important",
        "- This system does not guarantee revenue; it creates deterministic operating commands and blocks unsafe execution until integrations and approvals exist.",
        "",
        f"## Ready For Operator ({len(ready)})",
    ]

    if not ready:
        lines.append("- No commands are executable until required integrations are connected.")
    for item in ready:
        lines.append(f"- {item['owner']} | {item['country']} | {item['platform']} -> `{item['command']}`")

    lines.extend(["", f"## Needs Setup Or Approval ({len(blocked)})"])
    for item in blocked:
        blockers = ",".join(item["blocked_by_integrations"])
        approval = "approval_required" if item["approval_required"] else "integration_setup_required"
        lines.append(f"- {item['owner']} | {item['country']} | {item['platform']} -> `{item['command']}` | blockers={blockers or approval}")

    return "\n".join(lines) + "\n"


def build_growth_campaign_plan(campaigns: list[dict]) -> list[dict]:
    plan = []
    for campaign in campaigns:
        ads_budget = campaign["total_budget_usd"] * campaign["ads_pct"]
        coins_budget = campaign["total_budget_usd"] * campaign["coins_pct"]
        plan.append({
            "campaign_id": campaign["campaign_id"],
            "country": campaign["country"],
            "platform": campaign["platform"],
            "sku": campaign["sku"],
            "objective": campaign["objective"],
            "owner": campaign["owner"],
            "due_date": campaign["due_date"],
            "status": campaign["status"],
            "target_daily_gmv_usd": campaign["target_daily_gmv_usd"],
            "budget": {
                "total_budget_usd": campaign["total_budget_usd"],
                "shopee_ads_usd": ads_budget,
                "coins_usd": coins_budget,
            },
            "execution_steps": [
                "Confirm probiotic hero SKU margin, stock, claims, and Malaysia compliance before scaling",
                "Set Shopee Product Ads, Shop Ads, and Live Ads using the ads budget",
                "Run Coins only together with live sessions and ads traffic",
                f"Keep core live room concurrent viewers at or above {campaign['min_live_viewers']}",
                "Recruit affiliate hosts and seed product samples before the live push",
                "Update GMV, ad spend, ROI, refund rate, and inventory days in daily_metrics.csv every day",
            ],
            "kill_switches": [
                "Stop scaling if inventory days fall below the warning threshold",
                "Stop or cut budget if ROI falls below the low ROI threshold",
                "Stop claims or creatives that create compliance risk",
            ],
        })
    return plan


def render_growth_campaign_report(run_date: str, plan: list[dict]) -> str:
    lines = [
        f"# Growth Campaign Plan - {run_date}",
        "",
        "## Safety",
        "- Credentials, OTP phone numbers, and personal passwords must stay out of this repository.",
        "- Use platform sub-accounts, API tokens, or a password manager for real execution access.",
        "",
    ]
    for campaign in plan:
        budget = campaign["budget"]
        lines.extend([
            f"## {campaign['campaign_id']}",
            f"- Market: {campaign['country']} / {campaign['platform']}",
            f"- SKU: {campaign['sku']}",
            f"- Owner: {campaign['owner']} due={campaign['due_date']}",
            f"- Target daily GMV: ${campaign['target_daily_gmv_usd']:,.2f}",
            f"- Budget: total=${budget['total_budget_usd']:,.2f}, Shopee Ads=${budget['shopee_ads_usd']:,.2f}, Coins=${budget['coins_usd']:,.2f}",
            "",
            "### Execution Steps",
        ])
        for step in campaign["execution_steps"]:
            lines.append(f"- {step}")
        lines.extend(["", "### Kill Switches"])
        for switch in campaign["kill_switches"]:
            lines.append(f"- {switch}")
        lines.append("")

    return "\n".join(lines)


def render_operator_intake_report(run_date: str, items: list[dict]) -> str:
    lines = [
        f"# Operator Intake Checklist - {run_date}",
        "",
        "你不需要学习后台操作；你只要把这些资料用安全渠道交给我，我来转成系统输入和执行队列。",
        "",
        "## Missing / Needed",
    ]

    needed = [item for item in items if item["status"] != "received"]
    if not needed:
        lines.append("- All required intake items are received.")
    for item in needed:
        lines.append(
            f"- [{item['category']}] {item['item']} | owner={item['owner']} | "
            f"secure_channel={item['secure_channel']} | notes={item['notes']}"
        )

    lines.extend([
        "",
        "## Safety",
        "- Do not send platform passwords or OTP details in chat.",
        "- Use platform sub-accounts, password manager sharing, or revocable API tokens.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--country", help="Optional country code filter, for example MY")
    args = parser.parse_args()
    country = args.country.upper() if args.country else None
    suffix = f"_{country}" if country else ""

    cfg = load_config()
    rows = filter_country(load_metrics(args.date), country)
    if not rows:
        scope = f" and country {country}" if country else ""
        raise SystemExit(f"No metrics found for date {args.date}{scope}")

    actions = apply_rules(rows, cfg)
    cashflow_rows = load_cashflow()
    cashflow_risk = compute_cashflow_risk(cashflow_rows)
    launch_plan = build_market_launch_plan(filter_country(load_market_launch_backlog(), country), cfg)
    operator_queue = build_operator_execution_queue(
        args.date,
        rows,
        launch_plan,
        load_operator_integrations(),
        load_operator_workflows(),
        cfg,
    )
    growth_campaign_plan = build_growth_campaign_plan(filter_country(load_growth_campaigns(), country))
    intake_items = load_operator_intake(country)

    out_json = ROOT / "outputs" / f"actions_{args.date}{suffix}.json"
    out_md = ROOT / "outputs" / f"ceo_report_{args.date}{suffix}.md"
    out_cf = ROOT / "outputs" / f"cashflow_risk_{args.date}{suffix}.json"
    out_launch_json = ROOT / "outputs" / f"market_launch_plan_{args.date}{suffix}.json"
    out_launch_md = ROOT / "outputs" / f"market_launch_plan_{args.date}{suffix}.md"
    out_operator_json = ROOT / "outputs" / f"operator_queue_{args.date}{suffix}.json"
    out_operator_md = ROOT / "outputs" / f"operator_queue_{args.date}{suffix}.md"
    out_growth_json = ROOT / "outputs" / f"growth_campaign_plan_{args.date}{suffix}.json"
    out_growth_md = ROOT / "outputs" / f"growth_campaign_plan_{args.date}{suffix}.md"
    out_intake_md = ROOT / "outputs" / f"operator_intake_{args.date}{suffix}.md"

    out_json.write_text(json.dumps(actions, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(render_ceo_report(args.date, rows, actions, cfg, cashflow_risk), encoding="utf-8")
    out_cf.write_text(json.dumps(cashflow_risk, ensure_ascii=False, indent=2), encoding="utf-8")
    out_launch_json.write_text(json.dumps(launch_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    out_launch_md.write_text(render_market_launch_report(args.date, launch_plan), encoding="utf-8")
    out_operator_json.write_text(json.dumps(operator_queue, ensure_ascii=False, indent=2), encoding="utf-8")
    out_operator_md.write_text(render_operator_report(args.date, operator_queue, cfg), encoding="utf-8")
    out_growth_json.write_text(json.dumps(growth_campaign_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    out_growth_md.write_text(render_growth_campaign_report(args.date, growth_campaign_plan), encoding="utf-8")
    if intake_items:
        out_intake_md.write_text(render_operator_intake_report(args.date, intake_items), encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print(f"Wrote {out_cf}")
    print(f"Wrote {out_launch_json}")
    print(f"Wrote {out_launch_md}")
    print(f"Wrote {out_operator_json}")
    print(f"Wrote {out_operator_md}")
    print(f"Wrote {out_growth_json}")
    print(f"Wrote {out_growth_md}")
    if intake_items:
        print(f"Wrote {out_intake_md}")


if __name__ == "__main__":
    main()
