"""Markdown daily virtual trading report."""

from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths


def _line_items(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    if not rows:
        return ["- none"]
    output = []
    for row in rows:
        parts = [f"{field}={row.get(field)}" for field in fields]
        output.append("- " + ", ".join(parts))
    return output


def generate_daily_report(
    date: str,
    portfolio: dict[str, Any],
    data_quality: dict[str, int],
    macro_signals: list[dict[str, Any]],
    signals: list[dict[str, Any]],
    orders: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    benchmark: dict[str, Any],
    attribution: dict[str, Any],
    evolution: dict[str, Any],
    limitations: list[str],
    paths: ProjectPaths | None = None,
) -> str:
    lines = [
        f"# 虚拟交易日报 {date}",
        "",
        "## 1. 账户概况",
        f"- 现金: {portfolio.get('cash', 0)}",
        f"- 持仓市值: {portfolio.get('market_value', 0)}",
        f"- 总资产: {portfolio.get('total_asset', 0)}",
        f"- 日收益: {portfolio.get('daily_return', 0)}",
        f"- 累计收益: {portfolio.get('cumulative_return', 0)}",
        f"- 最大回撤: {portfolio.get('max_drawdown', 0)}",
        "",
        "## 2. 今日数据质量",
        *[f"- {key}: {value}" for key, value in data_quality.items()],
        "",
        "## 3. 今日宏观信号",
        *_line_items(macro_signals, ["macro_signal_id", "theme", "confidence", "status"]),
        "",
        "## 4. 今日交易信号",
        *_line_items(signals, ["signal_id", "strategy_id", "symbol", "side", "target_weight", "confidence", "status"]),
        "",
        "## 5. 风控检查",
        *_line_items(orders, ["order_id", "symbol", "side", "risk_check", "risk_reason", "status"]),
        "",
        "## 6. 订单与成交",
        *_line_items(trades, ["trade_id", "order_id", "symbol", "side", "filled_quantity", "filled_price", "status"]),
        "",
        "## 7. 当前持仓",
        *_line_items(portfolio.get("positions", []), ["symbol", "quantity", "available_quantity", "avg_cost", "current_price", "market_value", "weight"]),
        "",
        "## 8. Benchmark 对比",
        f"- portfolio return: {benchmark.get('portfolio_return', 0)}",
        *[f"- {key}: {value.get('return')}" for key, value in benchmark.get("benchmarks", {}).items()],
        "",
        "## 9. 收益归因",
        f"- 持仓贡献: {attribution.get('holding_contribution', {})}",
        f"- 策略贡献: {attribution.get('strategy_contribution', {})}",
        f"- benchmark 相对贡献: {attribution.get('benchmark_relative', {})}",
        "",
        "## 10. 自我迭代结果",
        f"- signal scorecard count: {len(evolution.get('signal_scorecard', {}).get('items', []))}",
        f"- mistake count: {len(evolution.get('mistakes', []))}",
        f"- experiment queue count: {evolution.get('experiment_queue_count', 0)}",
        f"- promotion: {evolution.get('promotion_recommendation', {})}",
        "",
        "## 11. 明日观察",
        "- 持仓风险: observe position weights and data quality.",
        "- 待验证信号: review open scorecard items.",
        "- shadow 策略观察: compare shadow results without touching main portfolio.",
        "",
        "## 12. 限制与异常",
        *([f"- {item}" for item in limitations] if limitations else ["- none"]),
        "",
    ]
    markdown = "\n".join(lines)
    paths = paths or project_paths()
    path = paths.daily_report(date)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        previous = path.read_text(encoding="utf-8")
        if previous != markdown:
            archive_dir = path.parent / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
            archive_path = archive_dir / f"{path.stem}-{stamp}-{uuid4().hex[:8]}.md"
            archive_path.write_text(previous, encoding="utf-8")
    path.write_text(markdown, encoding="utf-8")
    return markdown
